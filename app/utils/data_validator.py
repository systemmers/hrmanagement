"""
Data Integrity Validator

Phase 23: 데이터 정합성 검증 유틸리티
PersonCorporateContract, Employee, User 간 정합성 검증
"""
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from datetime import datetime

from app.database import db
from app.models.person_contract import PersonCorporateContract
from app.models.employee import Employee
from app.models.user import User


@dataclass
class IntegrityIssue:
    """데이터 정합성 이슈"""
    issue_type: str
    severity: str  # 'critical', 'warning', 'info'
    entity_type: str
    entity_id: int
    description: str
    current_value: Optional[str] = None
    expected_value: Optional[str] = None
    fix_action: Optional[str] = None


class DataIntegrityValidator:
    """데이터 정합성 검증기

    검증 항목:
    1. pending_info + approved: 계약 승인 시 Employee.status = 'active' 필요
    2. resigned + approved: 퇴사 시 PCC.status = 'terminated' 필요
    3. resigned + 퇴사일 없음: resignation_date 필수
    4. PCC.employee_number NULL: approved 계약은 employee_number 필요
    5. approved + Employee 없음: 승인된 계약은 Employee 연결 필요
    6. User.employee_id NULL: employee_sub 계정은 employee_id 필요
    """

    def __init__(self, company_id: Optional[int] = None):
        self.company_id = company_id
        self.issues: List[IntegrityIssue] = []

    def validate_all(self) -> List[IntegrityIssue]:
        """전체 검증 실행"""
        self.issues = []

        self._check_pending_info_approved()
        self._check_resigned_approved()
        self._check_resigned_no_date()
        self._check_pcc_employee_number_null()
        self._check_approved_no_employee()
        self._check_user_employee_id_null()
        self._check_employee_company_id_null()
        self._check_pcc_approved_at_null()

        return self.issues

    def get_summary(self) -> Dict:
        """검증 결과 요약"""
        if not self.issues:
            self.validate_all()

        summary = {
            'total_issues': len(self.issues),
            'critical': len([i for i in self.issues if i.severity == 'critical']),
            'warning': len([i for i in self.issues if i.severity == 'warning']),
            'info': len([i for i in self.issues if i.severity == 'info']),
            'by_type': {}
        }

        for issue in self.issues:
            if issue.issue_type not in summary['by_type']:
                summary['by_type'][issue.issue_type] = 0
            summary['by_type'][issue.issue_type] += 1

        return summary

    def _check_pending_info_approved(self):
        """pending_info + approved 조합 검증

        규칙: 계약 승인(approved) 시 Employee.status는 'active' 이어야 함
        """
        query = db.session.query(
            PersonCorporateContract, Employee
        ).join(
            Employee,
            PersonCorporateContract.employee_number == Employee.employee_number
        ).filter(
            PersonCorporateContract.status == 'approved',
            Employee.status == 'pending_info'
        )

        if self.company_id:
            query = query.filter(PersonCorporateContract.company_id == self.company_id)

        for contract, employee in query.all():
            self.issues.append(IntegrityIssue(
                issue_type='pending_info_approved',
                severity='critical',
                entity_type='Employee',
                entity_id=employee.id,
                description=f'{employee.name}: 계약 승인됨(PCC#{contract.id})이나 Employee.status가 pending_info',
                current_value='pending_info',
                expected_value='active',
                fix_action=f"UPDATE employees SET status='active' WHERE id={employee.id}"
            ))

    def _check_resigned_approved(self):
        """resigned + approved 조합 검증

        규칙: 퇴사(resigned)된 직원의 계약은 terminated 이어야 함
        """
        query = db.session.query(
            PersonCorporateContract, Employee
        ).join(
            Employee,
            PersonCorporateContract.employee_number == Employee.employee_number
        ).filter(
            PersonCorporateContract.status == 'approved',
            Employee.status == 'resigned'
        )

        if self.company_id:
            query = query.filter(PersonCorporateContract.company_id == self.company_id)

        for contract, employee in query.all():
            self.issues.append(IntegrityIssue(
                issue_type='resigned_approved',
                severity='critical',
                entity_type='PersonCorporateContract',
                entity_id=contract.id,
                description=f'PCC#{contract.id}: 퇴사 직원({employee.name})이나 계약 상태가 approved',
                current_value='approved',
                expected_value='terminated',
                fix_action=f"UPDATE person_corporate_contracts SET status='terminated' WHERE id={contract.id}"
            ))

    def _check_resigned_no_date(self):
        """resigned + 퇴사일 없음 검증

        규칙: resigned 상태는 resignation_date 필수
        """
        query = Employee.query.filter(
            Employee.status == 'resigned',
            Employee.resignation_date.is_(None)
        )

        if self.company_id:
            query = query.filter(Employee.company_id == self.company_id)

        for employee in query.all():
            self.issues.append(IntegrityIssue(
                issue_type='resigned_no_date',
                severity='warning',
                entity_type='Employee',
                entity_id=employee.id,
                description=f'{employee.name}: resigned 상태이나 resignation_date 없음',
                current_value='NULL',
                expected_value='퇴사일',
                fix_action=f"UPDATE employees SET resignation_date=CURRENT_DATE WHERE id={employee.id}"
            ))

    def _check_pcc_employee_number_null(self):
        """PCC.employee_number NULL 검증

        규칙: approved 계약은 employee_number 필수
        """
        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == 'approved',
            PersonCorporateContract.employee_number.is_(None)
        )

        if self.company_id:
            query = query.filter(PersonCorporateContract.company_id == self.company_id)

        for contract in query.all():
            user = User.query.get(contract.person_user_id)
            user_email = user.email if user else 'Unknown'

            self.issues.append(IntegrityIssue(
                issue_type='pcc_employee_number_null',
                severity='critical',
                entity_type='PersonCorporateContract',
                entity_id=contract.id,
                description=f'PCC#{contract.id} ({user_email}): approved 상태이나 employee_number 없음',
                current_value='NULL',
                expected_value='employee_number 동기화 필요',
                fix_action='Employee 연결 후 employee_number 동기화 필요'
            ))

    def _check_approved_no_employee(self):
        """approved + Employee 없음 검증

        규칙: approved 계약은 Employee와 연결되어야 함
        (employee_number가 있지만 Employee가 없는 경우)
        """
        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == 'approved',
            PersonCorporateContract.employee_number.isnot(None)
        )

        if self.company_id:
            query = query.filter(PersonCorporateContract.company_id == self.company_id)

        for contract in query.all():
            employee = Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()

            if not employee:
                user = User.query.get(contract.person_user_id)
                user_email = user.email if user else 'Unknown'

                self.issues.append(IntegrityIssue(
                    issue_type='approved_no_employee',
                    severity='critical',
                    entity_type='PersonCorporateContract',
                    entity_id=contract.id,
                    description=f'PCC#{contract.id} ({user_email}): employee_number={contract.employee_number}이나 Employee 없음',
                    current_value=contract.employee_number,
                    expected_value='Employee 레코드 필요',
                    fix_action='Employee 생성 필요'
                ))

    def _check_user_employee_id_null(self):
        """User.employee_id NULL 검증 (employee_sub 계정)

        규칙: employee_sub 계정은 Employee와 연결되어야 함
        """
        query = User.query.filter(
            User.account_type == 'employee_sub',
            User.employee_id.is_(None)
        )

        if self.company_id:
            query = query.filter(User.company_id == self.company_id)

        for user in query.all():
            # approved 계약이 있는지 확인
            contract = PersonCorporateContract.query.filter_by(
                person_user_id=user.id,
                status='approved'
            ).first()

            if contract:
                self.issues.append(IntegrityIssue(
                    issue_type='user_employee_id_null',
                    severity='critical',
                    entity_type='User',
                    entity_id=user.id,
                    description=f'User#{user.id} ({user.email}): approved 계약(PCC#{contract.id})이 있으나 employee_id 없음',
                    current_value='NULL',
                    expected_value='Employee 연결 필요',
                    fix_action='Employee 생성/연결 후 User.employee_id 설정 필요'
                ))

    def _check_employee_company_id_null(self):
        """Employee.company_id NULL 검증

        규칙: approved 계약이 있는 Employee는 company_id 필수
        """
        # approved 계약이 있는 employee_number 조회
        approved_emp_numbers = db.session.query(
            PersonCorporateContract.employee_number
        ).filter(
            PersonCorporateContract.status == 'approved',
            PersonCorporateContract.employee_number.isnot(None)
        )

        if self.company_id:
            approved_emp_numbers = approved_emp_numbers.filter(
                PersonCorporateContract.company_id == self.company_id
            )

        approved_emp_numbers = [x[0] for x in approved_emp_numbers.all()]

        # 해당 Employee 중 company_id가 NULL인 건 조회
        employees = Employee.query.filter(
            Employee.employee_number.in_(approved_emp_numbers),
            Employee.company_id.is_(None)
        ).all()

        for employee in employees:
            self.issues.append(IntegrityIssue(
                issue_type='employee_company_id_null',
                severity='critical',
                entity_type='Employee',
                entity_id=employee.id,
                description=f'{employee.name} ({employee.employee_number}): approved 계약이 있으나 company_id 없음',
                current_value='NULL',
                expected_value='company_id 설정 필요',
                fix_action=f'UPDATE employees SET company_id=? WHERE id={employee.id}'
            ))

    def _check_pcc_approved_at_null(self):
        """PCC.approved_at NULL 검증

        규칙: status='approved'인 계약은 approved_at 필수
        """
        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == 'approved',
            PersonCorporateContract.approved_at.is_(None)
        )

        if self.company_id:
            query = query.filter(PersonCorporateContract.company_id == self.company_id)

        for contract in query.all():
            user = User.query.get(contract.person_user_id)
            user_email = user.email if user else 'Unknown'

            self.issues.append(IntegrityIssue(
                issue_type='pcc_approved_at_null',
                severity='warning',
                entity_type='PersonCorporateContract',
                entity_id=contract.id,
                description=f'PCC#{contract.id} ({user_email}): approved 상태이나 approved_at 없음',
                current_value='NULL',
                expected_value='승인 일시',
                fix_action=f'UPDATE person_corporate_contracts SET approved_at=NOW() WHERE id={contract.id}'
            ))

    def auto_fix(self, dry_run: bool = True) -> Dict:
        """자동 수정 (dry_run=True: 미리보기만)

        Args:
            dry_run: True면 실제 수정 없이 수정 예정 내역만 반환

        Returns:
            수정 결과 (fixes, errors)
        """
        if not self.issues:
            self.validate_all()

        fixes = []
        errors = []

        for issue in self.issues:
            try:
                if issue.issue_type == 'pending_info_approved':
                    if not dry_run:
                        employee = db.session.get(Employee, issue.entity_id)
                        if employee:
                            employee.status = 'active'
                    fixes.append({
                        'issue': issue.issue_type,
                        'entity': f'{issue.entity_type}#{issue.entity_id}',
                        'action': 'status → active'
                    })

                elif issue.issue_type == 'resigned_approved':
                    if not dry_run:
                        contract = db.session.get(PersonCorporateContract, issue.entity_id)
                        if contract:
                            contract.status = 'terminated'
                            contract.terminated_at = datetime.utcnow()
                    fixes.append({
                        'issue': issue.issue_type,
                        'entity': f'{issue.entity_type}#{issue.entity_id}',
                        'action': 'status → terminated'
                    })

                elif issue.issue_type == 'resigned_no_date':
                    if not dry_run:
                        from datetime import date
                        employee = db.session.get(Employee, issue.entity_id)
                        if employee:
                            employee.resignation_date = date.today()
                    fixes.append({
                        'issue': issue.issue_type,
                        'entity': f'{issue.entity_type}#{issue.entity_id}',
                        'action': 'resignation_date → today'
                    })

                elif issue.issue_type == 'pcc_approved_at_null':
                    if not dry_run:
                        contract = db.session.get(PersonCorporateContract, issue.entity_id)
                        if contract:
                            contract.approved_at = datetime.utcnow()
                    fixes.append({
                        'issue': issue.issue_type,
                        'entity': f'{issue.entity_type}#{issue.entity_id}',
                        'action': 'approved_at → NOW()'
                    })

                # pcc_employee_number_null, approved_no_employee, user_employee_id_null, employee_company_id_null은
                # 자동 수정 불가 (데이터 생성/회사 정보 필요)
                elif issue.issue_type in ['pcc_employee_number_null', 'approved_no_employee', 'user_employee_id_null', 'employee_company_id_null']:
                    errors.append({
                        'issue': issue.issue_type,
                        'entity': f'{issue.entity_type}#{issue.entity_id}',
                        'reason': '수동 처리 필요 (데이터 생성/연결)'
                    })

            except Exception as e:
                errors.append({
                    'issue': issue.issue_type,
                    'entity': f'{issue.entity_type}#{issue.entity_id}',
                    'reason': str(e)
                })

        if not dry_run:
            db.session.commit()

        return {
            'dry_run': dry_run,
            'total_fixes': len(fixes),
            'total_errors': len(errors),
            'fixes': fixes,
            'errors': errors
        }


# 싱글톤 인스턴스 팩토리
def get_validator(company_id: Optional[int] = None) -> DataIntegrityValidator:
    """검증기 인스턴스 생성

    Args:
        company_id: 특정 회사로 제한 (없으면 전체)

    Returns:
        DataIntegrityValidator 인스턴스
    """
    return DataIntegrityValidator(company_id)
