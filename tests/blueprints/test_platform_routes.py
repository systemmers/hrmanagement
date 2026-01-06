"""
Platform Routes 테스트

플랫폼 관리자 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock


class TestPlatformCompanies:
    """플랫폼 법인 관리 테스트"""

    def test_companies_list_requires_superadmin(self, client):
        """법인 목록 접근 시 슈퍼관리자 권한 필요"""
        response = client.get('/platform/companies')
        assert response.status_code == 302

    def test_companies_list_renders(self, auth_client_corporate_full):
        """법인 목록 렌더링"""
        from app.services.platform_service import platform_service
        from app.shared.constants.session_keys import SessionKeys
        from unittest.mock import Mock
        
        mock_pagination = Mock()
        mock_pagination.total = 1
        mock_pagination.pages = 1
        mock_pagination.page = 1
        mock_pagination.per_page = 20
        mock_pagination.has_prev = False
        mock_pagination.has_next = False
        
        with patch.object(platform_service, 'get_companies_paginated') as mock_get:
            mock_get.return_value = ([Mock(id=1, name='테스트법인')], mock_pagination)

            # 슈퍼관리자 권한 설정
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.IS_SUPERADMIN] = True

            response = auth_client_corporate_full.get('/platform/companies')
            assert response.status_code == 200

    def test_company_detail_renders(self, auth_client_corporate_full):
        """법인 상세 페이지 렌더링"""
        from app.services.platform_service import platform_service
        from app.shared.constants.session_keys import SessionKeys
        from unittest.mock import Mock
        
        with patch.object(platform_service, 'get_company_by_id') as mock_get_company, \
             patch.object(platform_service, 'get_users_by_company') as mock_get_users:
            mock_get_company.return_value = Mock(id=1, name='테스트법인')
            mock_get_users.return_value = []

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.IS_SUPERADMIN] = True

            response = auth_client_corporate_full.get('/platform/companies/1')
            assert response.status_code == 200

    def test_company_detail_not_found(self, auth_client_corporate_full):
        """존재하지 않는 법인 조회"""
        from app.services.platform_service import platform_service
        from app.shared.constants.session_keys import SessionKeys
        
        with patch.object(platform_service, 'get_company_by_id', return_value=None):
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.IS_SUPERADMIN] = True

            response = auth_client_corporate_full.get('/platform/companies/999')
            assert response.status_code == 404

    def test_toggle_company_active_success(self, auth_client_corporate_full):
        """법인 활성화/비활성화 토글 성공"""
        from app.services.platform_service import platform_service
        from app.shared.constants.session_keys import SessionKeys
        
        with patch.object(platform_service, 'toggle_company_active', return_value=(True, None, True)):
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.IS_SUPERADMIN] = True

            response = auth_client_corporate_full.post('/platform/api/companies/1/toggle-active')
            assert response.status_code == 200
            assert response.is_json

    def test_toggle_company_active_failure(self, auth_client_corporate_full):
        """법인 활성화/비활성화 토글 실패"""
        from app.services.platform_service import platform_service
        from app.shared.constants.session_keys import SessionKeys
        
        with patch.object(platform_service, 'toggle_company_active', return_value=(False, '에러', None)):
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.IS_SUPERADMIN] = True

            response = auth_client_corporate_full.post('/platform/api/companies/1/toggle-active')
            assert response.status_code == 400

