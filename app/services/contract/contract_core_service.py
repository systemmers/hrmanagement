"""
Contract Core Service

계약 조회 관련 비즈니스 로직을 처리합니다.
- 개인/법인 계약 목록 조회
- 계약 상세 조회
- 계약 검색
- 계약 대상 조회
"""
from typing import Dict, Optional, List, Any

from ...constants.session_keys import AccountType
from ...constants.status import ContractStatus
from ...models.user import User
from ...models.employee import Employee
from ...models.person_contract import PersonCorporateContract


class ContractCoreService:
    """계약 조회 서비스"""

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        from ...extensions import person_contract_repo
        return person_contract_repo

    # ========================================
    # 개인 계정용 메서드
    # ========================================

    def get_personal_contracts(self, user_id: int) -> List[Dict]:
        """개인 계약 목록 조회"""
        return self.contract_repo.get_by_person_user_id(user_id)

    def get_personal_pending_contracts(self, user_id: int) -> List[Dict]:
        """개인 대기 중인 계약 조회"""
        return self.contract_repo.get_pending_contracts_by_person(user_id)

    def get_personal_statistics(self, user_id: int) -> Dict:
        """개인 계약 통계"""
        return self.contract_repo.get_statistics_by_person(user_id)

    # ========================================
    # 법인 계정용 메서드
    # ========================================

    def get_company_contracts(self, company_id: int) -> List[Dict]:
        """법인 계약 목록 조회"""
        return self.contract_repo.get_by_company_id(company_id)

    def get_company_pending_contracts(self, company_id: int) -> List[Dict]:
        """법인 대기 중인 계약 조회"""
        return self.contract_repo.get_pending_contracts_by_company(company_id)

    def get_company_statistics(self, company_id: int) -> Dict:
        """법인 계약 통계"""
        return self.contract_repo.get_statistics_by_company(company_id)

    def search_contracts(self, company_id: int, status: str = None,
                         contract_type: str = None, search_term: str = None) -> List[Dict]:
        """계약 검색 (법인용)"""
        return self.contract_repo.search_contracts(
            company_id=company_id,
            status=status,
            contract_type=contract_type,
            search_term=search_term
        )

    def get_contract_eligible_targets(self, company_id: int) -> Dict[str, List[Dict]]:
        """계약 요청 가능한 대상 목록 조회

        Returns:
            {
                'personal_accounts': [개인계정 목록],
                'employee_accounts': [직원계정 목록 (pending_contract 상태)]
            }
        """
        result = {
            'personal_accounts': [],
            'employee_accounts': []
        }

        # 1. 개인계정 중 해당 법인과 계약 미체결 (또는 거절/종료된 계약만 있는 경우)
        personal_users = User.query.filter(
            User.account_type == AccountType.PERSONAL,
            User.is_active == True
        ).all()

        for user in personal_users:
            existing_contract = self.contract_repo.get_contract_between(
                person_user_id=user.id,
                company_id=company_id
            )
            if not existing_contract or existing_contract.get('status') in [ContractStatus.REJECTED, ContractStatus.TERMINATED]:
                result['personal_accounts'].append({
                    'user_id': user.id,
                    'name': user.username,
                    'email': user.email,
                    'account_type': 'personal'
                })

        # 2. 직원계정 중 계약 미체결 상태 (pending_info 또는 pending_contract)
        pending_employees = Employee.query.filter(
            Employee.company_id == company_id,
            Employee.status.in_(['pending_info', 'pending_contract'])
        ).all()

        for emp in pending_employees:
            emp_user = User.query.filter(
                User.employee_id == emp.id
            ).first()

            if emp_user:
                existing_contract = self.contract_repo.get_contract_between(
                    person_user_id=emp_user.id,
                    company_id=company_id
                )
                if not existing_contract or existing_contract.get('status') in [ContractStatus.REJECTED, ContractStatus.TERMINATED]:
                    status_label = '프로필 미완성' if emp.status == 'pending_info' else '계약 대기'
                    result['employee_accounts'].append({
                        'user_id': emp_user.id,
                        'employee_id': emp.id,
                        'name': emp.name,
                        'email': emp_user.email,
                        'department': emp.department,
                        'position': emp.position,
                        'account_type': 'employee_sub',
                        'status': emp.status,
                        'status_label': status_label
                    })

        return result

    # ========================================
    # 계약 상세 조회
    # ========================================

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        """계약 상세 조회 (Dict 반환)"""
        model = self.contract_repo.find_by_id(contract_id)
        return model.to_dict() if model else None

    def get_contract_model_by_id(self, contract_id: int):
        """계약 모델 조회 (ORM 객체)"""
        return self.contract_repo.find_by_id(contract_id)

    def find_contract_with_history(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        """계약 이력 조회 - 수정불가 필터용

        Phase 28: termination_requested 추가
        계약 이력이 있는 직원은 필드 수정 불가
        """
        if not employee_number or not company_id:
            return None

        return PersonCorporateContract.query.filter(
            PersonCorporateContract.employee_number == employee_number,
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_([
                PersonCorporateContract.STATUS_APPROVED,
                PersonCorporateContract.STATUS_TERMINATION_REQUESTED,
                PersonCorporateContract.STATUS_TERMINATED,
                PersonCorporateContract.STATUS_EXPIRED
            ])
        ).first()

    def find_approved_contract(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        """승인된 계약 조회"""
        return self.contract_repo.find_approved_contract_by_employee_number(
            employee_number, company_id
        )

    def get_employee_contract_status(
        self,
        employee_user_id: int,
        company_id: int
    ) -> Optional[str]:
        """직원의 계약 상태 조회

        Returns:
            'none' | 'pending' | 'approved' | 'rejected' | 'terminated'
        """
        contract = self.contract_repo.get_contract_between(
            person_user_id=employee_user_id,
            company_id=company_id
        )
        if not contract:
            return 'none'
        return contract.get('status', 'none')


# 싱글톤 인스턴스
contract_core_service = ContractCoreService()
