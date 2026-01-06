"""
UserEmployeeLinkService 단위 테스트

User-Employee 연결 조회 서비스 테스트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.user_employee_link_service import UserEmployeeLinkService


class TestUserEmployeeLinkServiceInit:
    """초기화 테스트"""

    def test_service_initialization(self):
        """서비스 초기화"""
        service = UserEmployeeLinkService()
        assert service is not None
        assert hasattr(service, '_contract_repo')
        assert hasattr(service, '_user_repo')


class TestGetLinkedUser:
    """연결된 사용자 조회 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_get_linked_user_success(self, service):
        """연결된 사용자 조회 성공"""
        mock_user = Mock()
        mock_user.id = 1
        mock_user.email = 'test@example.com'
        
        mock_contract = Mock()
        mock_contract.person_user_id = 1
        
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = mock_contract
        
        service._user_repo = Mock()
        service._user_repo.find_by_id.return_value = mock_user
        
        result = service.get_linked_user(employee_id=100)
        
        assert result == mock_user
        service._contract_repo.get_contract_for_employee.assert_called_once_with(100)
        service._user_repo.find_by_id.assert_called_once_with(1)

    def test_get_linked_user_no_contract(self, service):
        """계약이 없을 때"""
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = None
        
        result = service.get_linked_user(employee_id=100)
        
        assert result is None

    def test_get_linked_user_no_person_user_id(self, service):
        """person_user_id가 없을 때"""
        mock_contract = Mock()
        mock_contract.person_user_id = None
        
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = mock_contract
        
        result = service.get_linked_user(employee_id=100)
        
        assert result is None


class TestGetLinkedUserDict:
    """연결된 사용자 Dict 조회 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_get_linked_user_dict_success(self, service):
        """사용자 Dict 조회 성공"""
        mock_user = Mock()
        mock_user.to_dict.return_value = {'id': 1, 'email': 'test@example.com'}
        
        service.get_linked_user = Mock(return_value=mock_user)
        
        result = service.get_linked_user_dict(employee_id=100)
        
        assert result == {'id': 1, 'email': 'test@example.com'}
        service.get_linked_user.assert_called_once_with(100)

    def test_get_linked_user_dict_no_user(self, service):
        """사용자가 없을 때"""
        service.get_linked_user = Mock(return_value=None)
        
        result = service.get_linked_user_dict(employee_id=100)
        
        assert result is None


class TestGetLinkedUsersBulk:
    """벌크 조회 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_get_linked_users_bulk_success(self, service):
        """벌크 조회 성공"""
        mock_user1 = Mock()
        mock_user1.id = 1
        
        mock_user2 = Mock()
        mock_user2.id = 2
        
        mock_contract1 = Mock()
        mock_contract1.person_user = mock_user1
        
        mock_contract2 = Mock()
        mock_contract2.person_user = mock_user2
        
        service._contract_repo = Mock()
        service._contract_repo.get_by_employee_ids_bulk.return_value = {
            100: mock_contract1,
            200: mock_contract2
        }
        
        result = service.get_linked_users_bulk([100, 200])
        
        assert len(result) == 2
        assert result[100] == mock_user1
        assert result[200] == mock_user2

    def test_get_linked_users_bulk_empty_list(self, service):
        """빈 리스트"""
        result = service.get_linked_users_bulk([])
        
        assert result == {}

    def test_get_linked_users_bulk_no_person_user(self, service):
        """person_user가 없는 계약"""
        mock_contract = Mock()
        mock_contract.person_user = None
        
        service._contract_repo = Mock()
        service._contract_repo.get_by_employee_ids_bulk.return_value = {
            100: mock_contract
        }
        
        result = service.get_linked_users_bulk([100])
        
        assert result == {}


