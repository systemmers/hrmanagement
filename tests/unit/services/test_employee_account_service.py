"""
EmployeeAccountService 단위 테스트

직원 계정 연동 서비스의 핵심 비즈니스 로직 테스트:
- 직원 + 계정 동시 생성
- 계정 비활성화/재활성화
- 계정 정보 검증
- 비밀번호 생성
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict

from app.domains.employee.services.employee_account_service import EmployeeAccountService, employee_account_service
from app.domains.employee.models import Employee
from app.models import User


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_employee_repo = Mock()
    mock_user_repo = Mock()

    with patch.object(extensions, 'employee_repo', mock_employee_repo), \
         patch.object(extensions, 'user_repo', mock_user_repo):
        yield employee_account_service


class TestEmployeeAccountServiceInit:
    """EmployeeAccountService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert employee_account_service is not None
        assert isinstance(employee_account_service, EmployeeAccountService)

    def test_service_has_repo_properties(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(employee_account_service, 'employee_repo')
        assert hasattr(employee_account_service, 'user_repo')


class TestEmployeeAccountServiceValidation:
    """계정 정보 검증 테스트"""

    def test_validate_account_data_valid(self, mock_repos, session):
        """유효한 계정 정보 검증"""
        with patch('app.services.employee_account_service.User') as mock_user:
            mock_user.query.filter_by.return_value.first.return_value = None

            result = mock_repos.validate_account_data(
                username='testuser',
                email='test@example.com'
            )

            assert result['valid'] is True
            assert len(result['errors']) == 0

    def test_validate_account_data_short_username(self, mock_repos):
        """사용자명이 너무 짧을 때"""
        result = mock_repos.validate_account_data(
            username='abc',
            email='test@example.com'
        )

        assert result['valid'] is False
        assert 'username' in result['errors']

    def test_validate_account_data_invalid_email(self, mock_repos):
        """이메일 형식이 잘못되었을 때"""
        result = mock_repos.validate_account_data(
            username='testuser',
            email='invalid-email'
        )

        assert result['valid'] is False
        assert 'email' in result['errors']

    def test_validate_account_data_duplicate_username(self, mock_repos, session):
        """중복된 사용자명일 때"""
        with patch('app.services.employee_account_service.User') as mock_user:
            mock_existing = Mock()
            mock_existing.id = 1
            mock_user.query.filter_by.return_value.first.return_value = mock_existing

            result = mock_repos.validate_account_data(
                username='existinguser',
                email='test@example.com'
            )

            assert result['valid'] is False
            assert 'username' in result['errors']

    def test_validate_account_data_exclude_user_id(self, mock_repos, session):
        """수정 시 자신의 ID는 제외"""
        with patch('app.services.employee_account_service.User') as mock_user:
            mock_existing = Mock()
            mock_existing.id = 1
            mock_user.query.filter_by.return_value.first.return_value = mock_existing

            result = mock_repos.validate_account_data(
                username='testuser',
                email='test@example.com',
                exclude_user_id=1
            )

            assert result['valid'] is True


class TestEmployeeAccountServicePasswordGeneration:
    """비밀번호 생성 테스트"""

    def test_generate_password_length(self, mock_repos):
        """비밀번호 길이 확인"""
        password = mock_repos.generate_password()
        assert len(password) == EmployeeAccountService.PASSWORD_LENGTH

    def test_generate_password_chars(self, mock_repos):
        """비밀번호 문자 집합 확인"""
        password = mock_repos.generate_password()
        allowed_chars = EmployeeAccountService.PASSWORD_CHARS
        assert all(c in allowed_chars for c in password)

    def test_generate_password_uniqueness(self, mock_repos):
        """비밀번호 생성의 고유성 확인"""
        passwords = [mock_repos.generate_password() for _ in range(10)]
        assert len(set(passwords)) > 1


class TestEmployeeAccountServiceCreateEmployeeWithAccount:
    """직원 + 계정 동시 생성 테스트"""

    def test_create_employee_with_account_success(self, mock_repos, session, test_company):
        """직원 + 계정 생성 성공"""
        employee_data = {
            'name': '테스트직원',
            'department': '개발팀',
            'position': '사원'
        }
        account_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'password123',
            'role': User.ROLE_EMPLOYEE
        }

        with patch('app.services.employee_account_service.User') as mock_user_model, \
             patch('app.services.employee_account_service.Employee') as mock_employee_model, \
             patch('app.services.employee_account_service.atomic_transaction'):
            mock_user_model.query.filter_by.return_value.first.return_value = None
            mock_employee = Mock()
            mock_employee.id = 1
            mock_user = Mock()
            mock_user.id = 2
            mock_user.username = 'testuser'
            mock_user.email = 'test@example.com'

            mock_repos._create_employee = Mock(return_value=mock_employee)
            mock_repos._create_user = Mock(return_value=mock_user)

            success, result, error = mock_repos.create_employee_with_account(
                employee_data=employee_data,
                account_data=account_data,
                company_id=test_company.id,
                admin_user_id=1
            )

            assert success is True
            assert result is not None
            assert result['employee_id'] == 1
            assert result['user_id'] == 2
            assert error is None

    def test_create_employee_with_account_validation_error(self, mock_repos, session):
        """계정 정보 검증 실패"""
        employee_data = {'name': '테스트직원'}
        account_data = {
            'username': 'ab',  # 너무 짧음
            'email': 'invalid-email'
        }

        with patch('app.services.employee_account_service.User') as mock_user_model:
            mock_user_model.query.filter_by.return_value.first.return_value = None

            success, result, error = mock_repos.create_employee_with_account(
                employee_data=employee_data,
                account_data=account_data,
                company_id=1,
                admin_user_id=1
            )

            assert success is False
            assert result is None
            assert error is not None


