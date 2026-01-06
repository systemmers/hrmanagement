"""
인증 데코레이터 테스트

app/utils/decorators.py의 인증 데코레이터 및 헬퍼 함수를 테스트합니다.
Phase 27: 품질 인프라 구축 - 핵심 인증 로직 테스트 커버리지 확보
"""
import pytest
from flask import url_for, session

from app.shared.constants import SessionKeys, AccountType, UserRole
from app.shared.utils.decorators import (
    # 헬퍼 함수
    _check_login,
    _check_api_login,
    _check_account_type,
    _check_api_account_type,
    _check_role,
    _check_superadmin,
    _check_api_superadmin,
    # 데코레이터
    login_required,
    personal_login_required,
    corporate_login_required,
    corporate_admin_required,
    api_login_required,
    api_corporate_account_required,
    superadmin_required,
)


# ============================================================
# 헬퍼 함수 테스트
# ============================================================

class TestCheckLogin:
    """_check_login() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_login_with_authenticated_user(self, app, client):
        """로그인된 사용자는 None 반환"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = 1

        with app.test_request_context():
            session[SessionKeys.USER_ID] = 1
            result = _check_login()
            assert result is None

    @pytest.mark.unit
    def test_check_login_without_session(self, app):
        """비로그인 사용자는 리다이렉트 튜플 반환"""
        with app.test_request_context():
            result = _check_login()
            assert result is not None
            assert len(result) == 1
            # 리다이렉트 응답 확인
            response = result[0]
            assert response.status_code == 302


class TestCheckApiLogin:
    """_check_api_login() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_api_login_authenticated(self, app):
        """로그인된 사용자는 None 반환"""
        with app.test_request_context():
            session[SessionKeys.USER_ID] = 1
            result = _check_api_login()
            assert result is None

    @pytest.mark.unit
    def test_check_api_login_unauthenticated(self, app):
        """비로그인 사용자는 401 JSON 반환"""
        with app.test_request_context():
            result = _check_api_login()
            assert result is not None
            response, status_code = result
            assert status_code == 401
            data = response.get_json()
            assert data['success'] is False


class TestCheckAccountType:
    """_check_account_type() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_account_type_matching(self, app):
        """계정 타입 일치 시 None 반환"""
        with app.test_request_context():
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = _check_account_type(AccountType.PERSONAL)
            assert result is None

    @pytest.mark.unit
    def test_check_account_type_personal_mismatch(self, app):
        """개인 계정 요구 시 법인 계정이면 리다이렉트"""
        with app.test_request_context():
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            result = _check_account_type(AccountType.PERSONAL)
            assert result is not None
            response = result[0]
            assert response.status_code == 302

    @pytest.mark.unit
    def test_check_account_type_corporate_mismatch(self, app):
        """법인 계정 요구 시 개인 계정이면 리다이렉트"""
        with app.test_request_context():
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = _check_account_type(AccountType.CORPORATE)
            assert result is not None
            response = result[0]
            assert response.status_code == 302


class TestCheckApiAccountType:
    """_check_api_account_type() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_api_account_type_matching(self, app):
        """계정 타입 일치 시 None 반환"""
        with app.test_request_context():
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            result = _check_api_account_type(AccountType.CORPORATE)
            assert result is None

    @pytest.mark.unit
    def test_check_api_account_type_mismatch(self, app):
        """계정 타입 불일치 시 403 JSON 반환"""
        with app.test_request_context():
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = _check_api_account_type(AccountType.CORPORATE)
            assert result is not None
            response, status_code = result
            assert status_code == 403
            data = response.get_json()
            assert data['success'] is False


class TestCheckRole:
    """_check_role() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_role_matching(self, app):
        """역할 일치 시 None 반환"""
        with app.test_request_context():
            session[SessionKeys.USER_ROLE] = UserRole.ADMIN
            result = _check_role(UserRole.ADMIN, UserRole.MANAGER)
            assert result is None

    @pytest.mark.unit
    def test_check_role_mismatch(self, app):
        """역할 불일치 시 abort 튜플 반환"""
        with app.test_request_context():
            session[SessionKeys.USER_ROLE] = UserRole.EMPLOYEE
            # abort는 예외를 발생시키므로 pytest.raises로 테스트
            with pytest.raises(Exception):
                _check_role(UserRole.ADMIN)


