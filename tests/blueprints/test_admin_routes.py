"""
Admin Routes 테스트

관리자 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock


class TestAdminAudit:
    """감사 로그 테스트"""

    def test_audit_logs_requires_admin(self, client):
        """감사 로그 접근 시 관리자 권한 필요"""
        response = client.get('/admin/audit')
        assert response.status_code == 302

    def test_audit_logs_renders(self, auth_client_corporate_full):
        """감사 로그 페이지 렌더링"""
        from app.shared.constants.session_keys import SessionKeys, UserRole
        
        with auth_client_corporate_full.session_transaction() as sess:
            sess[SessionKeys.USER_ROLE] = UserRole.ADMIN

        response = auth_client_corporate_full.get('/admin/audit')
        assert response.status_code == 200


class TestAdminOrganization:
    """조직 관리 테스트"""

    def test_organization_requires_admin(self, client):
        """조직 관리 접근 시 관리자 권한 필요"""
        response = client.get('/admin/organizations')
        assert response.status_code == 302

    def test_organization_renders(self, auth_client_corporate_full, test_company):
        """조직 관리 페이지 렌더링"""
        from app.shared.constants.session_keys import SessionKeys, UserRole
        from app.domains.company.services.organization_service import organization_service
        from app.domains.company.services.company_service import company_service
        
        with patch.object(company_service, 'get_by_id') as mock_get_company, \
             patch.object(organization_service, 'get_tree') as mock_tree, \
             patch.object(organization_service, 'get_flat_list') as mock_flat, \
             patch.object(organization_service, 'get_organization_statistics') as mock_stats:
            mock_get_company.return_value = test_company
            mock_tree.return_value = []
            mock_flat.return_value = []
            mock_stats.return_value = {
                'by_type': {'company': 0, 'department': 0, 'team': 0},
                'total': 0
            }
            
            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.USER_ROLE] = UserRole.ADMIN
                sess[SessionKeys.COMPANY_ID] = test_company.id

            response = auth_client_corporate_full.get('/admin/organizations')
            assert response.status_code == 200

