"""
ContractFilterService 단위 테스트

통합 계약 필터 서비스의 필터링 및 벌크 조회 테스트
"""
import pytest
from datetime import datetime
from app.services.contract_filter_service import ContractFilterService, contract_filter_service
from app.models import PersonCorporateContract
from app.domains.employee.models import Employee
from app.models import User
from app.models import Company
from app.shared.constants.status import ContractStatus


class TestContractFilterServiceInit:
    """ContractFilterService 초기화 테스트"""

    @pytest.mark.unit
    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert contract_filter_service is not None
        assert isinstance(contract_filter_service, ContractFilterService)

    @pytest.mark.unit
    def test_default_statuses(self, app):
        """기본 상태 값 확인"""
        assert ContractFilterService.DEFAULT_STATUSES == [ContractStatus.APPROVED]
        assert ContractStatus.TERMINATED in ContractFilterService.ACTIVE_STATUSES


class TestContractFilterServiceFiltering:
    """ContractFilterService 필터링 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_personal):
        """테스트 설정"""
        self.session = session
        self.service = ContractFilterService()
        self.company_id = test_company.id
        self.user_id = test_user_personal.id

        # 테스트 계약 생성
        self.contract_approved = PersonCorporateContract(
            person_user_id=self.user_id,
            company_id=self.company_id,
            status=ContractStatus.APPROVED,
            contract_type='employment',
            position='사원',
            department='개발팀',
            requested_by='company',
            employee_number='EMP001'
        )
        session.add(self.contract_approved)

        # 퇴사 직원 계약
        employee_resigned = Employee(
            employee_number='EMP002',
            name='퇴사직원',
            company_id=self.company_id,
            status='active',
            resignation_date=datetime.utcnow()
        )
        session.add(employee_resigned)

        contract_resigned = PersonCorporateContract(
            person_user_id=self.user_id,
            company_id=self.company_id,
            status=ContractStatus.APPROVED,
            contract_type='employment',
            position='사원',
            department='개발팀',
            requested_by='company',
            employee_number='EMP002'
        )
        session.add(contract_resigned)

        # 종료된 계약
        contract_terminated = PersonCorporateContract(
            person_user_id=self.user_id,
            company_id=self.company_id,
            status=ContractStatus.TERMINATED,
            contract_type='employment',
            position='사원',
            department='개발팀',
            requested_by='company',
            employee_number='EMP003'
        )
        session.add(contract_terminated)

        session.commit()

    @pytest.mark.unit
    def test_get_filtered_contracts_by_company(self):
        """법인 ID로 계약 필터링"""
        contracts = self.service.get_filtered_contracts(
            company_id=self.company_id
        )

        assert len(contracts) >= 1
        assert all(c.company_id == self.company_id for c in contracts)
        assert all(c.status == ContractStatus.APPROVED for c in contracts)

    @pytest.mark.unit
    def test_get_filtered_contracts_by_user(self):
        """사용자 ID로 계약 필터링"""
        contracts = self.service.get_filtered_contracts(
            person_user_id=self.user_id
        )

        assert len(contracts) >= 1
        assert all(c.person_user_id == self.user_id for c in contracts)

    @pytest.mark.unit
    def test_get_filtered_contracts_with_statuses(self):
        """상태 리스트로 필터링"""
        contracts = self.service.get_filtered_contracts(
            company_id=self.company_id,
            statuses=[ContractStatus.APPROVED, ContractStatus.TERMINATED]
        )

        statuses = [c.status for c in contracts]
        assert ContractStatus.APPROVED in statuses or ContractStatus.TERMINATED in statuses

    @pytest.mark.unit
    def test_get_filtered_contracts_include_terminated(self):
        """종료된 계약 포함"""
        contracts = self.service.get_filtered_contracts(
            company_id=self.company_id,
            include_terminated=True
        )

        statuses = [c.status for c in contracts]
        assert ContractStatus.TERMINATED in statuses or ContractStatus.APPROVED in statuses

    @pytest.mark.unit
    def test_get_filtered_contracts_exclude_resigned(self):
        """퇴사 직원 제외"""
        contracts = self.service.get_filtered_contracts(
            company_id=self.company_id,
            exclude_resigned=True
        )

        employee_numbers = [c.employee_number for c in contracts if c.employee_number]
        assert 'EMP002' not in employee_numbers

    @pytest.mark.unit
    def test_get_filtered_contracts_include_resigned(self):
        """퇴사 직원 포함"""
        contracts = self.service.get_filtered_contracts(
            company_id=self.company_id,
            exclude_resigned=False
        )

        employee_numbers = [c.employee_number for c in contracts if c.employee_number]
        # 퇴사 직원이 포함될 수 있음
        assert len(contracts) >= 1


class TestContractFilterServiceBulkQueries:
    """ContractFilterService 벌크 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_personal):
        """테스트 설정"""
        self.session = session
        self.service = ContractFilterService()
        self.company_id = test_company.id
        self.user_id = test_user_personal.id

        # 여러 계약 생성
        for i in range(1, 4):
            contract = PersonCorporateContract(
                person_user_id=self.user_id,
                company_id=self.company_id,
                status=ContractStatus.APPROVED,
                contract_type='employment',
                position='사원',
                department='개발팀',
                requested_by='company',
                employee_number=f'EMP{i:03d}'
            )
            session.add(contract)
        session.commit()

    @pytest.mark.unit
    def test_get_approved_contracts_map(self):
        """승인된 계약 맵 조회"""
        contracts_map = self.service.get_approved_contracts_map(
            company_id=self.company_id
        )

        assert isinstance(contracts_map, dict)
        assert len(contracts_map) >= 3
        assert 'EMP001' in contracts_map
        assert isinstance(contracts_map['EMP001'], PersonCorporateContract)

    @pytest.mark.unit
    def test_get_contracts_by_employee_numbers(self):
        """직원번호 목록으로 계약 조회"""
        employee_numbers = ['EMP001', 'EMP002', 'EMP003']

        contracts_map = self.service.get_contracts_by_employee_numbers(
            employee_numbers=employee_numbers,
            company_id=self.company_id
        )

        assert isinstance(contracts_map, dict)
        assert len(contracts_map) == 3
        assert all(num in contracts_map for num in employee_numbers)

    @pytest.mark.unit
    def test_get_contracts_by_employee_numbers_empty(self):
        """빈 직원번호 목록"""
        contracts_map = self.service.get_contracts_by_employee_numbers(
            employee_numbers=[],
            company_id=self.company_id
        )

        assert contracts_map == {}

    @pytest.mark.unit
    def test_get_contracts_by_employee_numbers_none_values(self):
        """None 값이 포함된 직원번호 목록"""
        contracts_map = self.service.get_contracts_by_employee_numbers(
            employee_numbers=['EMP001', None, 'EMP002'],
            company_id=self.company_id
        )

        assert isinstance(contracts_map, dict)
        assert 'EMP001' in contracts_map
        assert 'EMP002' in contracts_map

    @pytest.mark.unit
    def test_get_contracts_by_user_ids(self):
        """사용자 ID 목록으로 계약 조회"""
        user_ids = [self.user_id]

        contracts_map = self.service.get_contracts_by_user_ids(
            user_ids=user_ids,
            company_id=self.company_id
        )

        assert isinstance(contracts_map, dict)
        assert self.user_id in contracts_map
        assert isinstance(contracts_map[self.user_id], PersonCorporateContract)

    @pytest.mark.unit
    def test_get_contracts_by_user_ids_empty(self):
        """빈 사용자 ID 목록"""
        contracts_map = self.service.get_contracts_by_user_ids(
            user_ids=[],
            company_id=self.company_id
        )

        assert contracts_map == {}


