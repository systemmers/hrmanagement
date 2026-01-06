"""
Contract Model 테스트

Contract 모델의 메서드 테스트:
- to_dict()
- from_dict()
"""
import pytest

from app.models.contract import Contract


class TestContractModel:
    """Contract 모델 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session

    @pytest.mark.unit
    def test_to_dict(self, session, test_employee):
        """to_dict() 메서드 테스트"""
        contract = Contract(
            employee_id=test_employee.id,
            contract_type='employment',
            contract_date='2024-01-01'
        )
        session.add(contract)
        session.commit()

        result = contract.to_dict()

        assert isinstance(result, dict)
        assert result['contract_type'] == 'employment'
        assert result['id'] == contract.id

    @pytest.mark.unit
    def test_from_dict(self, session, test_employee):
        """from_dict() 메서드 테스트"""
        data = {
            'employee_id': test_employee.id,
            'contract_type': 'employment',
            'contract_date': '2024-01-01',
            'contract_period': '2024-12-31'
        }

        contract = Contract.from_dict(data)
        session.add(contract)
        session.commit()

        assert contract.contract_type == 'employment'
        assert contract.contract_date == '2024-01-01'

