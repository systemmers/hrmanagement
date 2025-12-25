"""
User-Employee 연결 조회 통합 서비스

SSOT 원칙: PersonCorporateContract가 User-Employee 관계의 유일한 진실의 원천
DIP 원칙: Repository를 통한 데이터 접근
SRP 원칙: User-Employee 연결 조회 로직만 담당
"""
from typing import Optional, List, Dict
from app.repositories.person_contract_repository import PersonContractRepository
from app.repositories.user_repository import UserRepository
from app.models.user import User
from app.models.employee import Employee


class UserEmployeeLinkService:
    """
    User-Employee 연결 조회 통합 서비스

    기존 User.employee_id 기반 조회를 PersonCorporateContract 기반으로 대체
    모든 User-Employee 관계 조회는 이 서비스를 통해 수행

    원칙:
    - SSOT: PersonCorporateContract가 유일한 진실의 원천
    - DIP: Repository를 통한 데이터 접근
    - SRP: 조회 로직 통합만 담당
    """

    def __init__(self):
        self._contract_repo = PersonContractRepository()
        self._user_repo = UserRepository()

    def get_linked_user(self, employee_id: int) -> Optional[User]:
        """직원에 연결된 User 조회

        Args:
            employee_id: Employee.id

        Returns:
            연결된 User 객체 또는 None
        """
        contract = self._contract_repo.get_contract_for_employee(employee_id)
        if contract and contract.person_user_id:
            return self._user_repo.get_model_by_id(contract.person_user_id)
        return None

    def get_linked_user_dict(self, employee_id: int) -> Optional[Dict]:
        """직원에 연결된 User 정보를 Dict로 조회

        Args:
            employee_id: Employee.id

        Returns:
            연결된 User 정보 딕셔너리 또는 None
        """
        user = self.get_linked_user(employee_id)
        return user.to_dict() if user else None

    def get_linked_users_bulk(self, employee_ids: List[int]) -> Dict[int, User]:
        """목록 페이지용 N+1 방지 벌크 조회

        Args:
            employee_ids: Employee.id 목록

        Returns:
            Dict[employee_id, User]: employee_id를 키로 하는 User 매핑
        """
        if not employee_ids:
            return {}

        contracts = self._contract_repo.get_by_employee_ids_bulk(employee_ids)

        result = {}
        for emp_id, contract in contracts.items():
            if contract.person_user:
                result[emp_id] = contract.person_user

        return result

    def get_linked_employee(self, user_id: int, company_id: int) -> Optional[Employee]:
        """User와 특정 회사 간의 연결된 Employee 조회

        Args:
            user_id: User.id
            company_id: Company.id

        Returns:
            해당 회사에 연결된 Employee 객체 또는 None
        """
        contract = self._contract_repo.get_active_contract_by_person_and_company(user_id, company_id)
        if contract and contract.employee_number:
            return Employee.query.filter_by(
                company_id=company_id,
                employee_number=contract.employee_number
            ).first()
        # employee_number가 없으면 해당 회사 소속 Employee 조회
        if contract:
            return Employee.query.filter_by(company_id=company_id).first()
        return None

    def get_linked_employees(self, user_id: int) -> List[Employee]:
        """User에 연결된 모든 Employee 조회

        개인 계정이 여러 법인과 계약한 경우 모든 Employee 반환

        Args:
            user_id: User.id

        Returns:
            연결된 Employee 목록
        """
        contracts = self._contract_repo.get_active_contracts_by_person(user_id)
        if not contracts:
            return []

        # 계약된 회사들의 Employee 조회
        company_ids = [c.get('company_id') for c in contracts if c.get('company_id')]
        if not company_ids:
            return []

        return Employee.query.filter(Employee.company_id.in_(company_ids)).all()

    def has_linked_user(self, employee_id: int) -> bool:
        """직원에 연결된 User 존재 여부 확인

        Args:
            employee_id: Employee.id

        Returns:
            User 연결 여부
        """
        contract = self._contract_repo.get_contract_for_employee(employee_id)
        return contract is not None and contract.person_user_id is not None

    def get_contract_for_employee(self, employee_id: int):
        """직원의 활성 계약 조회

        Args:
            employee_id: Employee.id

        Returns:
            PersonCorporateContract 또는 None
        """
        return self._contract_repo.get_contract_for_employee(employee_id)

    def get_contract_for_employee_by_user(self, user_id: int):
        """User의 활성 계약 조회 (employee_sub 계정용)

        Args:
            user_id: User.id

        Returns:
            PersonCorporateContract 또는 None
        """
        contracts = self._contract_repo.get_active_contracts_by_person(user_id)
        if contracts:
            # 첫 번째 활성 계약 반환 (employee_sub는 보통 1개만 있음)
            return self._contract_repo.get_model_by_id(contracts[0].get('id'))
        return None

    def get_users_with_contract_status_bulk(
        self,
        user_ids: List[int],
        company_id: int
    ) -> Dict[int, Dict]:
        """N+1 방지: 여러 User의 계약 상태 한번에 조회

        DRY 원칙: corporate.py, list_routes.py 등에서 공통 사용

        Args:
            user_ids: User ID 목록
            company_id: 회사 ID

        Returns:
            Dict[user_id, {'status': str, 'contract': PersonCorporateContract}]
        """
        if not user_ids or not company_id:
            return {}

        contracts_map = self._contract_repo.get_contracts_by_user_ids_bulk(user_ids, company_id)

        result = {}
        for user_id in user_ids:
            contract = contracts_map.get(user_id)
            if contract:
                result[user_id] = {
                    'status': contract.status,
                    'contract': contract
                }
            else:
                result[user_id] = {
                    'status': 'none',
                    'contract': None
                }

        return result

    def get_employees_with_approved_contracts_bulk(
        self,
        employee_numbers: List[str],
        company_id: int
    ) -> Dict[str, Dict]:
        """N+1 방지: employee_number 목록으로 approved 계약과 User 정보 조회

        DRY 원칙: list_routes.py의 직원목록에서 사용

        Args:
            employee_numbers: 직원번호 목록
            company_id: 회사 ID

        Returns:
            Dict[employee_number, {'status': str, 'user': User, 'contract': PersonCorporateContract}]
        """
        if not employee_numbers or not company_id:
            return {}

        contracts_map = self._contract_repo.get_approved_by_employee_numbers_bulk(
            employee_numbers, company_id
        )

        result = {}
        for emp_num in employee_numbers:
            if not emp_num:
                continue
            contract = contracts_map.get(emp_num)
            if contract:
                result[emp_num] = {
                    'status': 'approved',
                    'user': contract.person_user,
                    'contract': contract
                }

        return result

    def get_employees_from_approved_contracts(
        self,
        company_id: int
    ) -> List[Dict]:
        """승인된 계약 기반 직원 목록 조회

        21번 원칙: 계약 approved인 경우만 직원목록에 표시
        employee_number NULL인 경우 email 매칭으로 fallback

        Args:
            company_id: 회사 ID

        Returns:
            List[Dict]: 직원 정보 목록 (user_id, user_email, contract_status 포함)
        """
        if not company_id:
            return []

        # 1. 승인된 계약 조회
        contracts = self._contract_repo.get_approved_contracts_with_users(company_id)
        if not contracts:
            return []

        # 2. employee_number 있는 계약과 없는 계약 분리
        contracts_with_emp_num = []
        contracts_without_emp_num = []
        for c in contracts:
            if c.employee_number:
                contracts_with_emp_num.append(c)
            else:
                contracts_without_emp_num.append(c)

        # 3. employee_number 기반 Employee 조회 (벌크)
        emp_numbers = [c.employee_number for c in contracts_with_emp_num]
        employees_by_number = {}
        if emp_numbers:
            employees = Employee.query.filter(
                Employee.company_id == company_id,
                Employee.employee_number.in_(emp_numbers)
            ).all()
            employees_by_number = {e.employee_number: e for e in employees}

        # 4. email 기반 Employee 조회 (fallback용)
        user_emails = [c.person_user.email for c in contracts_without_emp_num if c.person_user]
        employees_by_email = {}
        if user_emails:
            employees = Employee.query.filter(
                Employee.company_id == company_id,
                Employee.email.in_(user_emails)
            ).all()
            employees_by_email = {e.email: e for e in employees if e.email}

        # 5. 결과 조립
        result = []
        seen_employee_ids = set()

        # 5-1. employee_number 매칭
        for contract in contracts_with_emp_num:
            emp = employees_by_number.get(contract.employee_number)
            if emp and emp.id not in seen_employee_ids:
                emp_dict = emp.to_dict()
                emp_dict['user_id'] = contract.person_user.id if contract.person_user else None
                emp_dict['user_email'] = contract.person_user.email if contract.person_user else None
                emp_dict['contract_status'] = 'approved'
                result.append(emp_dict)
                seen_employee_ids.add(emp.id)

        # 5-2. email 매칭 (fallback)
        for contract in contracts_without_emp_num:
            if not contract.person_user:
                continue
            emp = employees_by_email.get(contract.person_user.email)
            if emp and emp.id not in seen_employee_ids:
                emp_dict = emp.to_dict()
                emp_dict['user_id'] = contract.person_user.id
                emp_dict['user_email'] = contract.person_user.email
                emp_dict['contract_status'] = 'approved'
                result.append(emp_dict)
                seen_employee_ids.add(emp.id)

        return result


# 싱글톤 인스턴스
user_employee_link_service = UserEmployeeLinkService()
