"""
UserService 단위 테스트

사용자 서비스의 핵심 비즈니스 로직 테스트:
- 사용자 인증
- 사용자 조회
- 사용자 관리
"""
import pytest
from unittest.mock import Mock, patch

from app.services.user_service import UserService, user_service


@pytest.fixture
def mock_repos(app):
    """UserService의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_user_repo = Mock()

    with patch.object(extensions, 'user_repo', mock_user_repo):
        yield user_service, mock_user_repo


class TestUserServiceInit:
    """UserService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert user_service is not None
        assert isinstance(user_service, UserService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(user_service, 'user_repo')


class TestUserServiceAuthentication:
    """사용자 인증 테스트"""

    def test_authenticate_calls_repo(self, mock_repos):
        """인증 메서드가 repo를 호출하는지 확인"""
        service, mock_repo = mock_repos

        mock_user = Mock()
        mock_user.id = 1
        mock_repo.authenticate.return_value = mock_user

        result = service.authenticate('testuser', 'password123')

        mock_repo.authenticate.assert_called_once_with('testuser', 'password123')
        assert result == mock_user

    def test_authenticate_returns_none_for_invalid(self, mock_repos):
        """잘못된 인증 시 None 반환"""
        service, mock_repo = mock_repos

        mock_repo.authenticate.return_value = None

        result = service.authenticate('invalid', 'wrong')

        assert result is None


class TestUserServiceQueries:
    """사용자 조회 테스트"""

    def test_get_by_id_returns_dict(self, mock_repos):
        """ID로 사용자 조회"""
        service, mock_repo = mock_repos

        expected = {'id': 1, 'username': 'test'}
        mock_repo.find_by_id.return_value = Mock(to_dict=Mock(return_value=expected))

        result = service.get_by_id(1)

        assert result is not None

    def test_get_by_id_returns_none(self, mock_repos):
        """존재하지 않는 사용자 조회"""
        service, mock_repo = mock_repos

        mock_repo.find_by_id.return_value = None

        result = service.get_by_id(999)

        assert result is None

    def test_get_model_by_id(self, mock_repos):
        """모델 직접 조회"""
        service, mock_repo = mock_repos

        mock_user = Mock()
        mock_user.id = 1
        mock_repo.find_by_id.return_value = mock_user

        result = service.get_model_by_id(1)

        assert result == mock_user


class TestUserServiceCompanyQueries:
    """법인 관련 사용자 조회 테스트"""

    def test_get_by_company_and_account_type(self, mock_repos):
        """법인 및 계정 타입별 사용자 조회"""
        service, mock_repo = mock_repos

        mock_users = [Mock(id=1), Mock(id=2)]
        mock_repo.get_by_company_and_account_type.return_value = mock_users

        result = service.get_by_company_and_account_type(
            company_id=1,
            account_type='employee_sub'
        )

        mock_repo.get_by_company_and_account_type.assert_called_once()
        assert result == mock_users

    def test_get_employee_sub_users_with_employee(self, mock_repos):
        """직원 연결된 사용자 조회"""
        service, mock_repo = mock_repos

        mock_result = [{'user_id': 1, 'employee_id': 10}]
        mock_repo.get_employee_sub_users_with_employee.return_value = mock_result

        result = service.get_employee_sub_users_with_employee(company_id=1)

        assert result == mock_result


class TestUserServicePrivacy:
    """개인정보 설정 테스트"""

    def test_get_privacy_settings(self, mock_repos):
        """개인정보 설정 조회"""
        service, mock_repo = mock_repos

        expected = {'show_email': True}
        mock_repo.get_privacy_settings.return_value = expected

        result = service.get_privacy_settings(user_id=1)

        assert result == expected

    def test_update_privacy_settings(self, mock_repos):
        """개인정보 설정 수정"""
        service, mock_repo = mock_repos

        mock_repo.update_privacy_settings.return_value = True

        result = service.update_privacy_settings(
            user_id=1,
            settings={'show_email': False}
        )

        assert result is True


class TestUserServicePassword:
    """비밀번호 관리 테스트"""

    def test_update_password(self, mock_repos):
        """비밀번호 변경"""
        service, mock_repo = mock_repos

        mock_repo.update_password.return_value = True

        result = service.update_password(user_id=1, new_password='newpass123')

        mock_repo.update_password.assert_called_once_with(1, 'newpass123')
        assert result is True


class TestUserServiceAccount:
    """계정 관리 테스트"""

    def test_deactivate(self, mock_repos):
        """계정 비활성화"""
        service, mock_repo = mock_repos

        mock_repo.deactivate.return_value = True

        result = service.deactivate(user_id=1)

        mock_repo.deactivate.assert_called_once_with(1)
        assert result is True
