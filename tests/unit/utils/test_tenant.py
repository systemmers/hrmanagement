"""
Tenant Utils 테스트

멀티테넌시 유틸리티 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.shared.utils.tenant import (
    get_current_company_id,
    get_current_company,
    get_current_organization_id,
    get_current_user_id,
    get_current_account_type,
    is_corporate_account,
    is_personal_account
)
from app.shared.constants.session_keys import SessionKeys, AccountType


class TestGetCurrentCompanyId:
    """get_current_company_id 테스트"""

    def test_get_current_company_id_with_session(self, auth_client_corporate_full):
        """세션에 회사 ID가 있을 때"""
        with auth_client_corporate_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.COMPANY_ID] = 1
            assert get_current_company_id() == 1

    def test_get_current_company_id_no_session(self, client):
        """세션에 회사 ID가 없을 때"""
        with client.application.app_context():
            assert get_current_company_id() is None


class TestGetCurrentCompany:
    """get_current_company 테스트"""

    def test_get_current_company_with_session(self, auth_client_corporate_full, test_company):
        """세션에 회사가 있을 때"""
        with auth_client_corporate_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.COMPANY_ID] = test_company.id
            company = get_current_company()
            assert company is not None
            assert company.id == test_company.id

    def test_get_current_company_caching(self, auth_client_corporate_full, test_company):
        """요청 스코프 캐싱 확인"""
        with auth_client_corporate_full.session_transaction() as sess:
            sess[SessionKeys.COMPANY_ID] = test_company.id

        with auth_client_corporate_full.application.app_context():
            company1 = get_current_company()
            company2 = get_current_company()
            assert company1 is company2  # 같은 객체 반환 (캐싱)


class TestGetCurrentOrganizationId:
    """get_current_organization_id 테스트"""

    def test_get_current_organization_id_with_company(self, auth_client_corporate_full, test_company):
        """회사에 조직 ID가 있을 때"""
        with auth_client_corporate_full.session_transaction() as sess:
            sess[SessionKeys.COMPANY_ID] = test_company.id

        with patch('app.shared.utils.tenant.get_current_company') as mock_get:
            mock_company = Mock()
            mock_company.root_organization_id = 10
            mock_get.return_value = mock_company

            org_id = get_current_organization_id()
            assert org_id == 10

    def test_get_current_organization_id_no_company(self, client):
        """회사가 없을 때"""
        assert get_current_organization_id() is None


class TestGetCurrentUserId:
    """get_current_user_id 테스트"""

    def test_get_current_user_id_with_session(self, auth_client_personal_full):
        """세션에 사용자 ID가 있을 때"""
        with auth_client_personal_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.USER_ID] = 1
            assert get_current_user_id() == 1

    def test_get_current_user_id_no_session(self, client):
        """세션에 사용자 ID가 없을 때"""
        with client.application.app_context():
            assert get_current_user_id() is None


class TestGetCurrentAccountType:
    """get_current_account_type 테스트"""

    def test_get_current_account_type_personal(self, auth_client_personal_full):
        """개인 계정 타입"""
        with auth_client_personal_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            assert get_current_account_type() == AccountType.PERSONAL

    def test_get_current_account_type_corporate(self, auth_client_corporate_full):
        """법인 계정 타입"""
        with auth_client_corporate_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            assert get_current_account_type() == AccountType.CORPORATE

    def test_get_current_account_type_no_session(self, client):
        """세션에 계정 타입이 없을 때"""
        with client.application.app_context():
            assert get_current_account_type() is None


class TestIsCorporateAccount:
    """is_corporate_account 테스트"""

    def test_is_corporate_account_true(self, auth_client_corporate_full):
        """법인 계정일 때"""
        with auth_client_corporate_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            assert is_corporate_account() is True

    def test_is_corporate_account_false(self, auth_client_personal_full):
        """법인 계정이 아닐 때"""
        with auth_client_personal_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            assert is_corporate_account() is False


class TestIsPersonalAccount:
    """is_personal_account 테스트"""

    def test_is_personal_account_true(self, auth_client_personal_full):
        """개인 계정일 때"""
        with auth_client_personal_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.PERSONAL
            assert is_personal_account() is True

    def test_is_personal_account_false(self, auth_client_corporate_full):
        """개인 계정이 아닐 때"""
        with auth_client_corporate_full.application.test_request_context() as ctx:
            from flask import session
            session[SessionKeys.ACCOUNT_TYPE] = AccountType.CORPORATE
            assert is_personal_account() is False