class TestGetLinkedEmployee:
    """연결된 직원 조회 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    @patch('app.services.user_employee_link_service.Employee')
    def test_get_linked_employee_success(self, mock_employee, service):
        """연결된 직원 조회 성공"""
        mock_emp = Mock()
        mock_emp.id = 100
        
        mock_contract = Mock()
        mock_contract.employee_number = 'EMP001'
        
        service._contract_repo = Mock()
        service._contract_repo.get_active_contract_by_person_and_company.return_value = mock_contract
        
        mock_employee.query.filter_by.return_value.first.return_value = mock_emp
        
        result = service.get_linked_employee(user_id=1, company_id=10)
        
        assert result == mock_emp
        service._contract_repo.get_active_contract_by_person_and_company.assert_called_once_with(1, 10)

    def test_get_linked_employee_no_contract(self, service):
        """계약이 없을 때"""
        service._contract_repo = Mock()
        service._contract_repo.get_active_contract_by_person_and_company.return_value = None
        
        result = service.get_linked_employee(user_id=1, company_id=10)
        
        assert result is None

    @patch('app.services.user_employee_link_service.Employee')
    def test_get_linked_employee_no_employee_number(self, mock_employee, service):
        """employee_number가 없을 때"""
        mock_emp = Mock()
        
        mock_contract = Mock()
        mock_contract.employee_number = None
        
        service._contract_repo = Mock()
        service._contract_repo.get_active_contract_by_person_and_company.return_value = mock_contract
        
        mock_employee.query.filter_by.return_value.first.return_value = mock_emp
        
        result = service.get_linked_employee(user_id=1, company_id=10)
        
        assert result == mock_emp


class TestGetLinkedEmployees:
    """사용자의 모든 직원 조회 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    @patch('app.services.user_employee_link_service.Employee')
    def test_get_linked_employees_success(self, mock_employee, service):
        """모든 직원 조회 성공"""
        mock_emp1 = Mock()
        mock_emp1.id = 100
        mock_emp1.company_id = 1
        
        mock_emp2 = Mock()
        mock_emp2.id = 200
        mock_emp2.company_id = 2
        
        # contracts는 dict 리스트 반환
        service._contract_repo = Mock()
        service._contract_repo.get_active_contracts_by_person.return_value = [
            {'company_id': 1}, {'company_id': 2}
        ]
        
        mock_employee.query.filter.return_value.all.return_value = [mock_emp1, mock_emp2]
        
        result = service.get_linked_employees(user_id=1)
        
        assert len(result) == 2
        assert mock_emp1 in result
        assert mock_emp2 in result

    def test_get_linked_employees_no_contracts(self, service):
        """계약이 없을 때"""
        service._contract_repo = Mock()
        service._contract_repo.get_active_contracts_by_person.return_value = []
        
        result = service.get_linked_employees(user_id=1)
        
        assert result == []


class TestHasLinkedUser:
    """연결된 사용자 존재 확인 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_has_linked_user_true(self, service):
        """사용자 연결됨"""
        mock_contract = Mock()
        mock_contract.person_user_id = 1
        
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = mock_contract
        
        result = service.has_linked_user(employee_id=100)
        
        assert result is True

    def test_has_linked_user_false_no_contract(self, service):
        """계약 없음"""
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = None
        
        result = service.has_linked_user(employee_id=100)
        
        assert result is False

    def test_has_linked_user_false_no_user_id(self, service):
        """person_user_id 없음"""
        mock_contract = Mock()
        mock_contract.person_user_id = None
        
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = mock_contract
        
        result = service.has_linked_user(employee_id=100)
        
        assert result is False


class TestGetContractMethods:
    """계약 조회 메서드 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_get_contract_for_employee_success(self, service):
        """직원 계약 조회 성공"""
        mock_contract = Mock()
        
        service._contract_repo = Mock()
        service._contract_repo.get_contract_for_employee.return_value = mock_contract
        
        result = service.get_contract_for_employee(employee_id=100)
        
        assert result == mock_contract
        service._contract_repo.get_contract_for_employee.assert_called_once_with(100)

    def test_get_contract_for_employee_by_user_success(self, service):
        """사용자 계약 조회 성공"""
        mock_contract = Mock()
        
        service._contract_repo = Mock()
        service._contract_repo.get_active_contracts_by_person.return_value = [
            {'id': 1}
        ]
        service._contract_repo.find_by_id.return_value = mock_contract
        
        result = service.get_contract_for_employee_by_user(user_id=1)
        
        assert result == mock_contract

    def test_get_contract_for_employee_by_user_no_contracts(self, service):
        """계약 없음"""
        service._contract_repo = Mock()
        service._contract_repo.get_active_contracts_by_person.return_value = []
        
        result = service.get_contract_for_employee_by_user(user_id=1)
        
        assert result is None


class TestBulkMethods:
    """벌크 조회 메서드 테스트"""

    @pytest.fixture
    def service(self):
        """서비스 인스턴스"""
        return UserEmployeeLinkService()

    def test_get_users_with_contract_status_bulk_success(self, service):
        """사용자 계약 상태 벌크 조회"""
        mock_contract = Mock()
        mock_contract.status = 'approved'
        
        service._contract_repo = Mock()
        service._contract_repo.get_contracts_by_user_ids_bulk.return_value = {
            1: mock_contract
        }
        
        result = service.get_users_with_contract_status_bulk(
            user_ids=[1, 2],
            company_id=10
        )
        
        assert len(result) == 2
        assert result[1]['status'] == 'approved'
        assert result[2]['status'] == 'none'

    def test_get_users_with_contract_status_bulk_empty(self, service):
        """빈 입력"""
        result = service.get_users_with_contract_status_bulk(
            user_ids=[],
            company_id=10
        )
        
        assert result == {}

