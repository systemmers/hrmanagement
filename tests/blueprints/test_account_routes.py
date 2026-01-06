"""
Account Routes 테스트

계정 관리 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.constants.session_keys import SessionKeys


class TestAccountSettings:
    """계정 설정 테스트"""

    def test_settings_requires_login(self, client):
        """설정 페이지 접근 시 로그인 필요"""
        response = client.get('/account/settings')
        assert response.status_code == 302

    def test_settings_renders(self, auth_client_personal_full):
        """설정 페이지 렌더링"""
        with patch('app.blueprints.account.routes.user_service') as mock_service, \
             patch('app.blueprints.account.routes.employee_service') as mock_emp_service:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.employee_id = None  # 명시적으로 None 설정
            mock_service.get_model_by_id.return_value = mock_user

            response = auth_client_personal_full.get('/account/settings')
            assert response.status_code == 200


class TestAccountPassword:
    """비밀번호 변경 테스트"""

    def test_password_change_get(self, auth_client_personal_full):
        """비밀번호 변경 페이지 GET"""
        response = auth_client_personal_full.get('/account/password')
        assert response.status_code == 200

    def test_password_change_post_success(self, auth_client_personal_full):
        """비밀번호 변경 POST 성공"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.authenticate.return_value = Mock(id=1)
            mock_service.update_password.return_value = True

            with auth_client_personal_full.session_transaction() as sess:
                sess[SessionKeys.USER_ID] = 1
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/password', data={
                'current_password': 'oldpass',
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123'
            }, follow_redirects=False)

            assert response.status_code == 302

    def test_password_change_mismatch(self, auth_client_personal_full):
        """비밀번호 불일치"""
        response = auth_client_personal_full.post('/account/password', data={
            'current_password': 'oldpass',
            'new_password': 'newpassword123',
            'confirm_password': 'differentpass'
        })

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert '일치하지 않습니다' in response_text


class TestAccountPrivacy:
    """개인정보 공개 설정 테스트"""

    def test_privacy_get(self, auth_client_personal_full):
        """공개 설정 페이지 GET"""
        with patch('app.blueprints.account.routes.user_service') as mock_service, \
             patch('app.blueprints.account.routes.personal_service') as mock_personal:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.get_privacy_settings.return_value = {}
            mock_personal.get_user_with_profile.return_value = (mock_user, Mock())

            response = auth_client_personal_full.get('/account/privacy')
            assert response.status_code == 200

    def test_privacy_post_success(self, auth_client_personal_full):
        """공개 설정 저장 성공"""
        with patch('app.blueprints.account.routes.user_service') as mock_service, \
             patch('app.blueprints.account.routes.personal_service') as mock_personal:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.update_privacy_settings.return_value = True
            mock_personal.get_user_with_profile.return_value = (mock_user, Mock())
            mock_personal.update_profile.return_value = True

            response = auth_client_personal_full.post('/account/privacy', data={
                'show_email': 'on',
                'is_public': 'on'
            }, follow_redirects=False)

            assert response.status_code == 302


class TestAccountDelete:
    """계정 탈퇴 테스트"""

    def test_delete_get(self, auth_client_personal_full):
        """계정 탈퇴 페이지 GET"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user

            response = auth_client_personal_full.get('/account/delete')
            assert response.status_code == 200

    def test_delete_post_success(self, auth_client_personal_full):
        """계정 탈퇴 POST 성공"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.authenticate.return_value = mock_user
            mock_service.deactivate.return_value = True

            with auth_client_personal_full.session_transaction() as sess:
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/delete', data={
                'password': 'test1234',
                'confirm_text': '계정 탈퇴'
            }, follow_redirects=False)

            assert response.status_code == 302
            assert 'login' in response.location

    def test_delete_post_wrong_password(self, auth_client_personal_full):
        """계정 탈퇴 - 잘못된 비밀번호"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.authenticate.return_value = None

            with auth_client_personal_full.session_transaction() as sess:
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/delete', data={
                'password': 'wrongpassword',
                'confirm_text': '계정 탈퇴'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '올바르지 않습니다' in response_text

    def test_delete_post_wrong_confirm_text(self, auth_client_personal_full):
        """계정 탈퇴 - 잘못된 확인 텍스트"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.authenticate.return_value = mock_user

            with auth_client_personal_full.session_transaction() as sess:
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/delete', data={
                'password': 'test1234',
                'confirm_text': '잘못된 텍스트'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '정확히 입력해주세요' in response_text

    def test_delete_user_not_found(self, auth_client_personal_full):
        """계정 탈퇴 - 사용자 없음"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.get_model_by_id.return_value = None

            response = auth_client_personal_full.get('/account/delete', follow_redirects=False)
            assert response.status_code == 302
            assert 'main.index' in response.location or '/' in response.location


class TestAccountSettingsEdgeCases:
    """계정 설정 엣지 케이스 테스트"""

    def test_settings_user_not_found(self, auth_client_personal_full):
        """설정 페이지 - 사용자 없음"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.get_model_by_id.return_value = None

            response = auth_client_personal_full.get('/account/settings', follow_redirects=False)
            assert response.status_code == 302

    def test_settings_with_employee(self, auth_client_personal_full):
        """설정 페이지 - 직원 연결된 경우"""
        with patch('app.blueprints.account.routes.user_service') as mock_user_service, \
             patch('app.blueprints.account.routes.employee_service') as mock_emp_service:
            mock_user = Mock()
            mock_user.id = 1
            mock_user.employee_id = 1
            mock_user_service.get_model_by_id.return_value = mock_user
            
            mock_employee = Mock()
            mock_emp_service.get_employee_by_id.return_value = mock_employee

            response = auth_client_personal_full.get('/account/settings')
            assert response.status_code == 200
            mock_emp_service.get_employee_by_id.assert_called_once_with(1)