class TestCheckSuperadmin:
    """_check_superadmin() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_superadmin_is_superadmin(self, app):
        """슈퍼관리자는 None 반환"""
        with app.test_request_context():
            session[SessionKeys.IS_SUPERADMIN] = True
            result = _check_superadmin()
            assert result is None

    @pytest.mark.unit
    def test_check_superadmin_not_superadmin(self, app):
        """비슈퍼관리자는 abort 호출"""
        with app.test_request_context():
            session[SessionKeys.IS_SUPERADMIN] = False
            with pytest.raises(Exception):
                _check_superadmin()


class TestCheckApiSuperadmin:
    """_check_api_superadmin() 헬퍼 함수 테스트"""

    @pytest.mark.unit
    def test_check_api_superadmin_is_superadmin(self, app):
        """슈퍼관리자는 None 반환"""
        with app.test_request_context():
            session[SessionKeys.IS_SUPERADMIN] = True
            result = _check_api_superadmin()
            assert result is None

    @pytest.mark.unit
    def test_check_api_superadmin_not_superadmin(self, app):
        """비슈퍼관리자는 403 JSON 반환"""
        with app.test_request_context():
            session[SessionKeys.IS_SUPERADMIN] = False
            result = _check_api_superadmin()
            assert result is not None
            response, status_code = result
            assert status_code == 403
            data = response.get_json()
            assert data['success'] is False


# ============================================================
# 데코레이터 테스트
# ============================================================

class TestLoginRequired:
    """@login_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_login_required_allows_authenticated(self, client, test_user_personal, session):
        """로그인 사용자는 통과"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL

        # 실제 라우트 테스트 대신 데코레이터 동작 직접 테스트
        @login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_login_required_redirects_anonymous(self, client):
        """비로그인 사용자는 로그인 페이지로 리다이렉트"""
        @login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            result = dummy_view()
            assert result.status_code == 302
            assert 'login' in result.location


class TestPersonalLoginRequired:
    """@personal_login_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_personal_login_required_allows_personal(self, client, test_user_personal, session):
        """개인 계정은 통과"""
        @personal_login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_personal_login_required_rejects_corporate(self, client, test_user_corporate, session):
        """법인 계정은 거부"""
        @personal_login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            result = dummy_view()
            assert result.status_code == 302

    @pytest.mark.unit
    def test_personal_login_required_redirects_anonymous(self, client):
        """비로그인 사용자는 로그인 페이지로 리다이렉트"""
        @personal_login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            result = dummy_view()
            assert result.status_code == 302
            assert 'login' in result.location


class TestCorporateLoginRequired:
    """@corporate_login_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_corporate_login_required_allows_corporate(self, client, test_user_corporate, session):
        """법인 계정은 통과"""
        @corporate_login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_corporate_login_required_rejects_personal(self, client, test_user_personal, session):
        """개인 계정은 거부"""
        @corporate_login_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = dummy_view()
            assert result.status_code == 302


class TestCorporateAdminRequired:
    """@corporate_admin_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_corporate_admin_required_allows_admin(self, client, test_user_corporate, session):
        """법인 admin은 통과"""
        @corporate_admin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            flask_session[SessionKeys.USER_ROLE] = UserRole.ADMIN
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_corporate_admin_required_allows_manager(self, client, test_user_corporate, session):
        """법인 manager는 통과"""
        @corporate_admin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            flask_session[SessionKeys.USER_ROLE] = UserRole.MANAGER
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_corporate_admin_required_rejects_employee(self, client, test_user_corporate, session):
        """법인 employee는 거부"""
        @corporate_admin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            flask_session[SessionKeys.USER_ROLE] = UserRole.EMPLOYEE
            result = dummy_view()
            assert result.status_code == 302

    @pytest.mark.unit
    def test_corporate_admin_required_rejects_personal(self, client, test_user_personal, session):
        """개인 계정은 거부"""
        @corporate_admin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = dummy_view()
            assert result.status_code == 302


class TestApiLoginRequired:
    """@api_login_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_api_login_required_allows_authenticated(self, client, test_user_personal, session):
        """로그인 사용자는 통과"""
        @api_login_required
        def dummy_api():
            return {'success': True}

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            result = dummy_api()
            assert result == {'success': True}

    @pytest.mark.unit
    def test_api_login_required_returns_401_json(self, client):
        """비로그인 사용자는 401 JSON 반환"""
        @api_login_required
        def dummy_api():
            return {'success': True}

        with client.application.test_request_context():
            result = dummy_api()
            response, status_code = result
            assert status_code == 401
            data = response.get_json()
            assert data['success'] is False


class TestApiCorporateAccountRequired:
    """@api_corporate_account_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_api_corporate_required_allows_corporate(self, client, test_user_corporate, session):
        """법인 계정은 통과"""
        @api_corporate_account_required
        def dummy_api():
            return {'success': True}

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            result = dummy_api()
            assert result == {'success': True}

    @pytest.mark.unit
    def test_api_corporate_required_returns_403_json(self, client, test_user_personal, session):
        """개인 계정은 403 JSON 반환"""
        @api_corporate_account_required
        def dummy_api():
            return {'success': True}

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            result = dummy_api()
            response, status_code = result
            assert status_code == 403
            data = response.get_json()
            assert data['success'] is False


class TestSuperadminRequired:
    """@superadmin_required 데코레이터 테스트"""

    @pytest.mark.unit
    def test_superadmin_required_allows_superadmin(self, client, test_user_personal, session):
        """슈퍼관리자는 통과"""
        @superadmin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_personal.id
            flask_session[SessionKeys.IS_SUPERADMIN] = True
            result = dummy_view()
            assert result == 'success'

    @pytest.mark.unit
    def test_superadmin_required_rejects_regular_admin(self, client, test_user_corporate, session):
        """일반 관리자는 거부 (abort 403)"""
        @superadmin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            from flask import session as flask_session
            flask_session[SessionKeys.USER_ID] = test_user_corporate.id
            flask_session[SessionKeys.USER_ROLE] = UserRole.ADMIN
            flask_session[SessionKeys.IS_SUPERADMIN] = False
            with pytest.raises(Exception):
                dummy_view()

    @pytest.mark.unit
    def test_superadmin_required_redirects_anonymous(self, client):
        """비로그인 사용자는 로그인 페이지로 리다이렉트"""
        @superadmin_required
        def dummy_view():
            return 'success'

        with client.application.test_request_context():
            result = dummy_view()
            assert result.status_code == 302
            assert 'login' in result.location
