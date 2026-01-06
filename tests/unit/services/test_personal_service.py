"""
PersonalService 단위 테스트

개인 계정 서비스의 핵심 비즈니스 로직 테스트:
- 회원가입 유효성 검사
- 프로필 조회/수정
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.services.personal_service import PersonalService, personal_service
from app.shared.base import ServiceResult


@pytest.fixture
def mock_repos(app):
    """PersonalService의 Repository를 Mock으로 대체하는 fixture"""
    mock_user_repo = Mock()
    mock_profile_repo = Mock()

    with patch.object(personal_service, 'user_repo', mock_user_repo), \
         patch.object(personal_service, 'profile_repo', mock_profile_repo):
        yield personal_service, mock_user_repo, mock_profile_repo


class TestPersonalServiceInit:
    """PersonalService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert personal_service is not None
        assert isinstance(personal_service, PersonalService)

    def test_service_has_repo_attributes(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(personal_service, 'user_repo')
        assert hasattr(personal_service, 'profile_repo')


class TestPersonalServiceValidation:
    """회원가입 유효성 검사 테스트"""

    def test_validate_registration_returns_errors_for_empty_fields(self, mock_repos):
        """빈 필드 유효성 검사"""
        service, _, _ = mock_repos

        errors = service.validate_registration(
            username='',
            email='',
            password='',
            password_confirm='',
            name=''
        )

        assert isinstance(errors, list)
        assert len(errors) > 0

    def test_validate_registration_returns_errors_for_short_password(self, mock_repos):
        """짧은 비밀번호 유효성 검사"""
        service, mock_user_repo, _ = mock_repos

        mock_user_repo.username_exists.return_value = False
        mock_user_repo.email_exists.return_value = False

        errors = service.validate_registration(
            username='testuser',
            email='test@example.com',
            password='short',
            password_confirm='short',
            name='Test User'
        )

        assert any('8자' in e for e in errors)

    def test_validate_registration_returns_errors_for_password_mismatch(self, mock_repos):
        """비밀번호 불일치 검사"""
        service, mock_user_repo, _ = mock_repos

        mock_user_repo.username_exists.return_value = False
        mock_user_repo.email_exists.return_value = False

        errors = service.validate_registration(
            username='testuser',
            email='test@example.com',
            password='password123',
            password_confirm='different123',
            name='Test User'
        )

        assert any('일치' in e for e in errors)

    def test_validate_registration_duplicate_username(self, mock_repos):
        """중복 사용자명 검사"""
        service, mock_user_repo, _ = mock_repos

        mock_user_repo.username_exists.return_value = True
        mock_user_repo.email_exists.return_value = False

        errors = service.validate_registration(
            username='existing_user',
            email='new@example.com',
            password='password123',
            password_confirm='password123',
            name='Test User'
        )

        assert any('아이디' in e for e in errors)

    def test_validate_registration_duplicate_email(self, mock_repos):
        """중복 이메일 검사"""
        service, mock_user_repo, _ = mock_repos

        mock_user_repo.username_exists.return_value = False
        mock_user_repo.email_exists.return_value = True

        errors = service.validate_registration(
            username='new_user',
            email='existing@example.com',
            password='password123',
            password_confirm='password123',
            name='Test User'
        )

        assert any('이메일' in e for e in errors)

    def test_validate_registration_success(self, mock_repos):
        """유효한 입력 시 빈 에러 목록 반환"""
        service, mock_user_repo, _ = mock_repos

        mock_user_repo.username_exists.return_value = False
        mock_user_repo.email_exists.return_value = False

        errors = service.validate_registration(
            username='newuser',
            email='new@example.com',
            password='password123',
            password_confirm='password123',
            name='New User'
        )

        assert errors == []


class TestPersonalServiceRegister:
    """회원가입 테스트"""

    def test_register_returns_service_result(self, mock_repos):
        """회원가입 ServiceResult 반환 확인"""
        service, mock_user_repo, mock_profile_repo = mock_repos

        with patch('app.services.personal_service.atomic_transaction'), \
             patch('app.services.personal_service.db'):
            result = service.register(
                username='testuser',
                email='test@example.com',
                password='password123',
                name='Test User',
                mobile_phone='010-1234-5678'
            )

        assert isinstance(result, ServiceResult)


class TestPersonalServiceProfile:
    """프로필 조회/수정 테스트"""

    def test_get_user_with_profile_returns_tuple(self, mock_repos):
        """사용자 + 프로필 조회 반환 형식 확인"""
        service, mock_user_repo, mock_profile_repo = mock_repos

        mock_user = Mock()
        mock_user.id = 1

        mock_profile = Mock()
        mock_profile.user_id = 1

        with patch('app.services.personal_service.User') as MockUser:
            MockUser.query.get.return_value = mock_user
            mock_profile_repo.get_by_user_id.return_value = mock_profile

            user, profile = service.get_user_with_profile(user_id=1)

        assert user is not None
        assert profile is not None

    def test_get_user_with_profile_user_not_found(self, mock_repos):
        """존재하지 않는 사용자 조회"""
        service, mock_user_repo, _ = mock_repos

        with patch('app.services.personal_service.User') as MockUser:
            MockUser.query.get.return_value = None

            user, profile = service.get_user_with_profile(user_id=999)

        assert user is None
        assert profile is None

    def test_update_profile_returns_service_result(self, mock_repos):
        """프로필 수정 ServiceResult 반환 확인"""
        service, _, mock_profile_repo = mock_repos

        mock_profile = Mock()
        mock_profile.id = 1
        mock_profile.to_dict = Mock(return_value={'id': 1, 'name': 'Updated'})
        mock_profile_repo.get_by_user_id.return_value = mock_profile

        with patch('app.services.personal_service.atomic_transaction'):
            result = service.update_profile(
                user_id=1,
                data={'name': 'Updated Name'}
            )

        assert isinstance(result, ServiceResult)

    def test_update_profile_not_found(self, mock_repos):
        """존재하지 않는 프로필 수정 시도"""
        service, _, mock_profile_repo = mock_repos

        mock_profile_repo.get_by_user_id.return_value = None

        result = service.update_profile(
            user_id=999,
            data={'name': 'Updated Name'}
        )

        assert isinstance(result, ServiceResult)
        assert result.success is False


class TestPersonalServiceRelations:
    """관계형 데이터 조회 테스트"""

    def test_get_educations_method_exists(self, app):
        """학력 목록 조회 메서드 존재 확인"""
        assert hasattr(personal_service, 'get_educations')
        assert callable(getattr(personal_service, 'get_educations'))

    def test_get_careers_method_exists(self, app):
        """경력 목록 조회 메서드 존재 확인"""
        assert hasattr(personal_service, 'get_careers')
        assert callable(getattr(personal_service, 'get_careers'))

    def test_get_certificates_method_exists(self, app):
        """자격증 목록 조회 메서드 존재 확인"""
        assert hasattr(personal_service, 'get_certificates')
        assert callable(getattr(personal_service, 'get_certificates'))

    def test_get_languages_method_exists(self, app):
        """어학 목록 조회 메서드 존재 확인"""
        assert hasattr(personal_service, 'get_languages')
        assert callable(getattr(personal_service, 'get_languages'))

    def test_get_military_method_exists(self, app):
        """병역 정보 조회 메서드 존재 확인"""
        assert hasattr(personal_service, 'get_military')
        assert callable(getattr(personal_service, 'get_military'))
