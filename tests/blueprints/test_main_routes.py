"""
Main Routes 테스트

메인 페이지 및 검색 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.constants.session_keys import SessionKeys


class TestMainIndex:
    """메인 페이지 테스트"""

    def test_index_unauthenticated(self, client):
        """비로그인 사용자는 랜딩페이지"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'landing' in response.data.lower() or 'landing' in response.data.decode('utf-8', errors='ignore').lower()

    def test_index_personal_redirect(self, auth_client_personal_full):
        """개인 계정은 personal 대시보드로 리다이렉트"""
        response = auth_client_personal_full.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'personal' in response.location

    def test_index_corporate_renders(self, auth_client_corporate_full):
        """법인 계정은 메인 페이지 렌더링"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_service.get_statistics.return_value = {'total': 10}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/')
            assert response.status_code == 200


class TestMainSearch:
    """검색 기능 테스트"""

    def test_search_requires_login(self, client):
        """검색 시 로그인 필요"""
        response = client.get('/search')
        assert response.status_code == 302

    def test_search_with_query(self, auth_client_corporate_full):
        """검색어로 검색"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_employee = Mock()
            mock_employee.to_dict.return_value = {'id': 1, 'name': '홍길동'}
            mock_service.search_employees.return_value = [mock_employee]
            mock_service.get_statistics.return_value = {'total': 1}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/search?q=홍길동')
            assert response.status_code == 200

    def test_search_ajax_request(self, auth_client_corporate_full):
        """AJAX 요청 시 JSON 반환"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_employee = Mock()
            mock_employee.to_dict.return_value = {'id': 1, 'name': '홍길동'}
            mock_service.search_employees.return_value = [mock_employee]
            mock_service.get_statistics.return_value = {'total': 1}

            response = auth_client_corporate_full.get(
                '/search?q=홍길동',
                headers={'X-Requested-With': 'XMLHttpRequest'}
            )
            assert response.status_code == 200
            assert response.is_json

    def test_search_with_filters(self, auth_client_corporate_full):
        """필터로 검색"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_employee = Mock()
            mock_employee.to_dict.return_value = {'id': 1}
            mock_service.filter_employees.return_value = [mock_employee]
            mock_service.get_statistics.return_value = {'total': 1}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/search?department=개발팀&status=active')
            assert response.status_code == 200


class TestMainExamples:
    """예제 페이지 테스트"""

    def test_data_table_demo_requires_login(self, client):
        """데이터 테이블 데모 페이지 접근 시 로그인 필요"""
        response = client.get('/examples/data-table')
        assert response.status_code == 302

    def test_data_table_demo_renders(self, auth_client_personal_full):
        """데이터 테이블 데모 페이지 렌더링"""
        response = auth_client_personal_full.get('/examples/data-table')
        assert response.status_code == 200

    def test_styleguide_requires_login(self, client):
        """스타일 가이드 페이지 접근 시 로그인 필요"""
        response = client.get('/examples/styleguide')
        assert response.status_code == 302

    def test_styleguide_renders(self, auth_client_personal_full):
        """스타일 가이드 페이지 렌더링"""
        response = auth_client_personal_full.get('/examples/styleguide')
        assert response.status_code == 200


class TestMainIndexEdgeCases:
    """메인 페이지 엣지 케이스 테스트"""

    def test_index_employee_role_without_employee_id(self, client):
        """직원 역할이지만 employee_id가 없는 경우"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = 1
            sess[SessionKeys.ACCOUNT_TYPE] = 'corporate'
            sess[SessionKeys.USER_ROLE] = 'employee'
            sess[SessionKeys.EMPLOYEE_ID] = None

        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'logout' in response.location or 'login' in response.location

    def test_index_employee_role_with_employee_id(self, client):
        """직원 역할이고 employee_id가 있는 경우"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = 1
            sess[SessionKeys.ACCOUNT_TYPE] = 'corporate'
            sess[SessionKeys.USER_ROLE] = 'employee'
            sess[SessionKeys.EMPLOYEE_ID] = 1

        response = client.get('/', follow_redirects=False)
        assert response.status_code == 302
        assert 'profile.dashboard' in response.location or 'dashboard' in response.location


class TestMainSearchEdgeCases:
    """검색 기능 엣지 케이스 테스트"""

    def test_search_no_query_no_filters(self, auth_client_corporate_full):
        """검색어와 필터 모두 없는 경우"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_service.get_all_employees.return_value = []
            mock_service.get_statistics.return_value = {'total': 0}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/search')
            assert response.status_code == 200

    def test_search_with_all_filters(self, auth_client_corporate_full):
        """모든 필터 적용"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_employee = Mock()
            mock_employee.to_dict.return_value = {'id': 1}
            mock_service.filter_employees.return_value = [mock_employee]
            mock_service.get_statistics.return_value = {'total': 1}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/search?department=개발팀&position=사원&status=active')
            assert response.status_code == 200
            mock_service.filter_employees.assert_called_once()

    def test_search_empty_query(self, auth_client_corporate_full):
        """빈 검색어"""
        with patch('app.blueprints.main.employee_service') as mock_service, \
             patch('app.blueprints.main.get_current_organization_id', return_value=1):
            mock_service.get_all_employees.return_value = []
            mock_service.get_statistics.return_value = {'total': 0}
            mock_service.get_department_statistics.return_value = {}
            mock_service.get_recent_employees.return_value = []
            mock_service.get_all_classification_options.return_value = {}

            response = auth_client_corporate_full.get('/search?q=')
            assert response.status_code == 200
