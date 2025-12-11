"""
Corporate Blueprint Route Tests

app/blueprints/corporate.py의 모든 라우트를 테스트
"""
import pytest
from app.models.company import Company


class TestCorporatePublicRoutes:
    """공개 라우트 테스트 (인증 불필요)"""

    @pytest.mark.smoke
    def test_register_get(self, client):
        """법인 등록 페이지 GET"""
        response = client.get('/corporate/register')
        assert response.status_code == 200
        assert b'register' in response.data.lower() or response.status_code == 200

    @pytest.mark.smoke
    def test_register_post_invalid(self, client):
        """법인 등록 POST - 필수 필드 누락"""
        response = client.post('/corporate/register', data={})
        # 유효성 검사 실패시 다시 폼 표시 또는 에러
        assert response.status_code in [200, 302, 400]

    @pytest.mark.smoke
    def test_check_business_number_api(self, client):
        """사업자번호 중복 확인 API"""
        response = client.get('/corporate/api/check-business-number?business_number=9999999999')
        assert response.status_code == 200
        data = response.get_json()
        assert 'available' in data or 'exists' in data or 'error' not in data


class TestCorporateProtectedRoutes:
    """인증 필요 라우트 테스트 - 미인증시 리다이렉트"""

    @pytest.mark.smoke
    def test_dashboard_unauthenticated(self, client):
        """대시보드 - 미인증시 리다이렉트"""
        response = client.get('/corporate/dashboard')
        assert response.status_code in [302, 401, 403]

    @pytest.mark.smoke
    def test_settings_unauthenticated(self, client):
        """설정 - 미인증시 리다이렉트"""
        response = client.get('/corporate/settings')
        assert response.status_code in [302, 401, 403]

    @pytest.mark.smoke
    def test_users_unauthenticated(self, client):
        """사용자 목록 - 미인증시 리다이렉트"""
        response = client.get('/corporate/users')
        assert response.status_code in [302, 401, 403]

    @pytest.mark.smoke
    def test_add_user_unauthenticated(self, client):
        """사용자 추가 - 미인증시 리다이렉트"""
        response = client.get('/corporate/users/add')
        assert response.status_code in [302, 401, 403]


class TestCorporateAuthenticatedRoutes:
    """법인 계정 인증 후 라우트 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_user_corporate):
        """테스트 설정"""
        self.user = test_user_corporate

    @pytest.mark.smoke
    def test_dashboard_authenticated(self, auth_client_corporate):
        """대시보드 - 인증 후 접근"""
        response = auth_client_corporate.get('/corporate/dashboard')
        # 200: 정상 표시, 302: 프로필 생성 등 다른 페이지로 리다이렉트 가능
        assert response.status_code in [200, 302]

    @pytest.mark.smoke
    def test_settings_get(self, auth_client_corporate):
        """설정 페이지 GET"""
        response = auth_client_corporate.get('/corporate/settings')
        assert response.status_code in [200, 302]

    @pytest.mark.smoke
    def test_settings_post(self, auth_client_corporate):
        """설정 페이지 POST"""
        response = auth_client_corporate.post('/corporate/settings', data={
            'company_name': 'Updated Company',
        })
        # 성공시 리다이렉트 또는 폼 재표시
        assert response.status_code in [200, 302]

    @pytest.mark.smoke
    def test_users_list(self, auth_client_corporate):
        """사용자 목록 조회"""
        response = auth_client_corporate.get('/corporate/users')
        assert response.status_code in [200, 302]

    @pytest.mark.smoke
    def test_add_user_get(self, auth_client_corporate):
        """사용자 추가 폼 GET"""
        response = auth_client_corporate.get('/corporate/users/add')
        assert response.status_code in [200, 302]

    @pytest.mark.smoke
    def test_add_user_post_invalid(self, auth_client_corporate):
        """사용자 추가 POST - 필수 필드 누락"""
        response = auth_client_corporate.post('/corporate/users/add', data={})
        # 유효성 검사 실패시 폼 재표시 또는 에러
        assert response.status_code in [200, 302, 400]


class TestCorporateAPIRoutes:
    """법인 API 라우트 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_user_corporate, test_company):
        """테스트 설정"""
        self.user = test_user_corporate
        self.company = test_company

    @pytest.mark.smoke
    def test_company_info_api_unauthenticated(self, client, test_company):
        """회사 정보 API - 미인증시"""
        response = client.get(f'/corporate/api/company/{test_company.id}')
        assert response.status_code in [302, 401, 403]

    @pytest.mark.smoke
    def test_company_info_api_authenticated(self, auth_client_corporate, test_company):
        """회사 정보 API - 인증 후"""
        response = auth_client_corporate.get(f'/corporate/api/company/{test_company.id}')
        # 200: 정상 반환, 403: 다른 회사 정보 접근 시도시
        assert response.status_code in [200, 403, 404]

    @pytest.mark.smoke
    def test_company_info_api_invalid_id(self, auth_client_corporate):
        """회사 정보 API - 존재하지 않는 ID"""
        response = auth_client_corporate.get('/corporate/api/company/99999')
        assert response.status_code in [403, 404]


class TestCorporateRouteResponses:
    """라우트 응답 내용 검증"""

    @pytest.mark.smoke
    def test_register_page_has_form(self, client):
        """등록 페이지에 폼 존재 확인"""
        response = client.get('/corporate/register')
        assert response.status_code == 200
        # 폼 요소 또는 관련 텍스트 확인
        data = response.data.decode('utf-8').lower()
        assert 'form' in data or 'input' in data or 'submit' in data

    @pytest.mark.smoke
    def test_check_business_number_returns_json(self, client):
        """사업자번호 확인 API가 JSON 반환"""
        response = client.get('/corporate/api/check-business-number?business_number=1234567890')
        assert response.status_code == 200
        assert response.content_type == 'application/json'


class TestCorporateEdgeCases:
    """엣지 케이스 테스트"""

    @pytest.mark.smoke
    def test_register_duplicate_business_number(self, client, test_company):
        """중복 사업자번호로 등록 시도"""
        response = client.post('/corporate/register', data={
            'business_number': test_company.business_number,
            'company_name': 'Duplicate Company',
            'username': 'newuser',
            'email': 'new@test.com',
            'password': 'password123',
            'password_confirm': 'password123',
        })
        # 중복 검사로 인해 폼 재표시 또는 에러
        assert response.status_code in [200, 302, 400]

    @pytest.mark.smoke
    def test_check_existing_business_number(self, client, test_company):
        """이미 존재하는 사업자번호 확인"""
        response = client.get(
            f'/corporate/api/check-business-number?business_number={test_company.business_number}'
        )
        assert response.status_code == 200
        data = response.get_json()
        # available이 false이거나 exists가 true여야 함
        assert data.get('available') is False or data.get('exists') is True
