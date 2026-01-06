"""
User Model 테스트

User 모델의 메서드 테스트:
- 비밀번호 설정/검증
- 권한 확인 메서드
- 계정 타입 확인 메서드
"""
import pytest

from app.models.user import User


class TestUserModel:
    """User 모델 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session

    @pytest.mark.unit
    def test_set_password(self, session):
        """비밀번호 설정 테스트"""
        user = User(
            username='testuser',
            email='test@test.com'
        )
        user.set_password('password123')
        session.add(user)
        session.commit()

        assert user.password_hash is not None
        assert user.password_hash != 'password123'

    @pytest.mark.unit
    def test_check_password(self, session):
        """비밀번호 검증 테스트"""
        user = User(
            username='testuser',
            email='test@test.com'
        )
        user.set_password('password123')
        session.add(user)
        session.commit()

        assert user.check_password('password123') is True
        assert user.check_password('wrongpassword') is False

    @pytest.mark.unit
    def test_is_admin(self, session):
        """관리자 여부 확인"""
        admin_user = User(
            username='admin',
            email='admin@test.com',
            role=User.ROLE_ADMIN
        )
        admin_user.set_password('password')
        session.add(admin_user)
        session.commit()

        assert admin_user.is_admin() is True
        assert admin_user.is_manager() is False

    @pytest.mark.unit
    def test_is_manager(self, session):
        """매니저 여부 확인"""
        manager_user = User(
            username='manager',
            email='manager@test.com',
            role=User.ROLE_MANAGER
        )
        manager_user.set_password('password')
        session.add(manager_user)
        session.commit()

        assert manager_user.is_manager() is True
        assert manager_user.is_admin() is False

    @pytest.mark.unit
    def test_is_personal_account(self, session):
        """개인 계정 여부 확인"""
        user = User(
            username='personal',
            email='personal@test.com',
            account_type=User.ACCOUNT_PERSONAL
        )
        user.set_password('password')
        session.add(user)
        session.commit()

        assert user.is_personal_account() is True
        assert user.is_corporate_account() is False

    @pytest.mark.unit
    def test_is_corporate_account(self, session):
        """법인 계정 여부 확인"""
        user = User(
            username='corporate',
            email='corporate@test.com',
            account_type=User.ACCOUNT_CORPORATE
        )
        user.set_password('password')
        session.add(user)
        session.commit()

        assert user.is_corporate_account() is True
        assert user.is_personal_account() is False

    @pytest.mark.unit
    def test_is_employee_sub_account(self, session):
        """법인 하위 직원 계정 여부 확인"""
        user = User(
            username='employee',
            email='employee@test.com',
            account_type=User.ACCOUNT_EMPLOYEE_SUB
        )
        user.set_password('password')
        session.add(user)
        session.commit()

        assert user.is_employee_sub_account() is True

    @pytest.mark.unit
    def test_get_account_type_label(self, session):
        """계정 타입 라벨 조회"""
        user = User(
            username='test',
            email='test@test.com',
            account_type=User.ACCOUNT_PERSONAL
        )
        user.set_password('password')
        session.add(user)
        session.commit()

        assert user.get_account_type_label() == '개인'

    @pytest.mark.unit
    def test_update_last_login(self, session):
        """마지막 로그인 시간 업데이트"""
        user = User(
            username='test',
            email='test@test.com'
        )
        user.set_password('password')
        session.add(user)
        session.commit()

        initial_login = user.last_login
        user.update_last_login()

        assert user.last_login is not None
        assert user.last_login != initial_login