class TestAccountPasswordEdgeCases:
    """비밀번호 변경 엣지 케이스 테스트"""

    def test_password_change_missing_fields(self, auth_client_personal_full):
        """비밀번호 변경 - 필수 필드 누락"""
        response = auth_client_personal_full.post('/account/password', data={
            'current_password': '',
            'new_password': '',
            'confirm_password': ''
        })

        assert response.status_code == 200
        response_text = response.data.decode('utf-8', errors='ignore')
        assert '모든 필드를 입력해주세요' in response_text

    def test_password_change_short_password(self, auth_client_personal_full):
        """비밀번호 변경 - 짧은 비밀번호"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.authenticate.return_value = Mock(id=1)

            with auth_client_personal_full.session_transaction() as sess:
                sess[SessionKeys.USER_ID] = 1
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/password', data={
                'current_password': 'oldpass',
                'new_password': 'short',
                'confirm_password': 'short'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '8자 이상' in response_text

    def test_password_change_wrong_current_password(self, auth_client_personal_full):
        """비밀번호 변경 - 현재 비밀번호 불일치"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.authenticate.return_value = None

            with auth_client_personal_full.session_transaction() as sess:
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/password', data={
                'current_password': 'wrongpass',
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '올바르지 않습니다' in response_text

    def test_password_change_update_failed(self, auth_client_personal_full):
        """비밀번호 변경 - 업데이트 실패"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.authenticate.return_value = Mock(id=1)
            mock_service.update_password.return_value = False

            with auth_client_personal_full.session_transaction() as sess:
                sess[SessionKeys.USER_ID] = 1
                sess['username'] = 'testuser'

            response = auth_client_personal_full.post('/account/password', data={
                'current_password': 'oldpass',
                'new_password': 'newpassword123',
                'confirm_password': 'newpassword123'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '실패했습니다' in response_text


class TestAccountPrivacyEdgeCases:
    """개인정보 공개 설정 엣지 케이스 테스트"""

    def test_privacy_user_not_found(self, auth_client_personal_full):
        """공개 설정 - 사용자 없음"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_service.get_model_by_id.return_value = None

            response = auth_client_personal_full.get('/account/privacy', follow_redirects=False)
            assert response.status_code == 302

    def test_privacy_update_failed(self, auth_client_personal_full):
        """공개 설정 저장 실패"""
        with patch('app.blueprints.account.routes.user_service') as mock_service, \
             patch('app.blueprints.account.routes.personal_service') as mock_personal:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.update_privacy_settings.return_value = False
            mock_personal.get_user_with_profile.return_value = (mock_user, Mock())

            response = auth_client_personal_full.post('/account/privacy', data={
                'show_email': 'on'
            })

            assert response.status_code == 200
            response_text = response.data.decode('utf-8', errors='ignore')
            assert '실패했습니다' in response_text

    def test_privacy_corporate_account(self, auth_client_corporate_full):
        """법인 계정 공개 설정"""
        with patch('app.blueprints.account.routes.user_service') as mock_service:
            mock_user = Mock()
            mock_service.get_model_by_id.return_value = mock_user
            mock_service.get_privacy_settings.return_value = {}

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.ACCOUNT_TYPE] = 'corporate'

            response = auth_client_corporate_full.get('/account/privacy')
            assert response.status_code == 200

