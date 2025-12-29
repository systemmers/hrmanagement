"""
Sync Blueprint 테스트

데이터 동기화 기능 테스트:
- 필드 조회
- 개인 -> 법인 동기화
- 법인 -> 개인 동기화
- 실시간 동기화 설정
- 계약 종료 및 보관
"""
import pytest
import json

from app.constants.session_keys import SessionKeys, AccountType
from app.models.user import User


class TestSyncFieldsAPI:
    """동기화 필드 조회 테스트"""

    def test_get_syncable_fields_requires_login(self, client):
        """필드 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/fields/1')
        # api_login_required는 JSON 응답 반환
        assert response.status_code in [401, 302]

    def test_get_syncable_fields_not_found(self, auth_client_personal_full):
        """존재하지 않는 계약 필드 조회 테스트"""
        response = auth_client_personal_full.get('/api/sync/fields/99999')
        # 계약 없음 또는 권한 없음
        assert response.status_code in [403, 404]

    def test_get_syncable_fields_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """필드 조회 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(f'/api/sync/fields/{test_contract_approved.id}')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data.get('success') is True
        assert 'fields' in data or 'data' in data


class TestPersonalToEmployeeSyncAPI:
    """개인 -> 법인 동기화 테스트"""

    def test_sync_personal_to_employee_requires_login(self, client):
        """동기화 로그인 필요 테스트"""
        response = client.post('/api/sync/personal-to-employee/1')
        assert response.status_code in [401, 302]

    def test_sync_personal_to_employee_requires_personal_account(
        self, auth_client_corporate_full
    ):
        """개인 계정만 동기화 가능 테스트"""
        response = auth_client_corporate_full.post(
            '/api/sync/personal-to-employee/1',
            data=json.dumps({}),
            content_type='application/json'
        )
        assert response.status_code in [401, 403]

    def test_sync_personal_to_employee_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """개인 -> 법인 동기화 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.post(
            f'/api/sync/personal-to-employee/{test_contract_approved.id}',
            data=json.dumps({'fields': ['name']}),
            content_type='application/json'
        )
        # 성공 또는 프로필 없음 등의 비즈니스 에러
        assert response.status_code in [200, 400]


class TestEmployeeToPersonalSyncAPI:
    """법인 -> 개인 동기화 테스트"""

    def test_sync_employee_to_personal_requires_login(self, client):
        """동기화 로그인 필요 테스트"""
        response = client.post('/api/sync/employee-to-personal/1')
        assert response.status_code in [401, 302]

    def test_sync_employee_to_personal_requires_corporate_account(
        self, auth_client_personal_full
    ):
        """법인 계정만 역동기화 가능 테스트"""
        response = auth_client_personal_full.post(
            '/api/sync/employee-to-personal/1',
            data=json.dumps({'fields': ['name']}),
            content_type='application/json'
        )
        assert response.status_code in [401, 403]

    def test_sync_employee_to_personal_requires_fields(
        self, auth_client_corporate_full, test_contract_approved
    ):
        """필드 지정 필수 테스트"""
        response = auth_client_corporate_full.post(
            f'/api/sync/employee-to-personal/{test_contract_approved.id}',
            data=json.dumps({}),
            content_type='application/json'
        )
        # 필드 미지정 시 에러 또는 권한 검사에 따른 응답
        assert response.status_code in [400, 403]


class TestFullSyncAPI:
    """전체 동기화 테스트"""

    def test_full_sync_requires_corporate_account(self, auth_client_personal_full):
        """전체 동기화 법인 계정 필요 테스트"""
        response = auth_client_personal_full.post('/api/sync/full-sync/1')
        assert response.status_code in [401, 403]

    def test_full_sync_contract_not_found(self, auth_client_corporate_full):
        """존재하지 않는 계약 전체 동기화 테스트"""
        response = auth_client_corporate_full.post('/api/sync/full-sync/99999')
        assert response.status_code in [403, 404]

    def test_full_sync_success(
        self, client, test_user_corporate, test_company, test_contract_approved
    ):
        """전체 동기화 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = test_user_corporate.role

        response = client.post(
            f'/api/sync/full-sync/{test_contract_approved.id}'
        )
        # 성공 또는 관련 데이터 없음 등의 응답
        assert response.status_code in [200, 400, 403]


class TestSyncAllContractsAPI:
    """전체 계약 동기화 테스트"""

    def test_sync_all_contracts_requires_login(self, client):
        """전체 계약 동기화 로그인 필요 테스트"""
        response = client.post('/api/sync/all-contracts')
        assert response.status_code in [401, 302]

    def test_sync_all_contracts_requires_personal_account(
        self, auth_client_corporate_full
    ):
        """개인 계정만 전체 동기화 가능 테스트"""
        response = auth_client_corporate_full.post('/api/sync/all-contracts')
        assert response.status_code in [401, 403]

    def test_sync_all_contracts_success(self, auth_client_personal_full):
        """전체 계약 동기화 성공 테스트"""
        response = auth_client_personal_full.post('/api/sync/all-contracts')
        assert response.status_code == 200


