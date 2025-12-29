"""
Contract Filter Service - 통합 계약 필터 서비스

Personal과 Employee_Sub 계정에서 동일한 조건으로 계약을 조회합니다.
N+1 쿼리 방지를 위한 벌크 조회 메서드를 제공합니다.

SSOT 원칙: PersonCorporateContract가 계약 관계의 유일한 진실의 원천
"""
from typing import List, Dict, Optional
from sqlalchemy.orm import joinedload

from ..database import db
from ..models.person_contract import PersonCorporateContract
from ..models.employee import Employee
from ..models.user import User
from ..constants.status import ContractStatus


class ContractFilterService:
    """통합 계약 필터 서비스

    Personal과 Employee_Sub 계정의 계약 조회 조건을 통합합니다.
    """

    # 기본 상태 값
    DEFAULT_STATUSES = [ContractStatus.APPROVED]
    ACTIVE_STATUSES = [ContractStatus.APPROVED, ContractStatus.TERMINATED]

    def get_filtered_contracts(
        self,
        company_id: int = None,
        person_user_id: int = None,
        statuses: List[str] = None,
        include_terminated: bool = False,
        exclude_resigned: bool = True
    ) -> List[PersonCorporateContract]:
        """통합 계약 필터링

        Args:
            company_id: 법인 ID (employee_sub용)
            person_user_id: 개인 사용자 ID (personal용)
            statuses: 조회할 상태 리스트 (기본: ['approved'])
            include_terminated: 종료된 계약 포함 여부
            exclude_resigned: 퇴사 직원 제외 여부

        Returns:
            필터링된 계약 리스트
        """
        if statuses is None:
            statuses = self.DEFAULT_STATUSES.copy()

        if include_terminated and ContractStatus.TERMINATED not in statuses:
            statuses.append(ContractStatus.TERMINATED)

        query = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.status.in_(statuses)
        )

        if company_id:
            query = query.filter(PersonCorporateContract.company_id == company_id)
        if person_user_id:
            query = query.filter(PersonCorporateContract.person_user_id == person_user_id)

        contracts = query.all()

        # 퇴사 직원 제외
        if exclude_resigned:
            contracts = [c for c in contracts if not self._is_resigned(c)]

        return contracts

    def get_approved_contracts_map(
        self,
        company_id: int,
        exclude_resigned: bool = True
    ) -> Dict[str, PersonCorporateContract]:
        """approved 계약을 employee_number 기준 맵으로 반환

        직원목록에서 N+1 쿼리 방지를 위해 사용

        Args:
            company_id: 법인 ID
            exclude_resigned: 퇴사 직원 제외 여부

        Returns:
            Dict[employee_number, PersonCorporateContract]
        """
        contracts = self.get_filtered_contracts(
            company_id=company_id,
            statuses=[ContractStatus.APPROVED],
            exclude_resigned=exclude_resigned
        )

        return {
            c.employee_number: c
            for c in contracts
            if c.employee_number
        }

    def get_contracts_by_employee_numbers(
        self,
        employee_numbers: List[str],
        company_id: int,
        statuses: List[str] = None,
        exclude_resigned: bool = True
    ) -> Dict[str, PersonCorporateContract]:
        """employee_number 목록으로 계약 벌크 조회

        Args:
            employee_numbers: 직원번호 목록
            company_id: 법인 ID
            statuses: 조회할 상태 리스트 (기본: ['approved'])
            exclude_resigned: 퇴사 직원 제외 여부

        Returns:
            Dict[employee_number, PersonCorporateContract]
        """
        if not employee_numbers or not company_id:
            return {}

        # None 값 필터링
        valid_numbers = [n for n in employee_numbers if n]
        if not valid_numbers:
            return {}

        if statuses is None:
            statuses = self.DEFAULT_STATUSES.copy()

        contracts = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.employee_number.in_(valid_numbers),
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_(statuses)
        ).all()

        # 퇴사 직원 제외
        if exclude_resigned:
            contracts = [c for c in contracts if not self._is_resigned(c)]

        return {
            c.employee_number: c
            for c in contracts
            if c.employee_number
        }

    def get_contracts_by_user_ids(
        self,
        user_ids: List[int],
        company_id: int,
        statuses: List[str] = None
    ) -> Dict[int, PersonCorporateContract]:
        """user_id 목록으로 계약 벌크 조회

        Args:
            user_ids: User ID 목록
            company_id: 법인 ID
            statuses: 조회할 상태 리스트 (기본: ['approved'])

        Returns:
            Dict[user_id, PersonCorporateContract]
        """
        if not user_ids or not company_id:
            return {}

        if statuses is None:
            statuses = self.DEFAULT_STATUSES.copy()

        contracts = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.person_user_id.in_(user_ids),
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_(statuses)
        ).all()

        return {c.person_user_id: c for c in contracts}

    def get_employees_with_approved_contracts(
        self,
        company_id: int,
        exclude_resigned: bool = True
    ) -> List[Dict]:
        """approved 계약이 있는 직원 목록 조회

        직원목록 페이지에서 사용하는 통합 메서드

        Args:
            company_id: 법인 ID
            exclude_resigned: 퇴사 직원 제외 여부

        Returns:
            직원 정보와 계약 정보를 포함한 딕셔너리 리스트
        """
        contracts = self.get_filtered_contracts(
            company_id=company_id,
            statuses=[ContractStatus.APPROVED],
            exclude_resigned=exclude_resigned
        )

        result = []
        for contract in contracts:
            if contract.employee:
                emp_dict = contract.employee.to_dict()
                emp_dict['user_id'] = contract.person_user_id
                emp_dict['user_email'] = (
                    contract.person_user.email
                    if contract.person_user else None
                )
                emp_dict['contract_status'] = contract.status
                emp_dict['contract_id'] = contract.id
                result.append(emp_dict)

        return result

    def _is_resigned(self, contract: PersonCorporateContract) -> bool:
        """계약의 직원이 퇴사했는지 확인

        Args:
            contract: PersonCorporateContract 객체

        Returns:
            퇴사 여부 (resignation_date가 있으면 True)
        """
        # PersonCorporateContract에는 employee 관계가 없으므로
        # employee_number로 Employee를 조회하여 확인
        if contract.employee_number:
            from ..models.employee import Employee
            employee = Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()
            if employee:
                return employee.resignation_date is not None
        return False

    def is_contract_active(
        self,
        user_id: int,
        company_id: int
    ) -> bool:
        """특정 User와 회사 간 활성 계약 존재 여부

        Args:
            user_id: User ID
            company_id: 법인 ID

        Returns:
            활성 계약 존재 여부
        """
        contract = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).first()

        return contract is not None


# 싱글톤 인스턴스
contract_filter_service = ContractFilterService()
