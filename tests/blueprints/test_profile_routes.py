"""
Profile Routes 테스트

통합 프로필 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.shared.constants.session_keys import SessionKeys, AccountType


class TestProfileDashboard:
    """통합 프로필 대시보드 테스트"""

    def test_dashboard_requires_login(self, client):
        """대시보드 접근 시 로그인 필요"""
        response = client.get('/profile/dashboard')
        assert response.status_code == 302

    def test_dashboard_personal_redirect(self, auth_client_personal_full):
        """개인 계정은 personal 대시보드로 리다이렉트"""
        response = auth_client_personal_full.get('/profile/dashboard', follow_redirects=False)
        assert response.status_code == 302
        assert 'personal' in response.location

    def test_dashboard_employee_renders(self, auth_client_corporate_full, test_employee):
        """법인 직원 대시보드 렌더링"""
        from app.domains.employee.services import employee_service
        with patch.object(employee_service, 'get_dashboard_data') as mock_get_data:
            mock_get_data.return_value = {
                'employee': {'name': '홍길동'},
                'stats': {},
                'work_info': {}
            }
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.EMPLOYEE_ID] = test_employee.id
                sess[SessionKeys.ACCOUNT_TYPE] = 'employee_sub'

            response = auth_client_corporate_full.get('/profile/dashboard')
            assert response.status_code == 200


class TestProfileView:
    """통합 프로필 조회 테스트"""

    def test_profile_view_requires_login(self, client):
        """프로필 조회 시 로그인 필요"""
        response = client.get('/profile/')
        assert response.status_code == 302

    def test_profile_view_renders(self, auth_client_personal_full, test_user_personal, session):
        """프로필 조회 렌더링"""
        from app.models import PersonalProfile
        from app.domains.employee.models import Profile
        
        # 프로필 생성
        profile = Profile(
            name='홍길동',
            user_id=test_user_personal.id
        )
        session.add(profile)
        session.commit()
        
        response = auth_client_personal_full.get('/profile/')
        assert response.status_code == 200


class TestProfileEdit:
    """통합 프로필 수정 테스트"""

    def test_profile_edit_get(self, auth_client_personal_full, test_user_personal, session):
        """프로필 수정 페이지 GET"""
        from app.domains.employee.models import Profile
        
        # 프로필 생성
        profile = Profile(
            name='홍길동',
            user_id=test_user_personal.id
        )
        session.add(profile)
        session.commit()
        
        response = auth_client_personal_full.get('/profile/edit')
        assert response.status_code == 200

    def test_profile_edit_post_success(self, auth_client_personal_full, test_user_personal, session):
        """프로필 수정 POST 성공"""
        from app.domains.employee.models import Profile
        
        # 프로필 생성
        profile = Profile(
            name='홍길동',
            user_id=test_user_personal.id
        )
        session.add(profile)
        session.commit()
        
        response = auth_client_personal_full.post('/profile/edit', data={
            'name': '수정된이름'
        }, follow_redirects=False)

        assert response.status_code in [200, 302]


class TestProfileGetSection:
    """프로필 섹션 조회 API 테스트"""

    def test_get_section_api(self, auth_client_personal_full, test_user_personal, session):
        """섹션 조회 API"""
        from app.domains.employee.models import Profile
        
        # 프로필 생성
        profile = Profile(
            name='홍길동',
            user_id=test_user_personal.id
        )
        session.add(profile)
        session.commit()
        
        response = auth_client_personal_full.get('/profile/section/basic')
        assert response.status_code == 200