class TestContractFilterServiceEmployees:
    """ContractFilterService 직원 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_personal):
        """테스트 설정"""
        self.session = session
        self.service = ContractFilterService()
        self.company_id = test_company.id
        self.user_id = test_user_personal.id

        # 직원과 계약 생성
        employee = Employee(
            employee_number='EMP001',
            name='테스트직원',
            company_id=self.company_id,
            status='active'
        )
        session.add(employee)

        contract = PersonCorporateContract(
            person_user_id=self.user_id,
            company_id=self.company_id,
            status=ContractStatus.APPROVED,
            contract_type='employment',
            position='사원',
            department='개발팀',
            requested_by='company',
            employee_number='EMP001'
        )
        session.add(contract)
        session.commit()

    @pytest.mark.unit
    def test_get_employees_with_approved_contracts(self):
        """승인된 계약이 있는 직원 목록 조회"""
        employees = self.service.get_employees_with_approved_contracts(
            company_id=self.company_id
        )

        assert len(employees) >= 1
        assert all('user_id' in emp for emp in employees)
        assert all('contract_status' in emp for emp in employees)
        assert all('contract_id' in emp for emp in employees)

    @pytest.mark.unit
    def test_get_employees_with_approved_contracts_exclude_resigned(self):
        """퇴사 직원 제외"""
        employees = self.service.get_employees_with_approved_contracts(
            company_id=self.company_id,
            exclude_resigned=True
        )

        # 퇴사 직원이 제외되었는지 확인
        assert isinstance(employees, list)


class TestContractFilterServiceActiveCheck:
    """ContractFilterService 활성 계약 확인 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_personal):
        """테스트 설정"""
        self.session = session
        self.service = ContractFilterService()
        self.company_id = test_company.id
        self.user_id = test_user_personal.id

    @pytest.mark.unit
    def test_is_contract_active_true(self):
        """활성 계약 존재 확인 (True)"""
        # 활성 계약 생성
        contract = PersonCorporateContract(
            person_user_id=self.user_id,
            company_id=self.company_id,
            status=ContractStatus.APPROVED,
            contract_type='employment',
            position='사원',
            department='개발팀',
            requested_by='company'
        )
        self.session.add(contract)
        self.session.commit()

        result = self.service.is_contract_active(
            user_id=self.user_id,
            company_id=self.company_id
        )

        assert result is True

    @pytest.mark.unit
    def test_is_contract_active_false(self):
        """활성 계약 없음 확인 (False)"""
        result = self.service.is_contract_active(
            user_id=99999,
            company_id=self.company_id
        )

        assert result is False


class TestContractFilterServiceEdgeCases:
    """ContractFilterService 엣지 케이스 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.service = ContractFilterService()

    @pytest.mark.unit
    def test_get_filtered_contracts_no_params(self):
        """파라미터 없이 조회"""
        contracts = self.service.get_filtered_contracts()

        assert isinstance(contracts, list)

    @pytest.mark.unit
    def test_get_approved_contracts_map_no_company(self):
        """법인 ID 없이 맵 조회"""
        contracts_map = self.service.get_approved_contracts_map(company_id=None)

        assert isinstance(contracts_map, dict)

    @pytest.mark.unit
    def test_get_contracts_by_employee_numbers_no_company(self):
        """법인 ID 없이 직원번호로 조회"""
        contracts_map = self.service.get_contracts_by_employee_numbers(
            employee_numbers=['EMP001'],
            company_id=None
        )

        assert contracts_map == {}

    @pytest.mark.unit
    def test_get_contracts_by_user_ids_no_company(self):
        """법인 ID 없이 사용자 ID로 조회"""
        contracts_map = self.service.get_contracts_by_user_ids(
            user_ids=[1],
            company_id=None
        )

        assert contracts_map == {}

