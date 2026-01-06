"""
UserRepository 단위 테스트
"""
import pytest
from app.repositories.user_repository import UserRepository
from app.models import User


class TestUserRepository:
    """UserRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = UserRepository()

    @pytest.mark.unit
    def test_create_user(self, session):
        """사용자 생성 테스트"""
        user = self.repo.create_user(
            username='newuser',
            email='newuser@test.com',
            password='password123',
            role=User.ROLE_EMPLOYEE
        )

        assert user is not None
        assert user.username == 'newuser'
        assert user.email == 'newuser@test.com'
        assert user.role == User.ROLE_EMPLOYEE
        assert user.is_active is True

    @pytest.mark.unit
    def test_get_by_username(self, session):
        """사용자명으로 조회 테스트"""
        # 사용자 생성
        user = User(
            username='findme',
            email='findme@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        # 조회
        result = self.repo.get_by_username('findme')

        assert result is not None
        assert result.username == 'findme'

    @pytest.mark.unit
    def test_get_by_username_not_found(self):
        """존재하지 않는 사용자명 조회"""
        result = self.repo.get_by_username('nonexistent')
        assert result is None

    @pytest.mark.unit
    def test_get_by_email(self, session):
        """이메일로 조회 테스트"""
        user = User(
            username='emailuser',
            email='email@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        result = self.repo.get_by_email('email@test.com')

        assert result is not None
        assert result.email == 'email@test.com'

    @pytest.mark.unit
    def test_authenticate_success(self, session):
        """인증 성공 테스트"""
        user = User(
            username='authuser',
            email='auth@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('correctpassword')
        session.add(user)
        session.commit()

        result = self.repo.authenticate('authuser', 'correctpassword')

        assert result is not None
        assert result.username == 'authuser'

    @pytest.mark.unit
    def test_authenticate_wrong_password(self, session):
        """잘못된 비밀번호 인증 테스트"""
        user = User(
            username='authfail',
            email='authfail@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('correctpassword')
        session.add(user)
        session.commit()

        result = self.repo.authenticate('authfail', 'wrongpassword')

        assert result is None

    @pytest.mark.unit
    def test_authenticate_inactive_user(self, session):
        """비활성 사용자 인증 테스트"""
        user = User(
            username='inactive',
            email='inactive@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=False
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        result = self.repo.authenticate('inactive', 'test1234')

        assert result is None

    @pytest.mark.unit
    def test_update_password(self, session):
        """비밀번호 변경 테스트"""
        user = User(
            username='pwdchange',
            email='pwdchange@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('oldpassword')
        session.add(user)
        session.commit()

        # 비밀번호 변경
        result = self.repo.update_password(user.id, 'newpassword')
        assert result is True

        # 새 비밀번호로 인증
        auth_result = self.repo.authenticate('pwdchange', 'newpassword')
        assert auth_result is not None

    @pytest.mark.unit
    def test_update_role(self, session):
        """역할 변경 테스트"""
        user = User(
            username='rolechange',
            email='rolechange@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        result = self.repo.update_role(user.id, User.ROLE_MANAGER)
        assert result is True

        # 변경 확인
        updated = self.repo.get_by_username('rolechange')
        assert updated.role == User.ROLE_MANAGER

    @pytest.mark.unit
    def test_update_role_invalid(self, session):
        """잘못된 역할 변경 테스트"""
        user = User(
            username='invalidrole',
            email='invalidrole@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        result = self.repo.update_role(user.id, 'invalid_role')
        assert result is False

    @pytest.mark.unit
    def test_deactivate_and_activate(self, session):
        """사용자 비활성화/활성화 테스트"""
        user = User(
            username='toggleuser',
            email='toggle@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        # 비활성화
        result = self.repo.deactivate(user.id)
        assert result is True

        # 비활성 확인
        deactivated = self.repo.get_by_username('toggleuser')
        assert deactivated.is_active is False

        # 활성화
        result = self.repo.activate(user.id)
        assert result is True

        # 활성 확인
        activated = self.repo.get_by_username('toggleuser')
        assert activated.is_active is True

    @pytest.mark.unit
    def test_username_exists(self, session):
        """사용자명 중복 확인 테스트"""
        user = User(
            username='existinguser',
            email='existing@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        assert self.repo.username_exists('existinguser') is True
        assert self.repo.username_exists('nonexistent') is False

    @pytest.mark.unit
    def test_email_exists(self, session):
        """이메일 중복 확인 테스트"""
        user = User(
            username='emailcheck',
            email='check@test.com',
            role=User.ROLE_EMPLOYEE,
            is_active=True
        )
        user.set_password('test1234')
        session.add(user)
        session.commit()

        assert self.repo.email_exists('check@test.com') is True
        assert self.repo.email_exists('notexist@test.com') is False
