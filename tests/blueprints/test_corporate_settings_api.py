"""
Corporate Settings API 테스트

법인 설정 API 테스트
"""
import pytest
from unittest.mock import patch, Mock


class TestCorporateSettingsAPI:
    """법인 설정 API 테스트"""

    def test_get_settings_requires_auth(self, client):
        """설정 조회 시 인증 필요"""
        response = client.get('/api/corporate/settings')
        assert response.status_code == 302

    def test_get_settings_success(self, auth_client_corporate_full):
        """설정 조회 성공"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.get_settings.return_value = {'key1': 'value1'}

            response = auth_client_corporate_full.get('/api/corporate/settings')
            assert response.status_code == 200
            assert response.is_json

    def test_update_settings_success(self, auth_client_corporate_full):
        """설정 업데이트 성공"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.update_settings.return_value = [{'key': 'key1'}]

            response = auth_client_corporate_full.put(
                '/api/corporate/settings',
                json={'key1': 'value1'},
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_get_setting_by_key_success(self, auth_client_corporate_full):
        """단일 설정값 조회 성공"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.get_setting.return_value = 'value1'

            response = auth_client_corporate_full.get('/api/corporate/settings/key1')
            assert response.status_code == 200
            assert response.is_json

    def test_set_setting_by_key_success(self, auth_client_corporate_full):
        """단일 설정값 저장 성공"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.set_setting.return_value = {'key': 'key1', 'value': 'value1'}

            response = auth_client_corporate_full.put(
                '/api/corporate/settings/key1',
                json={'value': 'value1'},
                content_type='application/json'
            )
            assert response.status_code == 200

    def test_get_settings_no_company_id(self, auth_client_corporate_full):
        """법인 ID 없을 때"""
        with patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=None):
            response = auth_client_corporate_full.get('/api/corporate/settings')
            assert response.status_code == 403


class TestCorporateSettingsEmployeeNumber:
    """사번 설정 API 테스트"""

    def test_get_employee_number_settings(self, auth_client_corporate_full):
        """사번 설정 조회"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.get_employee_number_settings.return_value = {'format': 'EMP{number}'}

            response = auth_client_corporate_full.get('/api/corporate/settings/employee-number')
            assert response.status_code == 200


class TestCorporateSettingsPayroll:
    """급여 설정 API 테스트"""

    def test_get_payroll_settings(self, auth_client_corporate_full):
        """급여 설정 조회"""
        with patch('app.blueprints.corporate_settings.settings_api.corporate_settings_service') as mock_service, \
             patch('app.blueprints.corporate_settings.settings_api.get_company_id', return_value=1):
            mock_service.get_payroll_settings.return_value = {'payday': 25}

            response = auth_client_corporate_full.get('/api/corporate/settings/payroll')
            assert response.status_code == 200

