"""
Corporate Routes 확장 테스트

법인 등록/관리 라우트 추가 테스트
Phase 2 Migration: 도메인 경로로 patch 경로 업데이트
"""
import pytest
from unittest.mock import patch, Mock


class TestCorporateRegister:
    """법인 등록 테스트"""

    def test_register_get(self, client):
        """법인 등록 페이지 GET"""
        response = client.get('/corporate/register')
        assert response.status_code == 200

    def test_register_post_success(self, client, session):
        """법인 등록 POST 성공"""
        from app.shared.utils.corporate_helpers import create_company_entities
        from app.models.user import User

        with patch('app.domains.company.blueprints.corporate.create_company_entities', return_value=None):
            response = client.post('/corporate/register', data={
                'company_name': '테스트법인',
                'business_number': '1234567890',
                'representative': '홍길동',
                'admin_email': 'test@test.com',
                'admin_username': 'testadmin',
                'admin_password': 'password123',
                'confirm_password': 'password123',
                'phone': '02-1234-5678',
                'address': '서울시 강남구'
            }, follow_redirects=False)

            assert response.status_code in [200, 302]

    def test_register_post_validation_error(self, client):
        """법인 등록 POST 검증 실패"""
        response = client.post('/corporate/register', data={
            'name': '',
            'business_number': '123'
        })

        assert response.status_code == 200


class TestCorporateDashboard:
    """법인 대시보드 테스트"""

    def test_dashboard_requires_login(self, client):
        """대시보드 접근 시 로그인 필요"""
        response = client.get('/corporate/dashboard')
        assert response.status_code == 302

    def test_dashboard_renders(self, auth_client_corporate_full, test_company):
        """대시보드 렌더링"""
        from app.services.company_service import company_service
        from app.shared.constants.session_keys import SessionKeys

        with patch.object(company_service, 'get_with_stats') as mock_get:
            mock_get.return_value = test_company

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.COMPANY_ID] = test_company.id

            response = auth_client_corporate_full.get('/corporate/dashboard')
            assert response.status_code == 200
