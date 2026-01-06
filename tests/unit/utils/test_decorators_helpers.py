"""
Decorators 헬퍼 함수 테스트

데코레이터 모듈의 내부 헬퍼 함수 테스트
"""
import pytest
from flask import session
from app.constants.session_keys import SessionKeys, AccountType


class TestCheckLoginHelpers:
    """로그인 체크 헬퍼 함수 테스트"""

    def test_check_login_with_user(self, app):
        """로그인된 사용자 확인"""
        from app.utils.decorators import _check_login
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                result = _check_login()
                assert result is None

    def test_check_login_without_user(self, app):
        """로그인하지 않은 사용자 확인"""
        from app.utils.decorators import _check_login
        
        with app.app_context():
            with app.test_request_context():
                result = _check_login()
                assert result is not None
                assert len(result) == 1

    def test_check_api_login_with_user(self, app):
        """API 로그인 확인 - 로그인됨"""
        from app.utils.decorators import _check_api_login
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                result = _check_api_login()
                assert result is None

    def test_check_api_login_without_user(self, app):
        """API 로그인 확인 - 로그인 안됨"""
        from app.utils.decorators import _check_api_login
        
        with app.app_context():
            with app.test_request_context():
                result = _check_api_login()
                assert result is not None
                assert len(result) == 2
                response, status_code = result
                assert status_code == 401


class TestCheckAccountTypeHelpers:
    """계정 타입 체크 헬퍼 함수 테스트"""

    def test_check_account_type_personal_valid(self, app):
        """개인 계정 확인 - 유효"""
        from app.utils.decorators import _check_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
                result = _check_account_type(AccountType.PERSONAL)
                assert result is None

    def test_check_account_type_personal_invalid(self, app):
        """개인 계정 확인 - 무효"""
        from app.utils.decorators import _check_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
                result = _check_account_type(AccountType.PERSONAL)
                assert result is not None

    def test_check_account_type_corporate_valid(self, app):
        """법인 계정 확인 - 유효"""
        from app.utils.decorators import _check_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
                result = _check_account_type(AccountType.CORPORATE)
                assert result is None

    def test_check_api_account_type_personal_valid(self, app):
        """API 개인 계정 확인 - 유효"""
        from app.utils.decorators import _check_api_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
                result = _check_api_account_type(AccountType.PERSONAL)
                assert result is None

    def test_check_api_account_type_personal_invalid(self, app):
        """API 개인 계정 확인 - 무효"""
        from app.utils.decorators import _check_api_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
                result = _check_api_account_type(AccountType.PERSONAL)
                assert result is not None
                response, status_code = result
                assert status_code == 403

    def test_check_api_account_type_corporate_invalid(self, app):
        """API 법인 계정 확인 - 무효"""
        from app.utils.decorators import _check_api_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
                result = _check_api_account_type(AccountType.CORPORATE)
                assert result is not None
                response, status_code = result
                assert status_code == 403


class TestCheckRoleHelpers:
    """역할 체크 헬퍼 함수 테스트"""

    def test_check_role_valid(self, app):
        """역할 확인 - 유효"""
        from app.utils.decorators import _check_role
        from app.constants.session_keys import UserRole
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ROLE] = UserRole.ADMIN
                result = _check_role(UserRole.ADMIN, UserRole.MANAGER)
                assert result is None

    def test_check_role_invalid(self, app):
        """역할 확인 - 무효"""
        from app.utils.decorators import _check_role
        from app.constants.session_keys import UserRole
        from werkzeug.exceptions import Forbidden
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ROLE] = UserRole.USER
                # abort(403)가 호출되므로 예외가 발생함
                try:
                    result = _check_role(UserRole.ADMIN, UserRole.MANAGER)
                    assert False, "예외가 발생해야 함"
                except Forbidden:
                    pass  # 예상된 동작


class TestDecoratorFunctionality:
    """데코레이터 기능 테스트"""

    def test_login_required_functionality(self, app):
        """login_required 데코레이터 기능"""
        from app.utils.decorators import login_required
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                
                @login_required
                def test_view():
                    return "success"
                
                result = test_view()
                assert result == "success"

    def test_personal_required_functionality(self, app):
        """personal_required 데코레이터 기능 (헬퍼 함수 테스트)"""
        from app.utils.decorators import _check_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
                
                # 헬퍼 함수 직접 테스트
                result = _check_account_type(AccountType.PERSONAL)
                assert result is None

    def test_corporate_required_functionality(self, app):
        """corporate_required 데코레이터 기능 (헬퍼 함수 테스트)"""
        from app.utils.decorators import _check_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
                
                # 헬퍼 함수 직접 테스트
                result = _check_account_type(AccountType.CORPORATE)
                assert result is None


class TestAPIDecorators:
    """API 데코레이터 테스트"""

    def test_api_login_required_functionality(self, app):
        """api_login_required 데코레이터 기능"""
        from app.utils.decorators import api_login_required
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                
                @api_login_required
                def test_api():
                    return {"success": True}
                
                result = test_api()
                assert result == {"success": True}

    def test_api_personal_required_functionality(self, app):
        """api_personal_required 데코레이터 기능 (헬퍼 함수 테스트)"""
        from app.utils.decorators import _check_api_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
                
                # 헬퍼 함수 직접 테스트
                result = _check_api_account_type(AccountType.PERSONAL)
                assert result is None

    def test_api_corporate_required_functionality(self, app):
        """api_corporate_required 데코레이터 기능 (헬퍼 함수 테스트)"""
        from app.utils.decorators import _check_api_account_type
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
                
                # 헬퍼 함수 직접 테스트
                result = _check_api_account_type(AccountType.CORPORATE)
                assert result is None


class TestRoleDecorators:
    """역할 데코레이터 테스트"""

    def test_role_required_single(self, app):
        """단일 역할 필요"""
        from app.utils.decorators import role_required
        from app.constants.session_keys import UserRole
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                session[SessionKeys.USER_ROLE] = UserRole.ADMIN
                
                @role_required(UserRole.ADMIN)
                def test_view():
                    return "success"
                
                result = test_view()
                assert result == "success"

    def test_role_required_multiple(self, app):
        """다중 역할 허용"""
        from app.utils.decorators import role_required
        from app.constants.session_keys import UserRole
        
        with app.app_context():
            with app.test_request_context():
                session[SessionKeys.USER_ID] = 1
                session[SessionKeys.USER_ROLE] = UserRole.MANAGER
                
                @role_required(UserRole.ADMIN, UserRole.MANAGER)
                def test_view():
                    return "success"
                
                result = test_view()
                assert result == "success"

