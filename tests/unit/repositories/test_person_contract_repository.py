"""
PersonContractRepository 단위 테스트
"""
import pytest
from app.repositories.contract.person_contract_repository import PersonContractRepository
from app.models import PersonCorporateContract


class TestPersonContractRepository:
    """PersonContractRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = PersonContractRepository()

    @pytest.mark.unit
    def test_create_contract_request(self, session, test_user_personal, test_company):
        """계약 요청 생성 테스트"""
        result = self.repo.create_contract_request(
            person_user_id=test_user_personal.id,
            company_id=test_company.id,
            requested_by='company',
            contract_type='employment',
            position='사원',
            department='개발팀'
        )

        assert result is not None
        assert result['status'] == PersonCorporateContract.STATUS_REQUESTED
        assert result['contract_type'] == 'employment'

    @pytest.mark.unit
    def test_get_by_person_user_id(self, session, test_user_personal, test_company):
        """개인 사용자의 계약 조회"""
        contract = PersonCorporateContract(
            person_user_id=test_user_personal.id,
            company_id=test_company.id,
            status=PersonCorporateContract.STATUS_APPROVED
        )
        session.add(contract)
        session.commit()

        result = self.repo.get_by_person_user_id(test_user_personal.id)

        assert len(result) >= 1
        assert result[0]['person_user_id'] == test_user_personal.id

    @pytest.mark.unit
    def test_get_contract_between(self, session, test_user_personal, test_company):
        """특정 개인과 기업 간 계약 조회"""
        contract = PersonCorporateContract(
            person_user_id=test_user_personal.id,
            company_id=test_company.id,
            status=PersonCorporateContract.STATUS_APPROVED
        )
        session.add(contract)
        session.commit()

        result = self.repo.get_contract_between(
            person_user_id=test_user_personal.id,
            company_id=test_company.id
        )

        assert result is not None
        assert result['person_user_id'] == test_user_personal.id

    @pytest.mark.unit
    def test_get_active_contracts_by_person(self, session, test_user_personal, test_company):
        """개인의 활성 계약 조회"""
        contract = PersonCorporateContract(
            person_user_id=test_user_personal.id,
            company_id=test_company.id,
            status=PersonCorporateContract.STATUS_APPROVED
        )
        session.add(contract)
        session.commit()

        result = self.repo.get_active_contracts_by_person(test_user_personal.id)

        assert len(result) >= 1
        assert all(c['status'] == PersonCorporateContract.STATUS_APPROVED for c in result)

