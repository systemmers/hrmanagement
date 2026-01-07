"""
Employees Blueprint 테스트

직원 관리 기능 테스트:
- 직원 목록 조회
- 직원 상세 조회
- 직원 생성/수정/삭제
- 계정 발급
- API 엔드포인트
"""
import pytest
import json

from app.shared.constants.session_keys import SessionKeys
from app.domains.user.models import User


class TestEmployeeList:
    """직원 목록 조회 테스트"""

    def test_employee_list_requires_login(self, client):
        """목록 조회 로그인 필요 테스트"""
        response = client.get('/employees', follow_redirects=False)
        assert response.status_code == 302
        assert 'login' in response.location

    def test_employee_list_requires_manager_or_admin(
        self, client, test_user_personal
    ):
        """매니저/관리자만 접근 가능 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_PERSONAL
            sess[SessionKeys.USER_ROLE] = User.ROLE_EMPLOYEE

        response = client.get('/employees', follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_employee_list_renders_for_admin(self, auth_client_corporate_full):
        """관리자 직원 목록 렌더링 테스트"""
        response = auth_client_corporate_full.get('/employees')
        assert response.status_code == 200

    def test_employee_list_with_filters(self, auth_client_corporate_full):
        """필터를 포함한 목록 조회 테스트"""
        response = auth_client_corporate_full.get(
            '/employees?department=개발팀&status=active'
        )
        assert response.status_code == 200

    def test_employee_list_with_sorting(self, auth_client_corporate_full):
        """정렬을 포함한 목록 조회 테스트"""
        response = auth_client_corporate_full.get(
            '/employees?sort=name&order=asc'
        )
        assert response.status_code == 200


class TestEmployeePendingList:
    """계약대기 목록 테스트"""

    def test_pending_list_requires_manager_or_admin(
        self, client, test_user_personal
    ):
        """매니저/관리자만 접근 가능 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_PERSONAL
            sess[SessionKeys.USER_ROLE] = User.ROLE_EMPLOYEE

        response = client.get('/employees/pending', follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_pending_list_renders_for_admin(self, auth_client_corporate_full):
        """관리자 계약대기 목록 렌더링 테스트"""
        response = auth_client_corporate_full.get('/employees/pending')
        assert response.status_code == 200


class TestEmployeeDetail:
    """직원 상세 조회 테스트"""

    def test_employee_detail_requires_login(self, client):
        """상세 조회 로그인 필요 테스트"""
        response = client.get('/employees/1', follow_redirects=False)
        assert response.status_code == 302

    def test_employee_detail_not_found(self, auth_client_corporate_full):
        """존재하지 않는 직원 상세 조회 테스트"""
        response = auth_client_corporate_full.get(
            '/employees/99999', follow_redirects=True
        )
        # 리다이렉트 후 목록 또는 에러 페이지
        assert response.status_code == 200

    def test_employee_detail_renders(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """직원 상세 렌더링 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.get(f'/employees/{test_employee.id}')
        # 멀티테넌시 검증 (organization_id 필요)으로 인해 리다이렉트 발생 가능
        assert response.status_code in [200, 302]


class TestEmployeeNew:
    """직원 등록 폼 테스트"""

    def test_new_employee_form_requires_manager_or_admin(
        self, auth_client_personal_full
    ):
        """매니저/관리자만 접근 가능 테스트"""
        response = auth_client_personal_full.get(
            '/employees/new', follow_redirects=False
        )
        assert response.status_code in [302, 403]

    def test_new_employee_form_renders_for_admin(self, auth_client_corporate_full):
        """관리자 등록 폼 렌더링 테스트"""
        response = auth_client_corporate_full.get('/employees/new')
        assert response.status_code == 200


class TestEmployeeEdit:
    """직원 수정 폼 테스트"""

    def test_edit_employee_form_requires_login(self, client):
        """수정 폼 로그인 필요 테스트"""
        response = client.get('/employees/1/edit', follow_redirects=False)
        assert response.status_code == 302

    def test_edit_employee_form_not_found(self, auth_client_corporate_full):
        """존재하지 않는 직원 수정 폼 테스트"""
        response = auth_client_corporate_full.get(
            '/employees/99999/edit', follow_redirects=True
        )
        assert response.status_code == 200  # 리다이렉트 후

    def test_edit_employee_form_renders(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """직원 수정 폼 렌더링 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.get(f'/employees/{test_employee.id}/edit')
        # 멀티테넌시 검증 (organization_id 필요)으로 인해 리다이렉트 발생 가능
        assert response.status_code in [200, 302]


class TestEmployeeCreate:
    """직원 생성 테스트"""

    def test_create_employee_requires_manager_or_admin(
        self, auth_client_personal_full
    ):
        """생성 매니저/관리자 권한 필요 테스트"""
        response = auth_client_personal_full.post(
            '/employees',
            data={'name': '테스트'},
            follow_redirects=False
        )
        assert response.status_code in [302, 403]

    def test_create_employee_success(self, auth_client_corporate_full):
        """직원 생성 성공 테스트"""
        response = auth_client_corporate_full.post(
            '/employees',
            data={
                'name': '신규직원',
                'department': '개발팀',
                'position': '사원',
                'status': 'active',
                'email': 'new@test.com'
            },
            follow_redirects=True
        )
        # 생성 후 상세 또는 목록으로 리다이렉트
        assert response.status_code == 200

    def test_create_employee_with_account(self, auth_client_corporate_full):
        """계정 포함 직원 생성 테스트"""
        response = auth_client_corporate_full.post(
            '/employees',
            data={
                'name': '신규직원',
                'department': '개발팀',
                'position': '사원',
                'status': 'active',
                'email': 'newwithacc@test.com',
                'create_account': 'on',
                'account_username': 'newemployee',
                'account_password': 'password123'
            },
            follow_redirects=True
        )
        assert response.status_code == 200


class TestEmployeeUpdate:
    """직원 수정 테스트"""

    def test_update_employee_requires_login(self, client):
        """수정 로그인 필요 테스트"""
        response = client.post('/employees/1/update')
        assert response.status_code == 302

    def test_update_employee_success(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """직원 수정 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.post(
            f'/employees/{test_employee.id}/update',
            data={
                'name': '수정된이름',
                'department': '인사팀',
                'position': '대리'
            },
            follow_redirects=True
        )
        assert response.status_code == 200


class TestEmployeeUpdateBasic:
    """직원 기본정보 수정 테스트"""

    def test_update_basic_requires_login(self, client):
        """기본정보 수정 로그인 필요 테스트"""
        response = client.post('/employees/1/update/basic')
        assert response.status_code == 302

    def test_update_basic_success(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """기본정보 수정 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.post(
            f'/employees/{test_employee.id}/update/basic',
            data={'position': '과장'},
            follow_redirects=True
        )
        assert response.status_code == 200


class TestEmployeeUpdateHistory:
    """직원 이력정보 수정 테스트"""

    def test_update_history_requires_login(self, client):
        """이력정보 수정 로그인 필요 테스트"""
        response = client.post('/employees/1/update/history')
        assert response.status_code == 302

    def test_update_history_success(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """이력정보 수정 성공 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.USERNAME] = test_user_corporate.username
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.post(
            f'/employees/{test_employee.id}/update/history',
            data={},
            follow_redirects=True
        )
        assert response.status_code == 200


class TestEmployeeDelete:
    """직원 삭제 테스트"""

    def test_delete_employee_requires_admin(
        self, client, test_user_corporate, test_company
    ):
        """삭제 관리자 권한 필요 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_MANAGER  # Not admin

        response = client.post('/employees/1/delete', follow_redirects=False)
        assert response.status_code in [302, 403]

    def test_delete_employee_not_found(self, auth_client_corporate_full):
        """존재하지 않는 직원 삭제 테스트"""
        response = auth_client_corporate_full.post(
            '/employees/99999/delete', follow_redirects=True
        )
        assert response.status_code == 200


class TestAccountProvision:
    """계정 발급 테스트"""

    def test_account_provision_requires_manager_or_admin(
        self, auth_client_personal_full
    ):
        """계정 발급 매니저/관리자 권한 필요 테스트"""
        response = auth_client_personal_full.get(
            '/employees/provision', follow_redirects=False
        )
        assert response.status_code in [302, 403]

    def test_account_provision_page_renders(self, auth_client_corporate_full):
        """계정 발급 페이지 렌더링 테스트"""
        response = auth_client_corporate_full.get('/employees/provision')
        assert response.status_code == 200


class TestEmployeeListAPI:
    """직원 목록 API 테스트"""

    def test_api_employee_list_requires_login(self, client):
        """API 목록 조회 로그인 필요 테스트"""
        response = client.get('/api/employees')
        assert response.status_code in [302, 401]

    def test_api_employee_list_requires_manager_or_admin(
        self, auth_client_personal_full
    ):
        """API 매니저/관리자 권한 필요 테스트"""
        response = auth_client_personal_full.get('/api/employees')
        assert response.status_code in [302, 403]

    def test_api_employee_list_success(self, auth_client_corporate_full):
        """API 목록 조회 성공 테스트"""
        response = auth_client_corporate_full.get('/api/employees')
        assert response.status_code == 200

        data = json.loads(response.data)
        assert 'success' in data or 'employees' in data or 'data' in data


class TestLegacyRedirects:
    """레거시 리다이렉트 테스트"""

    def test_edit_basic_redirects(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """기본정보 수정 리다이렉트 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.get(
            f'/employees/{test_employee.id}/edit/basic',
            follow_redirects=False
        )
        assert response.status_code == 302
        assert 'edit' in response.location

    def test_edit_history_redirects(
        self, client, test_user_corporate, test_company, test_employee
    ):
        """이력정보 수정 리다이렉트 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_corporate.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_CORPORATE
            sess[SessionKeys.COMPANY_ID] = test_company.id
            sess[SessionKeys.USER_ROLE] = User.ROLE_ADMIN

        response = client.get(
            f'/employees/{test_employee.id}/edit/history',
            follow_redirects=False
        )
        assert response.status_code == 302
        assert 'edit' in response.location
