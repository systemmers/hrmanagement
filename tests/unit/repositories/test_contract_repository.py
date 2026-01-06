"""
ContractRepository 단위 테스트
"""
import pytest
from app.domains.employee.repositories import ContractRepository
from app.domains.employee.models import Contract


class TestContractRepository:
    """ContractRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = ContractRepository()

    @pytest.mark.unit
    def test_create_contract(self, session, test_employee):
        """계약 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'contract_type': 'employment',
            'contract_date': '2024-01-01',
            'contract_period': '2024-12-31'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['contract_type'] == 'employment'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_id(self, session, test_employee):
        """ID로 계약 조회 테스트"""
        contract = Contract(
            employee_id=test_employee.id,
            contract_type='employment',
            contract_date='2024-01-01'
        )
        session.add(contract)
        session.commit()

        result = self.repo.find_by_id(contract.id)

        assert result is not None
        assert isinstance(result, Contract)
        assert result.contract_type == 'employment'

