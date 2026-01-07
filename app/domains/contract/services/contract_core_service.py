"""
Contract Core Service

계약 조회 관련 비즈니스 로직을 처리합니다.
- 개인/법인 계약 목록 조회
- 계약 상세 조회
- 계약 검색
- 계약 대상 조회

Phase 30: 레이어 분리 - Model.query 제거, Repository 패턴 적용
"""
from typing import Dict, Optional, List, Any

from app.shared.constants.status import ContractStatus


class ContractCoreService:
    """계약 조회 서비스

    Phase 30: Repository DI 패턴 적용
    """

    def __init__(self):
        self._contract_repo = None
        self._user_repo = None
        self._employee_repo = None
        self._profile_repo = None

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        if self._contract_repo is None:
            from app.extensions import person_contract_repo
            self._contract_repo = person_contract_repo
        return self._contract_repo

    @property
    def user_repo(self):
        """지연 초기화된 User Repository"""
        if self._user_repo is None:
            from app.domains.user.repositories.user_repository import user_repository
            self._user_repo = user_repository
        return self._user_repo

    @property
    def employee_repo(self):
        """지연 초기화된 Employee Repository"""
        if self._employee_repo is None:
            from app.domains.employee.repositories import EmployeeRepository
            self._employee_repo = EmployeeRepository()
        return self._employee_repo

    @property
    def profile_repo(self):
        """지연 초기화된 Profile Repository"""
        if self._profile_repo is None:
            from app.domains.employee.repositories import ProfileRepository
            self._profile_repo = ProfileRepository()
        return self._profile_repo

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

        Phase 30: Repository 패턴 적용

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
        # Phase 30: Repository 사용
        personal_users = self.user_repo.find_active_personal_users()

        for user in personal_users:
            existing_contract = self.contract_repo.get_contract_between(
                person_user_id=user.id,
                company_id=company_id
            )
            if not existing_contract or existing_contract.get('status') in [ContractStatus.REJECTED, ContractStatus.TERMINATED]:
                # Phase 30: Repository 사용 - Profile에서 실제 이름 조회
                profile = self.profile_repo.get_by_user_id(user.id)
                actual_name = profile.name if profile else user.username

                result['personal_accounts'].append({
                    'user_id': user.id,
                    'username': user.username,  # 아이디 (로그인용)
                    'name': actual_name,         # 실제 이름
                    'email': user.email,
                    'account_type': 'personal'
                })

        # 2. 직원계정 중 계약 미체결 상태 (pending_info 또는 pending_contract)
        # Phase 30: Repository 사용
        pending_employees = self.employee_repo.find_by_company_and_statuses(
            company_id, ['pending_info', 'pending_contract']
        )

        for emp in pending_employees:
            # Phase 30: Repository 사용
            emp_user = self.user_repo.find_by_employee_id(emp.id)

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
        Phase 30: Repository 패턴 적용
        계약 이력이 있는 직원은 필드 수정 불가
        """
        return self.contract_repo.find_with_history(
            employee_number=employee_number,
            company_id=company_id,
            history_statuses=[
                ContractStatus.APPROVED,
                ContractStatus.TERMINATION_REQUESTED,
                ContractStatus.TERMINATED,
                ContractStatus.EXPIRED
            ]
        )

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
