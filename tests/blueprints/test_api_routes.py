"""
API Routes 테스트

Field Registry API 테스트
"""
import pytest
from unittest.mock import patch, Mock


class TestFieldRegistryAPI:
    """Field Registry API 테스트"""

    def test_get_all_sections_requires_login(self, client):
        """섹션 조회 시 로그인 필요"""
        response = client.get('/api/fields/sections')
        assert response.status_code == 302

    def test_get_all_sections_success(self, auth_client_personal_full):
        """모든 섹션 조회 성공"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_section = Mock()
            mock_section.is_visible_for.return_value = True
            mock_registry.get_all_sections.return_value = [mock_section]
            mock_registry.get_js_config.return_value = {'id': 'basic'}

            response = auth_client_personal_full.get('/api/fields/sections')
            assert response.status_code == 200
            assert response.is_json
            data = response.get_json()
            assert 'sections' in data['data']

    def test_get_section_by_id_success(self, auth_client_personal_full):
        """특정 섹션 조회 성공"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_section = Mock()
            mock_section.is_visible_for.return_value = True
            mock_registry.get_section.return_value = mock_section
            mock_registry.get_js_config.return_value = {'id': 'basic'}

            response = auth_client_personal_full.get('/api/fields/sections/basic')
            assert response.status_code == 200
            assert response.is_json

    def test_get_section_not_found(self, auth_client_personal_full):
        """존재하지 않는 섹션 조회"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_registry.get_section.return_value = None

            response = auth_client_personal_full.get('/api/fields/sections/nonexistent')
            assert response.status_code == 404

    def test_get_all_domains_success(self, auth_client_personal_full):
        """모든 도메인 조회 성공"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_registry.get_all_domains.return_value = ['profile', 'employee']

            response = auth_client_personal_full.get('/api/fields/domains')
            assert response.status_code == 200
            assert response.is_json
            data = response.get_json()
            assert 'domains' in data['data']


class TestFieldRegistryAPIFiltering:
    """Field Registry API 필터링 테스트"""

    def test_get_sections_with_account_type_filter(self, auth_client_personal_full):
        """계정 타입 필터링"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_section = Mock()
            mock_section.is_visible_for.return_value = True
            mock_registry.get_all_sections.return_value = [mock_section]
            mock_registry.get_js_config.return_value = {'id': 'basic'}

            response = auth_client_personal_full.get('/api/fields/sections?account_type=personal')
            assert response.status_code == 200

    def test_get_sections_with_domain_filter(self, auth_client_personal_full):
        """도메인 필터링"""
        with patch('app.blueprints.api.FieldRegistry') as mock_registry:
            mock_section = Mock()
            mock_section.is_visible_for.return_value = True
            mock_registry.get_sections_by_domain.return_value = [mock_section]
            mock_registry.get_js_config.return_value = {'id': 'basic'}

            response = auth_client_personal_full.get('/api/fields/sections?domain=profile')
            assert response.status_code == 200