class TestEmployeeAccountServiceAccountManagement:
    """계정 관리 테스트"""

    def test_deactivate_employee_account_success(self, mock_repos, session):
        """직원 계정 비활성화 성공"""
        mock_employee = Mock()
        mock_employee.id = 1
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        with patch('app.services.employee_account_service.User') as mock_user_model, \
             patch('app.services.employee_account_service.atomic_transaction'):
            mock_user = Mock()
            mock_user_model.query.filter_by.return_value.first.return_value = mock_user

            success, error = mock_repos.deactivate_employee_account(
                employee_id=1,
                reason='테스트',
                deactivated_by=1
            )

            assert success is True
            assert error is None
            assert mock_user.is_active is False
            assert mock_employee.status == 'inactive'

    def test_deactivate_employee_account_not_found(self, mock_repos):
        """직원을 찾을 수 없을 때"""
        mock_repos.employee_repo.find_by_id.return_value = None

        success, error = mock_repos.deactivate_employee_account(
            employee_id=999,
            reason='테스트',
            deactivated_by=1
        )

        assert success is False
        assert '찾을 수 없습니다' in error

    def test_reactivate_employee_account_success(self, mock_repos, session):
        """직원 계정 재활성화 성공"""
        mock_employee = Mock()
        mock_employee.id = 1
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        with patch('app.services.employee_account_service.User') as mock_user_model, \
             patch('app.services.employee_account_service.atomic_transaction'), \
             patch('app.services.employee_account_service.EmployeeStatus') as mock_status:
            mock_status.ACTIVE = 'active'
            mock_user = Mock()
            mock_user_model.query.filter_by.return_value.first.return_value = mock_user

            success, error = mock_repos.reactivate_employee_account(
                employee_id=1,
                reactivated_by=1
            )

            assert success is True
            assert error is None
            assert mock_user.is_active is True


class TestEmployeeAccountServiceGetEmployeesWithoutAccount:
    """계정 없는 직원 조회 테스트"""

    def test_get_employees_without_account(self, mock_repos, session, test_company):
        """계정 없는 직원 목록 조회"""
        with patch('app.services.employee_account_service.Employee') as mock_employee_model, \
             patch('app.services.employee_account_service.User') as mock_user_model:
            mock_emp1 = Mock()
            mock_emp1.id = 1
            mock_emp1.name = '직원1'
            mock_emp1.department = '개발팀'
            mock_emp1.position = '사원'
            mock_emp1.email = 'emp1@test.com'

            mock_emp2 = Mock()
            mock_emp2.id = 2
            mock_emp2.name = '직원2'
            mock_emp2.department = '인사팀'
            mock_emp2.position = '대리'
            mock_emp2.email = 'emp2@test.com'

            mock_employee_model.query.filter_by.return_value.all.return_value = [mock_emp1, mock_emp2]

            def user_filter_side_effect(**kwargs):
                mock_query = Mock()
                if kwargs.get('employee_id') == 1:
                    mock_query.first.return_value = Mock()  # 계정 있음
                else:
                    mock_query.first.return_value = None  # 계정 없음
                return mock_query

            mock_user_model.query.filter_by.side_effect = user_filter_side_effect

            result = mock_repos.get_employees_without_account(test_company.id)

            assert len(result) == 1
            assert result[0]['id'] == 2
            assert result[0]['name'] == '직원2'