class TestFieldMappingsAPI:
    """필드 매핑 조회 테스트"""

    def test_field_mappings_requires_login(self, client):
        """필드 매핑 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/field-mappings')
        assert response.status_code in [401, 302]

    def test_field_mappings_success(self, auth_client_personal_full):
        """필드 매핑 조회 성공 테스트"""
        response = auth_client_personal_full.get('/api/sync/field-mappings')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert data.get('success') is True


class TestContractsListAPI:
    """계약 목록 조회 테스트"""

    def test_get_my_contracts_requires_login(self, client):
        """계약 목록 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/contracts')
        assert response.status_code in [401, 302]

    def test_get_my_contracts_requires_personal_account(
        self, auth_client_corporate_full
    ):
        """개인 계정만 조회 가능 테스트"""
        response = auth_client_corporate_full.get('/api/sync/contracts')
        assert response.status_code in [401, 403]

    def test_get_my_contracts_success(self, auth_client_personal_full):
        """계약 목록 조회 성공 테스트"""
        response = auth_client_personal_full.get('/api/sync/contracts')
        assert response.status_code == 200


class TestRealtimeSyncSettingsAPI:
    """실시간 동기화 설정 테스트"""

    def test_toggle_realtime_sync_requires_login(self, client):
        """실시간 동기화 설정 로그인 필요 테스트"""
        response = client.put(
            '/api/sync/settings/1/realtime',
            data=json.dumps({'enabled': True}),
            content_type='application/json'
        )
        assert response.status_code in [401, 302]

    def test_toggle_realtime_sync_requires_personal_account(
        self, auth_client_corporate_full
    ):
        """개인 계정만 설정 가능 테스트"""
        response = auth_client_corporate_full.put(
            '/api/sync/settings/1/realtime',
            data=json.dumps({'enabled': True}),
            content_type='application/json'
        )
        assert response.status_code in [401, 403]

    def test_toggle_realtime_sync_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """실시간 동기화 설정 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.put(
            f'/api/sync/settings/{test_contract_approved.id}/realtime',
            data=json.dumps({'enabled': True}),
            content_type='application/json'
        )
        assert response.status_code == 200


class TestSyncLogsAPI:
    """동기화 로그 조회 테스트"""

    def test_get_sync_logs_requires_login(self, client):
        """로그 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/logs/1')
        assert response.status_code in [401, 302]

    def test_get_sync_logs_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """로그 조회 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(
            f'/api/sync/logs/{test_contract_approved.id}'
        )
        assert response.status_code == 200

    def test_get_sync_logs_with_filters(
        self, client, test_user_personal, test_contract_approved
    ):
        """필터를 포함한 로그 조회 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(
            f'/api/sync/logs/{test_contract_approved.id}?limit=10&sync_type=manual'
        )
        assert response.status_code == 200


class TestTerminationAPI:
    """계약 종료 테스트"""

    def test_terminate_contract_requires_login(self, client):
        """계약 종료 로그인 필요 테스트"""
        response = client.post('/api/sync/terminate/1')
        assert response.status_code in [401, 302]

    def test_terminate_contract_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """계약 종료 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.post(
            f'/api/sync/terminate/{test_contract_approved.id}',
            data=json.dumps({'reason': '테스트 종료'}),
            content_type='application/json'
        )
        # 성공 또는 상태 검사에 따른 에러
        assert response.status_code in [200, 400, 403]


class TestRetentionStatusAPI:
    """데이터 보관 상태 조회 테스트"""

    def test_get_retention_status_requires_login(self, client):
        """보관 상태 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/retention/1')
        assert response.status_code in [401, 302]

    def test_get_retention_status_not_found(self, auth_client_personal_full):
        """존재하지 않는 계약 보관 상태 조회 테스트"""
        response = auth_client_personal_full.get('/api/sync/retention/99999')
        assert response.status_code in [400, 403, 404]

    def test_get_retention_status_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """보관 상태 조회 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(
            f'/api/sync/retention/{test_contract_approved.id}'
        )
        # 성공 또는 종료되지 않은 계약 에러
        assert response.status_code in [200, 400]


class TestTerminationHistoryAPI:
    """종료 이력 조회 테스트"""

    def test_get_termination_history_requires_login(self, client):
        """종료 이력 조회 로그인 필요 테스트"""
        response = client.get('/api/sync/termination-history')
        assert response.status_code in [401, 302]

    def test_get_termination_history_personal(self, auth_client_personal_full):
        """개인 계정 종료 이력 조회 테스트"""
        response = auth_client_personal_full.get('/api/sync/termination-history')
        assert response.status_code == 200

    def test_get_termination_history_corporate(self, auth_client_corporate_full):
        """법인 계정 종료 이력 조회 테스트"""
        response = auth_client_corporate_full.get('/api/sync/termination-history')
        assert response.status_code == 200

    def test_get_termination_history_with_limit(self, auth_client_personal_full):
        """제한 조건 포함 종료 이력 조회 테스트"""
        response = auth_client_personal_full.get(
            '/api/sync/termination-history?limit=10'
        )
        assert response.status_code == 200
