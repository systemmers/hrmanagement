"""
Auth Blueprint 테스트

로그인, 로그아웃, 회원가입, 비밀번호 변경 테스트
"""
import pytest
from flask import session

from app.shared.constants.session_keys import SessionKeys
from app.models.user import User


class TestLogin:
    """로그인 기능 테스트"""

    def test_login_page_renders(self, client):
        """로그인 페이지 렌더링 테스트"""
        response = client.get('/auth/login')
        assert response.status_code == 200
        assert b'login' in response.data.lower() or 'login' in response.data.decode('utf-8').lower()

    def test_login_success(self, client, test_user_personal):
        """로그인 성공 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testpersonal',
            'password': 'test1234'
        }, follow_redirects=False)

        # 로그인 성공 시 리다이렉트
        assert response.status_code == 302

        # 세션에 사용자 정보 저장 확인
        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ID) == test_user_personal.id
            assert sess.get(SessionKeys.USERNAME) == 'testpersonal'

    def test_login_success_redirect_to_index(self, client, test_user_personal):
        """로그인 성공 후 리다이렉트 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testpersonal',
            'password': 'test1234'
        }, follow_redirects=False)

        # 로그인 성공 시 리다이렉트 발생 (메인 또는 프로필 완성 페이지)
        assert response.status_code == 302
        # 리다이렉트 대상이 적절한 경로인지 확인
        assert response.location in ['/', '/main/', '/personal/profile/edit'] or \
               'main' in response.location or 'profile' in response.location

    def test_login_failure_invalid_password(self, client, test_user_personal):
        """잘못된 비밀번호 로그인 실패 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testpersonal',
            'password': 'wrongpassword'
        }, follow_redirects=True)

        assert response.status_code == 200
        # 에러 메시지 표시 (로그인 페이지에 남아있음)
        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ID) is None

    def test_login_failure_invalid_username(self, client):
        """존재하지 않는 사용자 로그인 실패 테스트"""
        response = client.post('/auth/login', data={
            'username': 'nonexistent',
            'password': 'test1234'
        }, follow_redirects=True)

        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ID) is None

    def test_login_failure_empty_fields(self, client):
        """빈 필드 로그인 실패 테스트"""
        response = client.post('/auth/login', data={
            'username': '',
            'password': ''
        }, follow_redirects=True)

        assert response.status_code == 200
        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ID) is None

    def test_login_redirect_when_already_logged_in(self, client, test_user_personal):
        """이미 로그인된 상태에서 로그인 페이지 접근 시 리다이렉트 테스트"""
        # 먼저 로그인
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id

        response = client.get('/auth/login', follow_redirects=False)

        assert response.status_code == 302  # 리다이렉트

    def test_login_with_next_parameter(self, client, test_user_personal):
        """next 파라미터를 통한 리다이렉트 테스트"""
        response = client.post('/auth/login?next=/employees', data={
            'username': 'testpersonal',
            'password': 'test1234'
        }, follow_redirects=False)

        assert response.status_code == 302
        assert '/employees' in response.location or 'main' in response.location.lower()


class TestLogout:
    """로그아웃 기능 테스트"""

    def test_logout_clears_session(self, client, test_user_personal):
        """로그아웃 시 세션 초기화 테스트"""
        # 먼저 로그인
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.get('/auth/logout', follow_redirects=False)

        assert response.status_code == 302

        # 세션 클리어 확인
        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ID) is None
            assert sess.get(SessionKeys.USERNAME) is None

    def test_logout_redirects_to_login(self, client, test_user_personal):
        """로그아웃 후 로그인 페이지로 리다이렉트 테스트"""
        # 먼저 로그인
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id

        response = client.get('/auth/logout', follow_redirects=False)

        assert response.status_code == 302
        assert 'login' in response.location


class TestRegister:
    """회원가입 페이지 테스트"""

    def test_register_page_renders(self, client):
        """회원가입 유형 선택 페이지 렌더링 테스트"""
        response = client.get('/auth/register')
        assert response.status_code == 200

    def test_register_redirect_when_logged_in(self, client, test_user_personal):
        """로그인 상태에서 회원가입 페이지 접근 시 리다이렉트 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id

        response = client.get('/auth/register', follow_redirects=False)

        assert response.status_code == 302


class TestChangePassword:
    """비밀번호 변경 기능 테스트"""

    def test_change_password_page_requires_login(self, client):
        """비밀번호 변경 페이지 로그인 필요 테스트"""
        response = client.get('/auth/change-password', follow_redirects=False)

        assert response.status_code == 302
        assert 'login' in response.location

    def test_change_password_page_renders_when_logged_in(self, client, test_user_personal):
        """로그인 상태에서 비밀번호 변경 페이지 렌더링 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.get('/auth/change-password')
        assert response.status_code == 200

    def test_change_password_success(self, client, session, test_user_personal):
        """비밀번호 변경 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.post('/auth/change-password', data={
            'current_password': 'test1234',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=False)

        assert response.status_code == 302  # 성공 시 리다이렉트

    def test_change_password_failure_wrong_current(self, client, test_user_personal):
        """현재 비밀번호 불일치 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.post('/auth/change-password', data={
            'current_password': 'wrongpassword',
            'new_password': 'newpassword123',
            'confirm_password': 'newpassword123'
        }, follow_redirects=True)

        assert response.status_code == 200  # 변경 페이지에 남아있음

    def test_change_password_failure_mismatch(self, client, test_user_personal):
        """새 비밀번호 확인 불일치 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.post('/auth/change-password', data={
            'current_password': 'test1234',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpassword'
        }, follow_redirects=True)

        assert response.status_code == 200  # 변경 페이지에 남아있음

    def test_change_password_failure_too_short(self, client, test_user_personal):
        """비밀번호 길이 부족 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.post('/auth/change-password', data={
            'current_password': 'test1234',
            'new_password': 'short',
            'confirm_password': 'short'
        }, follow_redirects=True)

        assert response.status_code == 200  # 변경 페이지에 남아있음

    def test_change_password_failure_empty_fields(self, client, test_user_personal):
        """빈 필드 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = 'testpersonal'

        response = client.post('/auth/change-password', data={
            'current_password': '',
            'new_password': '',
            'confirm_password': ''
        }, follow_redirects=True)

        assert response.status_code == 200  # 변경 페이지에 남아있음


class TestSessionHandling:
    """세션 관리 테스트"""

    def test_session_stores_account_type(self, client, test_user_personal):
        """세션에 계정 타입 저장 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testpersonal',
            'password': 'test1234'
        }, follow_redirects=False)

        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.ACCOUNT_TYPE) == User.ACCOUNT_PERSONAL

    def test_session_stores_company_id_for_corporate(self, client, test_user_corporate):
        """법인 계정 로그인 시 company_id 저장 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testcorporate',
            'password': 'admin1234'
        }, follow_redirects=False)

        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.COMPANY_ID) is not None

    def test_session_stores_user_role(self, client, test_user_corporate):
        """세션에 사용자 역할 저장 테스트"""
        response = client.post('/auth/login', data={
            'username': 'testcorporate',
            'password': 'admin1234'
        }, follow_redirects=False)

        with client.session_transaction() as sess:
            assert sess.get(SessionKeys.USER_ROLE) == User.ROLE_ADMIN
