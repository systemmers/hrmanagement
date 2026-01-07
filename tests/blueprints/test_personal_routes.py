"""
Personal Routes 테스트

개인 프로필 CRUD 라우트 테스트
"""
import pytest
from flask import session
from unittest.mock import patch, Mock

from app.shared.constants.session_keys import SessionKeys


class TestPersonalDashboard:
    """개인 대시보드 테스트"""

    def test_dashboard_requires_login(self, client):
        """대시보드 접근 시 로그인 필요"""
        response = client.get('/personal/dashboard')
        assert response.status_code == 302  # 리다이렉트

    def test_dashboard_renders(self, auth_client_personal_full, test_user_personal):
        """대시보드 렌더링"""
        from app.domains.user.services.personal_service import personal_service
        with patch.object(personal_service, 'get_dashboard_data') as mock_get_data:
            mock_get_data.return_value = {
                'user': test_user_personal,
                'profile': {'name': '홍길동'},
                'stats': {}
            }
            response = auth_client_personal_full.get('/personal/dashboard')
            assert response.status_code == 200


class TestPersonalProfileView:
    """개인 프로필 조회 테스트"""

    def test_profile_view_requires_login(self, client):
        """프로필 조회 시 로그인 필요"""
        response = client.get('/personal/profile')
        assert response.status_code == 302

    def test_profile_view_renders(self, auth_client_personal_full):
        """프로필 조회 렌더링 - 리다이렉트 확인"""
        response = auth_client_personal_full.get('/personal/profile', follow_redirects=False)
        assert response.status_code == 301  # profile.view로 리다이렉트


class TestPersonalProfileEdit:
    """개인 프로필 수정 테스트"""

    def test_profile_edit_get(self, auth_client_personal_full):
        """프로필 수정 페이지 GET - 리다이렉트 확인"""
        response = auth_client_personal_full.get('/personal/profile/edit', follow_redirects=False)
        assert response.status_code == 301  # profile.edit으로 리다이렉트

    def test_profile_edit_post_success(self, auth_client_personal_full, test_user_personal):
        """프로필 수정 POST 성공"""
        from app.domains.user.services.personal_service import personal_service
        from app.models import PersonalProfile
        from app.shared.base.service_result import ServiceResult
        from unittest.mock import MagicMock
        
        mock_profile = MagicMock(spec=PersonalProfile)
        mock_profile.photo = None
        mock_profile.id = 1
        
        with patch.object(personal_service, 'get_user_with_profile') as mock_get_user, \
             patch.object(personal_service, 'ensure_profile_exists') as mock_ensure, \
             patch.object(personal_service, 'update_profile') as mock_update, \
             patch('app.domains.user.blueprints.personal.routes.handle_photo_upload') as mock_photo, \
             patch('app.domains.user.blueprints.personal.routes.extract_profile_data') as mock_extract, \
             patch('app.domains.user.blueprints.personal.routes.update_profile_relations') as mock_update_relations:
            mock_get_user.return_value = (test_user_personal, mock_profile)
            mock_ensure.return_value = mock_profile
            mock_photo.return_value = (None, None)
            mock_extract.return_value = {}
            mock_update.return_value = ServiceResult.ok()
            mock_update_relations.return_value = None

            response = auth_client_personal_full.post('/personal/profile/edit', data={
                'name': '수정된이름',
                'email': 'updated@test.com'
            }, follow_redirects=False)

            assert response.status_code in [200, 302]  # 리다이렉트 또는 성공


class TestPersonalPhotoUpload:
    """개인 프로필 사진 업로드 테스트"""

    def test_photo_upload_invalid_file(self, auth_client_personal_full, test_user_personal):
        """잘못된 파일 형식 업로드"""
        from app.domains.user.services.personal_service import personal_service
        from app.models import PersonalProfile
        from app.shared.base.service_result import ServiceResult
        from unittest.mock import MagicMock
        
        mock_profile = MagicMock(spec=PersonalProfile)
        mock_profile.photo = None
        mock_profile.id = 1
        
        with patch.object(personal_service, 'get_user_with_profile') as mock_get_user, \
             patch.object(personal_service, 'ensure_profile_exists') as mock_ensure, \
             patch.object(personal_service, 'update_profile') as mock_update, \
             patch('app.domains.user.blueprints.personal.routes.handle_photo_upload') as mock_photo, \
             patch('app.domains.user.blueprints.personal.routes.extract_profile_data') as mock_extract, \
             patch('app.domains.user.blueprints.personal.routes.update_profile_relations') as mock_update_relations:
            mock_get_user.return_value = (test_user_personal, mock_profile)
            mock_ensure.return_value = mock_profile
            mock_photo.return_value = (None, 'Invalid file type')
            mock_extract.return_value = {}
            mock_update.return_value = ServiceResult.ok()
            mock_update_relations.return_value = None
            
            from io import BytesIO
            data = {
                'photoFile': (BytesIO(b'fake image'), 'test.exe')
            }
            response = auth_client_personal_full.post('/personal/profile/edit', data=data, content_type='multipart/form-data')
            assert response.status_code in [200, 302, 400]

