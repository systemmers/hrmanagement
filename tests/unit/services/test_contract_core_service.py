"""
ContractCoreService 단위 테스트

계약 조회 서비스의 핵심 비즈니스 로직 테스트:
- 개인 계약 목록 조회
- 법인 계약 목록 조회
- 계약 검색
- 계약 상세 조회
- 계약 대상 조회
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from app.services.contract.contract_core_service import (
    ContractCoreService,
    contract_core_service
)
from app.models.person_contract import PersonCorporateContract
from app.models.user import User
from app.models.employee import Employee
from app.shared.constants.status import ContractStatus


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_contract_repo = Mock()
    with patch.object(extensions, 'person_contract_repo', mock_contract_repo):
        yield contract_core_service


class TestContractCoreServiceInit:
    """ContractCoreService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert contract_core_service is not None
        assert isinstance(contract_core_service, ContractCoreService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(contract_core_service, 'contract_repo')


class TestContractCoreServicePersonal:
    """개인 계정용 메서드 테스트"""

    def test_get_personal_contracts(self, mock_repos):
        """개인 계약 목록 조회"""
        mock_repos.contract_repo.get_by_person_user_id.return_value = [
            {'id': 1, 'status': 'approved'},
            {'id': 2, 'status': 'pending'}
        ]
        
        result = mock_repos.get_personal_contracts(user_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repos.contract_repo.get_by_person_user_id.assert_called_once_with(1)

    def test_get_personal_pending_contracts(self, mock_repos):
        """개인 대기 중인 계약 조회"""
        mock_repos.contract_repo.get_pending_contracts_by_person.return_value = [
            {'id': 1, 'status': 'pending'}
        ]
        
        result = mock_repos.get_personal_pending_contracts(user_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_repos.contract_repo.get_pending_contracts_by_person.assert_called_once_with(1)

    def test_get_personal_statistics(self, mock_repos):
        """개인 계약 통계 조회"""
        mock_repos.contract_repo.get_statistics_by_person.return_value = {
            'total': 5,
            'approved': 3,
            'pending': 2
        }
        
        result = mock_repos.get_personal_statistics(user_id=1)
        
        assert isinstance(result, dict)
        assert 'total' in result
        mock_repos.contract_repo.get_statistics_by_person.assert_called_once_with(1)


class TestContractCoreServiceCorporate:
    """법인 계정용 메서드 테스트"""

    def test_get_company_contracts(self, mock_repos):
        """법인 계약 목록 조회"""
        mock_repos.contract_repo.get_by_company_id.return_value = [
            {'id': 1, 'status': 'approved'},
            {'id': 2, 'status': 'pending'}
        ]
        
        result = mock_repos.get_company_contracts(company_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 2
        mock_repos.contract_repo.get_by_company_id.assert_called_once_with(1)

    def test_get_company_pending_contracts(self, mock_repos):
        """법인 대기 중인 계약 조회"""
        mock_repos.contract_repo.get_pending_contracts_by_company.return_value = [
            {'id': 1, 'status': 'pending'}
        ]
        
        result = mock_repos.get_company_pending_contracts(company_id=1)
        
        assert isinstance(result, list)
        assert len(result) == 1
        mock_repos.contract_repo.get_pending_contracts_by_company.assert_called_once_with(1)

    def test_get_company_statistics(self, mock_repos):
        """법인 계약 통계 조회"""
        mock_repos.contract_repo.get_statistics_by_company.return_value = {
            'total': 10,
            'approved': 7,
            'pending': 3
        }
        
        result = mock_repos.get_company_statistics(company_id=1)
        
        assert isinstance(result, dict)
        assert 'total' in result
        mock_repos.contract_repo.get_statistics_by_company.assert_called_once_with(1)

    def test_search_contracts(self, mock_repos):
        """계약 검색"""
        mock_repos.contract_repo.search_contracts.return_value = [
            {'id': 1, 'status': 'approved', 'name': '홍길동'}
        ]
        
        result = mock_repos.search_contracts(
            company_id=1,
            status='approved',
            search_term='홍길동'
        )
        
        assert isinstance(result, list)
        mock_repos.contract_repo.search_contracts.assert_called_once_with(
            company_id=1,
            status='approved',
            contract_type=None,
            search_term='홍길동'
        )


class TestContractCoreServiceGetEligibleTargets:
    """계약 요청 가능한 대상 목록 조회 테스트"""

    def test_get_contract_eligible_targets(self, mock_repos, session):
        """계약 요청 가능한 대상 목록 조회"""
        with patch('app.services.contract.contract_core_service.User') as mock_user, \
             patch('app.services.contract.contract_core_service.Employee') as mock_employee:
            
            # 개인 계정 Mock
            personal_user = Mock()
            personal_user.id = 1
            personal_user.username = 'testuser'
            personal_user.email = 'test@test.com'
            personal_user.account_type = 'personal'
            personal_user.is_active = True
            
            # 직원 Mock
            employee = Mock()
            employee.id = 1
            employee.name = '직원1'
            employee.department = '개발팀'
            employee.position = '사원'
            employee.status = 'pending_contract'
            employee.company_id = 1
            
            emp_user = Mock()
            emp_user.id = 2
            emp_user.email = 'emp@test.com'
            emp_user.employee_id = 1
            
            mock_user.query.filter.return_value.all.return_value = [personal_user]
            mock_employee.query.filter.return_value.all.return_value = [employee]
            mock_user.query.filter.return_value.first.return_value = emp_user
            
            mock_repos.contract_repo.get_contract_between.return_value = None
            
            result = mock_repos.get_contract_eligible_targets(company_id=1)
            
            assert isinstance(result, dict)
            assert 'personal_accounts' in result
            assert 'employee_accounts' in result
            assert isinstance(result['personal_accounts'], list)
            assert isinstance(result['employee_accounts'], list)


class TestContractCoreServiceGetContract:
    """계약 상세 조회 테스트"""

    def test_get_contract_by_id_success(self, mock_repos):
        """계약 상세 조회 성공"""
        mock_contract = Mock()
        mock_contract.to_dict.return_value = {'id': 1, 'status': 'approved'}
        mock_repos.contract_repo.find_by_id.return_value = mock_contract
        
        result = mock_repos.get_contract_by_id(contract_id=1)
        
        assert isinstance(result, dict)
        assert result['id'] == 1
        mock_repos.contract_repo.find_by_id.assert_called_once_with(1)

    def test_get_contract_by_id_not_found(self, mock_repos):
        """계약 상세 조회 - 존재하지 않음"""
        mock_repos.contract_repo.find_by_id.return_value = None
        
        result = mock_repos.get_contract_by_id(contract_id=999)
        
        assert result is None

    def test_get_contract_model_by_id(self, mock_repos):
        """계약 모델 조회"""
        mock_contract = Mock()
        mock_repos.contract_repo.find_by_id.return_value = mock_contract
        
        result = mock_repos.get_contract_model_by_id(contract_id=1)
        
        assert result is not None
        assert result == mock_contract

    def test_find_contract_with_history(self, mock_repos, session):
        """계약 이력 조회"""
        with patch('app.services.contract.contract_core_service.PersonCorporateContract') as mock_model:
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.first.return_value = Mock(id=1, status='approved')
            mock_model.query = mock_query
            
            result = mock_repos.find_contract_with_history(
                employee_number='EMP001',
                company_id=1
            )
            
            assert result is not None

    def test_find_contract_with_history_invalid_params(self, mock_repos):
        """계약 이력 조회 - 잘못된 파라미터"""
        result = mock_repos.find_contract_with_history(
            employee_number=None,
            company_id=1
        )
        
        assert result is None

    def test_find_approved_contract(self, mock_repos):
        """승인된 계약 조회"""
        mock_repos.contract_repo.find_approved_contract_by_employee_number.return_value = Mock(
            id=1,
            status='approved'
        )
        
        result = mock_repos.find_approved_contract(
            employee_number='EMP001',
            company_id=1
        )
        
        assert result is not None
        mock_repos.contract_repo.find_approved_contract_by_employee_number.assert_called_once_with(
            'EMP001',
            1
        )

    def test_get_employee_contract_status(self, mock_repos):
        """직원의 계약 상태 조회"""
        mock_repos.contract_repo.get_contract_between.return_value = {
            'status': 'approved'
        }
        
        result = mock_repos.get_employee_contract_status(
            employee_user_id=1,
            company_id=1
        )
        
        assert result == 'approved'
        mock_repos.contract_repo.get_contract_between.assert_called_once_with(
            person_user_id=1,
            company_id=1
        )

    def test_get_employee_contract_status_none(self, mock_repos):
        """직원의 계약 상태 조회 - 계약 없음"""
        mock_repos.contract_repo.get_contract_between.return_value = None
        
        result = mock_repos.get_employee_contract_status(
            employee_user_id=1,
            company_id=1
        )
        
        assert result == 'none'

