"""
Employee Core Service

직원 기본 CRUD 및 멀티테넌시 접근 제어를 담당합니다.
- 직원 생성/조회/수정/삭제
- 멀티테넌시 접근 권한 확인
- 폼 데이터 처리
- 통계/검색

Phase 3: EmployeeService 분리 - Core Service
Phase 28: RRN 파싱/자동입력, 신규 필드 추가, blood_type/religion 삭제
"""
from typing import Any, Dict, List, Optional, Tuple

from app.database import db
from app.models import Employee
from app.utils.transaction import atomic_transaction
from app.utils.tenant import get_current_organization_id
from app.constants.status import EmployeeStatus
from app.utils.rrn_parser import RRNParser


class EmployeeCoreService:
    """직원 기본 CRUD 서비스"""

    # ========================================
    # Repository Property (지연 초기화)
    # ========================================

    @property
    def employee_repo(self):
        """지연 초기화된 직원 Repository"""
        from app.extensions import employee_repo
        return employee_repo

    # ========================================
    # 멀티테넌시 접근 제어
    # ========================================

    def get_current_org_id(self) -> Optional[int]:
        """현재 조직 ID 반환"""
        return get_current_organization_id()

    def verify_access(self, employee_id: int) -> bool:
        """현재 회사가 해당 직원에 접근 가능한지 확인"""
        org_id = self.get_current_org_id()
        if not org_id:
            return False
        return self.employee_repo.verify_ownership(employee_id, org_id)

    def verify_ownership(self, employee_id: int, org_id: int) -> bool:
        """직원 소유권 확인"""
        return self.employee_repo.verify_ownership(employee_id, org_id)

    # ========================================
    # 직원 조회
    # ========================================

    def get_employee(self, employee_id: int) -> Optional[Dict]:
        """직원 조회 (접근 권한 확인 포함, Dict 반환)"""
        if not self.verify_access(employee_id):
            return None
        model = self.employee_repo.find_by_id(employee_id)
        return model.to_dict() if model else None

    def _get_employee_model(self, employee_id: int) -> Optional[Employee]:
        """내부용: Model이 필요한 경우 (수정/삭제 작업용)"""
        return self.employee_repo.find_by_id(employee_id)

    def get_employees_by_org(self, org_id: int = None) -> List[Employee]:
        """조직별 직원 목록 조회"""
        org_id = org_id or self.get_current_org_id()
        if not org_id:
            return []
        return self.employee_repo.get_by_company_id(org_id)

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict]:
        """직원 ID로 조회 (Dict 반환)"""
        model = self.employee_repo.find_by_id(employee_id)
        return model.to_dict() if model else None

    def get_employee_model_by_id(self, employee_id: int) -> Optional[Employee]:
        """직원 ID로 모델 조회 (템플릿 렌더링용)"""
        return self.employee_repo.find_by_id(employee_id)

    def filter_employees(self, **kwargs) -> List[Dict]:
        """직원 필터링 조회"""
        return self.employee_repo.filter_employees(**kwargs)

    def get_all_employees(self, organization_id: int = None) -> List[Dict]:
        """전체 직원 조회"""
        models = self.employee_repo.find_all(organization_id=organization_id)
        return [m.to_dict() for m in models]

    # ========================================
    # 직원 CRUD (직접 호출 - Blueprint용)
    # ========================================

    def create_employee_direct(self, employee_data: Dict) -> Dict:
        """직원 생성 (Dict 데이터로 직접 생성)"""
        return self.employee_repo.create(employee_data)

    def update_employee_direct(self, employee_id: int, employee: Any) -> Optional[Any]:
        """직원 수정 (모델 객체로 직접 수정)"""
        return self.employee_repo.update(employee_id, employee)

    def update_employee_partial(self, employee_id: int, fields: Dict) -> Optional[Any]:
        """직원 부분 수정"""
        return self.employee_repo.update_partial(employee_id, fields)

    def delete_employee_direct(self, employee_id: int) -> bool:
        """직원 삭제 (직접 호출)"""
        return self.employee_repo.delete(employee_id)

    # ========================================
    # 직원 CRUD (트랜잭션 포함)
    # ========================================

    def create_employee(self, form_data: Dict,
                        relation_updater_callback=None) -> Tuple[bool, Optional[Employee], Optional[str]]:
        """직원 생성

        Args:
            form_data: 폼 데이터
            relation_updater_callback: 관계형 데이터 업데이트 콜백 (employee_id, form_data)

        Returns:
            Tuple[성공여부, Employee객체, 에러메시지]
        """
        try:
            org_id = self.get_current_org_id()
            if not org_id:
                return False, None, "조직 정보를 찾을 수 없습니다."

            with atomic_transaction():
                employee = self._extract_employee_from_form(form_data)
                employee.company_id = org_id

                self.employee_repo.create(employee, commit=False)
                db.session.flush()

                # 관계형 데이터 업데이트 (콜백)
                if relation_updater_callback:
                    relation_updater_callback(employee.id, form_data)

            return True, employee, None

        except Exception as e:
            return False, None, str(e)

    def update_employee(self, employee_id: int, form_data: Dict,
                        relation_updater_callback=None) -> Tuple[bool, Optional[str]]:
        """직원 정보 수정

        Args:
            employee_id: 직원 ID
            form_data: 폼 데이터
            relation_updater_callback: 관계형 데이터 업데이트 콜백 (employee_id, form_data)

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                # 기본 필드 업데이트
                updated_employee = self._extract_employee_from_form(form_data, employee_id)
                self.employee_repo.update(employee, updated_employee, commit=False)

                # 관계형 데이터 업데이트 (콜백)
                if relation_updater_callback:
                    relation_updater_callback(employee_id, form_data)

            return True, None

        except Exception as e:
            return False, str(e)

    def delete_employee(self, employee_id: int) -> Tuple[bool, Optional[str]]:
        """직원 삭제

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                self.employee_repo.delete(employee, commit=False)

            return True, None

        except Exception as e:
            return False, str(e)

    # ========================================
    # 기본 정보만 수정 (Employee 역할용)
    # ========================================

    def update_basic_info(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """기본 정보만 수정 (연락처, 주소 등)

        Phase 28: RRN 입력 시 birth_date, age, gender 자동 입력
        """
        try:
            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                basic_fields = self._extract_basic_fields(form_data)

                # Phase 28: RRN 자동 입력 처리
                basic_fields = self._apply_rrn_auto_fields(basic_fields)

                for key, value in basic_fields.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)

            return True, None

        except Exception as e:
            return False, str(e)

    # ========================================
    # 통계/검색용 메서드
    # ========================================

    def get_statistics(self, organization_id: int = None) -> Dict:
        """직원 통계 조회"""
        return self.employee_repo.get_statistics(organization_id=organization_id)

    def get_department_statistics(self, organization_id: int = None) -> List[Dict]:
        """부서별 통계 조회"""
        return self.employee_repo.get_department_statistics(organization_id=organization_id)

    def get_recent_employees(self, organization_id: int = None, limit: int = 5) -> List[Dict]:
        """최근 입사 직원 조회"""
        return self.employee_repo.get_recent_employees(limit=limit, organization_id=organization_id)

    def search_employees(self, query: str, organization_id: int = None) -> List[Dict]:
        """직원 검색"""
        return self.employee_repo.search(query, organization_id=organization_id)

    def get_employees_by_ids(self, employee_ids: List[int]) -> List[Dict]:
        """여러 직원 ID로 조회 (벌크)

        Args:
            employee_ids: 직원 ID 목록

        Returns:
            직원 Dict 목록
        """
        if not employee_ids:
            return []
        employees = self.employee_repo.find_by_ids(employee_ids)
        return [emp.to_dict() for emp in employees]

    def get_employees_with_contracts(
        self,
        employees: List[Dict],
        company_id: int
    ) -> List[Dict]:
        """직원 목록에 계약 정보 추가 (레이어 분리용)

        Blueprint의 for 루프 데이터 변환 로직을 Service로 이동.
        퇴사 직원 제외, 활성 계약이 있는 직원만 반환.

        Args:
            employees: 직원 Dict 목록
            company_id: 법인 ID

        Returns:
            계약 정보가 추가된 직원 목록 (활성 계약 있는 직원만)
        """
        from app.services.contract_filter_service import contract_filter_service
        from app.constants.status import ContractStatus

        if not company_id or not employees:
            return []

        # 벌크 계약 조회
        employee_numbers = [emp.get('employee_number') for emp in employees]
        contract_map = contract_filter_service.get_contracts_by_employee_numbers(
            employee_numbers=employee_numbers,
            company_id=company_id,
            statuses=ContractStatus.ACTIVE_STATUSES,
            exclude_resigned=True
        )

        result = []
        for emp in employees:
            employee_number = emp.get('employee_number')

            # 퇴사 직원 제외
            if emp.get('resignation_date'):
                continue

            # 계약 정보 매핑
            contract = contract_map.get(employee_number)
            if contract:
                emp['user_id'] = contract.person_user_id
                emp['user_email'] = (
                    contract.person_user.email
                    if contract.person_user else None
                )
                emp['contract_status'] = contract.status
                # 계정유형 및 아이디 추가
                if contract.person_user:
                    emp['account_type_label'] = contract.person_user.get_account_type_label()
                    emp['username'] = contract.person_user.username
                else:
                    emp['account_type_label'] = '-'
                    emp['username'] = '-'
                result.append(emp)

        return result

    # ========================================
    # Private: 폼 데이터 처리
    # ========================================

    def _extract_employee_from_form(self, form_data: Dict, employee_id: int = 0) -> Employee:
        """폼 데이터에서 Employee 객체 생성

        Phase 28: RRN 자동입력, 신규 필드 추가, blood_type/religion 삭제
        """
        org_id = form_data.get('organization_id')
        organization_id = int(org_id) if org_id and str(org_id).strip() else None

        # 수정 시 기존 employee의 company_id, organization_id 보존
        company_id = None
        if employee_id:
            existing = db.session.get(Employee, employee_id)
            if existing:
                company_id = existing.company_id
                if not organization_id:
                    organization_id = existing.organization_id

        # Phase 28: RRN에서 자동 입력 필드 추출
        rrn = form_data.get('resident_number') or form_data.get('rrn')
        birth_date = form_data.get('birth_date')
        age = form_data.get('age')
        gender = form_data.get('gender')

        if rrn:
            parsed = RRNParser.parse(rrn)
            if parsed.is_valid:
                birth_date = birth_date or parsed.birth_date
                age = age if age is not None else parsed.age
                gender = gender or parsed.gender

        # Phase 28: nationality 기본값
        nationality = form_data.get('nationality') or '대한민국'

        return Employee(
            company_id=company_id,
            id=employee_id,
            name=form_data.get('name', ''),
            photo=form_data.get('photo') or '/static/images/face/face_01_m.png',
            department=form_data.get('department', ''),
            position=form_data.get('position', ''),
            status=form_data.get('status', EmployeeStatus.ACTIVE),
            hire_date=form_data.get('hire_date') or form_data.get('hireDate', ''),
            phone=form_data.get('phone', ''),
            email=form_data.get('email', ''),
            organization_id=organization_id,
            employee_number=form_data.get('employee_number') or None,
            team=form_data.get('team') or None,
            job_title=form_data.get('job_title') or None,
            work_location=form_data.get('work_location') or None,
            internal_phone=form_data.get('internal_phone') or None,
            company_email=form_data.get('company_email') or None,
            english_name=form_data.get('english_name') or form_data.get('name_en') or None,
            chinese_name=form_data.get('chinese_name') or None,
            foreign_name=form_data.get('foreign_name') or None,  # Phase 28
            birth_date=birth_date,
            age=age,  # Phase 28
            gender=gender,
            address=form_data.get('address') or None,
            detailed_address=form_data.get('detailed_address') or None,
            postal_code=form_data.get('postal_code') or None,
            resident_number=rrn or None,
            mobile_phone=form_data.get('mobile_phone') or None,
            home_phone=form_data.get('home_phone') or None,
            nationality=nationality,
            # Phase 28: blood_type, religion 삭제
            hobby=form_data.get('hobby') or None,
            specialty=form_data.get('specialty') or None,
            disability_info=form_data.get('disability_info') or None,
            marital_status=form_data.get('marital_status') or None,
            # Phase 28: 계좌 정보
            bank_name=form_data.get('bank_name') or None,
            account_number=form_data.get('account_number') or None,
            account_holder=form_data.get('account_holder') or None,
            # 실제 거주 주소
            actual_postal_code=form_data.get('actual_postal_code') or None,
            actual_address=form_data.get('actual_address') or None,
            actual_detailed_address=form_data.get('actual_detailed_address') or None,
            # 비상연락처
            emergency_contact=form_data.get('emergency_contact') or None,
            emergency_relation=form_data.get('emergency_relation') or None,
        )

    def _extract_basic_fields(self, form_data: Dict) -> Dict:
        """기본 정보 필드만 추출

        Phase 28: 신규 필드 추가, blood_type/religion 삭제
        """
        return {
            'name': form_data.get('name', ''),
            'english_name': form_data.get('english_name') or None,
            'chinese_name': form_data.get('chinese_name') or None,
            'foreign_name': form_data.get('foreign_name') or None,  # Phase 28
            'resident_number': form_data.get('resident_number') or form_data.get('rrn') or None,
            'birth_date': form_data.get('birth_date') or None,
            'age': form_data.get('age') or None,  # Phase 28
            'gender': form_data.get('gender') or None,
            'marital_status': form_data.get('marital_status') or None,
            'phone': form_data.get('phone', ''),
            'email': form_data.get('email', ''),
            'mobile_phone': form_data.get('mobile_phone') or None,
            'home_phone': form_data.get('home_phone') or None,
            'address': form_data.get('address') or None,
            'detailed_address': form_data.get('detailed_address') or None,
            'postal_code': form_data.get('postal_code') or None,
            'actual_postal_code': form_data.get('actual_postal_code') or None,
            'actual_address': form_data.get('actual_address') or None,
            'actual_detailed_address': form_data.get('actual_detailed_address') or None,
            'nationality': form_data.get('nationality') or '대한민국',  # Phase 28: 기본값
            # Phase 28: blood_type, religion 삭제
            'hobby': form_data.get('hobby') or None,
            'specialty': form_data.get('specialty') or None,
            'disability_info': form_data.get('disability_info') or None,
            # Phase 28: 계좌 정보
            'bank_name': form_data.get('bank_name') or None,
            'account_number': form_data.get('account_number') or None,
            'account_holder': form_data.get('account_holder') or None,
            # 비상연락처
            'emergency_contact': form_data.get('emergency_contact') or None,
            'emergency_relation': form_data.get('emergency_relation') or None,
        }

    def _apply_rrn_auto_fields(self, fields: Dict) -> Dict:
        """Phase 28: RRN에서 자동 입력 필드 적용

        Args:
            fields: 기본 필드 딕셔너리

        Returns:
            자동 입력 필드가 적용된 딕셔너리
        """
        rrn = fields.get('resident_number')
        if not rrn:
            return fields

        parsed = RRNParser.parse(rrn)
        if not parsed.is_valid:
            return fields

        # 자동 입력 (기존 값이 없는 경우에만)
        if not fields.get('birth_date'):
            fields['birth_date'] = parsed.birth_date
        if fields.get('age') is None:
            fields['age'] = parsed.age
        if not fields.get('gender'):
            fields['gender'] = parsed.gender

        return fields


# 싱글톤 인스턴스
employee_core_service = EmployeeCoreService()
