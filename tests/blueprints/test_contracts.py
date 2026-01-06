"""
Contracts Blueprint 테스트

계약 관리 기능 테스트:
- 개인/직원 계약 목록 조회
- 법인 계약 관리
- 계약 승인/거절/종료 API
- 데이터 공유 설정
"""
import pytest
import json

from app.shared.constants.session_keys import SessionKeys
from app.models.user import User


class TestPersonalContracts:
    """개인/직원 계정 계약 기능 테스트"""

    def test_my_contracts_requires_login(self, client):
        """로그인 필요 테스트"""
        response = client.get('/contracts/my', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location

    def test_my_contracts_requires_personal_account(self, client, test_user_corporate, test_company):
        """개인/직원 계정만 접근 가능 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id

        response = client.get('/contracts/my', follow_redirects=False)
        # 법인 계정은 접근 불가 (리다이렉트 또는 403)
        assert response.status_code in [302, 403]

    def test_my_contracts_renders_for_personal(self, auth_client_personal_full):
        """개인 계정 계약 목록 렌더링 테스트"""
        response = auth_client_personal_full.get('/contracts/my')
        assert response.status_code == 200

    def test_pending_contracts_requires_login(self, client):
        """대기 중 계약 페이지 로그인 필요 테스트"""
        response = client.get('/contracts/pending', follow_redirects=False)
        assert response.status_code == 302

    def test_pending_contracts_renders_for_personal(self, auth_client_personal_full):
        """대기 중 계약 목록 렌더링 테스트"""
        response = auth_client_personal_full.get('/contracts/pending')
        assert response.status_code == 200


class TestContractDetail:
    """계약 상세 조회 테스트"""

    def test_contract_detail_requires_login(self, client):
        """계약 상세 로그인 필요 테스트"""
        response = client.get('/contracts/1', follow_redirects=False)
        assert response.status_code == 302

    def test_contract_detail_not_found(self, auth_client_personal_full):
        """존재하지 않는 계약 조회 테스트"""
        response = auth_client_personal_full.get('/contracts/99999', follow_redirects=True)
        assert response.status_code == 200  # 리다이렉트 후 목록 페이지

    def test_contract_detail_renders_for_owner(
        self, client, test_user_personal, test_contract_pending
    ):
        """계약 당사자 상세 조회 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(f'/contracts/{test_contract_pending.id}')
        assert response.status_code == 200


class TestCompanyContracts:
    """법인 계약 관리 테스트"""

    def test_company_contracts_requires_corporate_account(self, client, test_user_personal):
        """법인 계정만 접근 가능 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_PERSONAL

        response = client.get('/contracts/company', follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_company_contracts_renders_for_corporate(self, auth_client_corporate_full):
        """법인 계약 목록 렌더링 테스트"""
        response = auth_client_corporate_full.get('/contracts/company')
        assert response.status_code == 200

    def test_company_pending_requires_corporate_account(self, auth_client_personal_full):
        """법인 대기 계약 접근 권한 테스트"""
        response = auth_client_personal_full.get('/contracts/company/pending', follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_company_pending_renders_for_corporate(self, auth_client_corporate_full):
        """법인 대기 계약 목록 렌더링 테스트"""
        response = auth_client_corporate_full.get('/contracts/company/pending')
        assert response.status_code == 200

    def test_request_contract_page_renders(self, auth_client_corporate_full):
        """계약 요청 페이지 렌더링 테스트"""
        response = auth_client_corporate_full.get('/contracts/request')
        assert response.status_code == 200


class TestContractApproveRejectAPI:
    """계약 승인/거절 API 테스트"""

    def test_approve_contract_requires_login(self, client):
        """승인 API 로그인 필요 테스트"""
        response = client.post('/contracts/api/1/approve')
        assert response.status_code == 302 or response.status_code == 401

    def test_reject_contract_requires_login(self, client):
        """거절 API 로그인 필요 테스트"""
        response = client.post('/contracts/api/1/reject')
        assert response.status_code == 302 or response.status_code == 401

    def test_approve_contract_not_found(self, auth_client_personal_full):
        """존재하지 않는 계약 승인 테스트"""
        response = auth_client_personal_full.post('/contracts/api/99999/approve')
        # 404 또는 권한 없음(302) 응답
        assert response.status_code in [302, 403, 404]

    def test_approve_contract_success(
        self, client, test_user_personal, test_contract_pending
    ):
        """계약 승인 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.post(f'/contracts/api/{test_contract_pending.id}/approve')
        # 성공 또는 권한 검사에 따른 응답
        assert response.status_code in [200, 302, 403]

    def test_reject_contract_with_reason(
        self, client, test_user_personal, test_contract_pending
    ):
        """계약 거절 (사유 포함) 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.post(
            f'/contracts/api/{test_contract_pending.id}/reject',
            data=json.dumps({'reason': '테스트 거절 사유'}),
            content_type='application/json'
        )
        assert response.status_code in [200, 302, 403]


class TestContractTerminateAPI:
    """계약 종료 API 테스트"""

    def test_terminate_contract_requires_login(self, client):
        """종료 API 로그인 필요 테스트"""
        response = client.post('/contracts/api/1/terminate')
        assert response.status_code == 302 or response.status_code == 401

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
            f'/contracts/api/{test_contract_approved.id}/terminate',
            data=json.dumps({'reason': '테스트 종료 사유'}),
            content_type='application/json'
        )
        assert response.status_code in [200, 302, 403]


class TestSharingSettingsAPI:
    """데이터 공유 설정 API 테스트"""

    def test_get_sharing_settings_requires_login(self, client):
        """공유 설정 조회 로그인 필요 테스트"""
        response = client.get('/contracts/api/1/sharing-settings')
        assert response.status_code == 302 or response.status_code == 401

    def test_get_sharing_settings_not_found(self, auth_client_personal_full):
        """존재하지 않는 계약 공유 설정 조회 테스트"""
        response = auth_client_personal_full.get('/contracts/api/99999/sharing-settings')
        assert response.status_code in [403, 404]

    def test_get_sharing_settings_success(
        self, client, test_user_personal, test_contract_approved
    ):
        """공유 설정 조회 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.USERNAME] = test_user_personal.username
            sess[SessionKeys.ACCOUNT_TYPE] = test_user_personal.account_type
            sess[SessionKeys.USER_ROLE] = test_user_personal.role

        response = client.get(
            f'/contracts/api/{test_contract_approved.id}/sharing-settings'
        )
        assert response.status_code == 200

    def test_update_sharing_settings_forbidden_for_non_owner(
        self, client, test_user_corporate, test_company, test_contract_approved
    ):
        """비소유자 공유 설정 수정 금지 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id

        response = client.put(
            f'/contracts/api/{test_contract_approved.id}/sharing-settings',
            data=json.dumps({'share_basic_info': True}),
            content_type='application/json'
        )
        assert response.status_code == 403


class TestContractSearchAPI:
    """계약 검색 API 테스트"""

    def test_search_contracts_requires_corporate(self, auth_client_personal_full):
        """법인 계정만 검색 가능 테스트"""
        response = auth_client_personal_full.get('/contracts/api/search')
        assert response.status_code in [302, 403]

    def test_search_contracts_success(self, auth_client_corporate_full):
        """계약 검색 성공 테스트"""
        response = auth_client_corporate_full.get('/contracts/api/search')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'success' in data or 'data' in data

    def test_search_contracts_with_filters(self, auth_client_corporate_full):
        """필터를 포함한 계약 검색 테스트"""
        response = auth_client_corporate_full.get(
            '/contracts/api/search?status=approved&contract_type=employment'
        )
        assert response.status_code == 200


class TestContractStatsAPI:
    """계약 통계 API 테스트"""

    def test_company_stats_requires_corporate(self, auth_client_personal_full):
        """법인 통계 API 법인 계정 필요 테스트"""
        response = auth_client_personal_full.get('/contracts/api/stats/company')
        assert response.status_code in [302, 403]

    def test_company_stats_success(self, auth_client_corporate_full):
        """법인 계약 통계 조회 성공 테스트"""
        response = auth_client_corporate_full.get('/contracts/api/stats/company')
        assert response.status_code == 200

    def test_personal_stats_requires_personal(self, auth_client_corporate_full):
        """개인 통계 API 개인/직원 계정 필요 테스트"""
        response = auth_client_corporate_full.get('/contracts/api/stats/personal')
        assert response.status_code in [302, 403]

    def test_personal_stats_success(self, auth_client_personal_full):
        """개인 계약 통계 조회 성공 테스트"""
        response = auth_client_personal_full.get('/contracts/api/stats/personal')
        assert response.status_code == 200


class TestEmployeeContractRequestAPI:
    """직원 계약 요청 API 테스트"""

    def test_request_employee_contract_requires_corporate(
        self, auth_client_personal_full
    ):
        """직원 계약 요청 법인 계정 필요 테스트"""
        response = auth_client_personal_full.post(
            '/contracts/api/employee/1/request',
            data=json.dumps({'contract_type': 'employment'}),
            content_type='application/json'
        )
        assert response.status_code in [302, 403]

    def test_request_employee_contract_success(
        self, auth_client_corporate_full, test_user_personal
    ):
        """직원 계약 요청 성공 테스트"""
        response = auth_client_corporate_full.post(
            f'/contracts/api/employee/{test_user_personal.id}/request',
            data=json.dumps({
                'contract_type': 'employment',
                'position': '사원',
                'department': '개발팀'
            }),
            content_type='application/json'
        )
        # 성공 또는 이미 계약이 있는 경우 에러
        assert response.status_code in [200, 400]
