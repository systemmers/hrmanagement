"""
ContractService 단위 테스트

계약 서비스의 핵심 비즈니스 로직 테스트:
- 계약 조회 (개인/법인)
- 계약 통계
- 계약 검색
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.domains.contract.services.contract_service import ContractService, contract_service


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    mock_contract_repo = Mock()
    mock_user_repo = Mock()

    with patch('app.domains.contract.get_person_contract_repo', return_value=mock_contract_repo), \
         patch('app.domains.user.get_user_repo', return_value=mock_user_repo):
        yield contract_service, mock_contract_repo, mock_user_repo


class TestContractServiceInit:
    """ContractService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert contract_service is not None
        assert isinstance(contract_service, ContractService)

    def test_service_has_repo_attributes(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(contract_service, 'contract_repo')
        assert hasattr(contract_service, 'user_repo')


class TestContractServicePersonal:
    """개인 계정용 계약 조회 테스트"""

    def test_get_personal_contracts_returns_list(self, mock_repos):
        """개인 계약 목록 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1, 'status': 'approved'}]
        mock_contract_repo.get_by_person_user_id.return_value = expected

        result = service.get_personal_contracts(user_id=1)
        assert len(result) == 1
        assert result[0]['status'] == 'approved'

    def test_get_personal_pending_contracts_returns_list(self, mock_repos):
        """개인 대기 중인 계약 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1, 'status': 'pending'}]
        mock_contract_repo.get_pending_contracts_by_person.return_value = expected

        result = service.get_personal_pending_contracts(user_id=1)
        assert len(result) == 1
        assert result[0]['status'] == 'pending'

    def test_get_personal_statistics_returns_dict(self, mock_repos):
        """개인 계약 통계 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = {'total': 5, 'approved': 3, 'pending': 2}
        mock_contract_repo.get_statistics_by_person.return_value = expected

        result = service.get_personal_statistics(user_id=1)
        assert result['total'] == 5
        assert result['approved'] == 3


class TestContractServiceCompany:
    """법인 계정용 계약 조회 테스트"""

    def test_get_company_contracts_returns_list(self, mock_repos):
        """법인 계약 목록 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1, 'company_id': 1, 'status': 'approved'}]
        mock_contract_repo.get_by_company_id.return_value = expected

        result = service.get_company_contracts(company_id=1)
        assert len(result) == 1
        assert result[0]['company_id'] == 1

    def test_get_company_pending_contracts_returns_list(self, mock_repos):
        """법인 대기 중인 계약 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1, 'status': 'pending'}]
        mock_contract_repo.get_pending_contracts_by_company.return_value = expected

        result = service.get_company_pending_contracts(company_id=1)
        assert len(result) == 1
        assert result[0]['status'] == 'pending'

    def test_get_company_statistics_returns_dict(self, mock_repos):
        """법인 계약 통계 조회"""
        service, mock_contract_repo, _ = mock_repos
        expected = {'total': 50, 'approved': 40, 'pending': 10}
        mock_contract_repo.get_statistics_by_company.return_value = expected

        result = service.get_company_statistics(company_id=1)
        assert result['total'] == 50
        assert result['approved'] == 40


class TestContractServiceSearch:
    """계약 검색 테스트"""

    def test_search_contracts_calls_repo(self, mock_repos):
        """계약 검색 시 Repository 호출"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1, 'status': 'approved'}]
        mock_contract_repo.search_contracts.return_value = expected

        result = service.search_contracts(
            company_id=1,
            status='approved',
            contract_type='employment',
            search_term='홍길동'
        )
        assert len(result) == 1
        mock_contract_repo.search_contracts.assert_called_once_with(
            company_id=1,
            status='approved',
            contract_type='employment',
            search_term='홍길동'
        )

    def test_search_contracts_with_partial_params(self, mock_repos):
        """부분 파라미터로 검색"""
        service, mock_contract_repo, _ = mock_repos
        expected = [{'id': 1}, {'id': 2}]
        mock_contract_repo.search_contracts.return_value = expected

        result = service.search_contracts(company_id=1, status='pending')
        assert len(result) == 2


class TestContractServiceEligibleTargets:
    """계약 요청 가능 대상 조회 테스트"""

    def test_get_contract_eligible_targets_returns_dict(self, mock_repos):
        """계약 요청 가능 대상 목록 구조"""
        service, mock_contract_repo, _ = mock_repos
        with patch('app.domains.contract.services.contract_core_service.User') as MockUser:
            with patch('app.domains.contract.services.contract_core_service.Employee') as MockEmployee:
                MockUser.query.filter.return_value.all.return_value = []
                MockEmployee.query.filter.return_value.all.return_value = []

                result = service.get_contract_eligible_targets(company_id=1)

                assert 'personal_accounts' in result
                assert 'employee_accounts' in result
                assert isinstance(result['personal_accounts'], list)
                assert isinstance(result['employee_accounts'], list)


class TestContractServiceValidation:
    """계약 유효성 검증 테스트"""

    def test_empty_contracts_list(self, mock_repos):
        """빈 계약 목록 반환"""
        service, mock_contract_repo, _ = mock_repos
        mock_contract_repo.get_by_person_user_id.return_value = []

        result = service.get_personal_contracts(user_id=99999)
        assert result == []

    def test_empty_company_contracts_list(self, mock_repos):
        """빈 법인 계약 목록 반환"""
        service, mock_contract_repo, _ = mock_repos
        mock_contract_repo.get_by_company_id.return_value = []

        result = service.get_company_contracts(company_id=99999)
        assert result == []
