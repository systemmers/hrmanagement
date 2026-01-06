"""
Mypage Routes 테스트

마이페이지 라우트 테스트
"""
import pytest
from unittest.mock import patch, Mock

from app.shared.constants.session_keys import SessionKeys, AccountType


class TestMypageCompanyInfo:
    """회사 인사카드 테스트"""

    def test_company_info_requires_login(self, client):
        """인사카드 접근 시 로그인 필요"""
        response = client.get('/my/company')
        assert response.status_code == 302

    def test_company_info_personal_redirect(self, auth_client_personal_full):
        """개인 계정은 회사 목록으로 리다이렉트"""
        response = auth_client_personal_full.get('/my/company', follow_redirects=False)
        assert response.status_code == 302
        assert 'company_card_list' in response.location or 'personal' in response.location

    def test_company_info_no_employee_id(self, auth_client_corporate_full):
        """employee_id 없을 때 안내 페이지"""
        with auth_client_corporate_full.session_transaction() as sess:
            sess.pop(SessionKeys.EMPLOYEE_ID, None)

        response = auth_client_corporate_full.get('/my/company')
        assert response.status_code == 200

    def test_company_info_renders(self, auth_client_corporate_full):
        """인사카드 렌더링"""
        with patch('app.blueprints.mypage.employee_service') as mock_service, \
             patch('app.blueprints.mypage.contract_service') as mock_contract, \
             patch('app.blueprints.mypage.system_setting_service') as mock_system:
            mock_service.get_employee_by_id.return_value = {'id': 1, 'name': '홍길동', 'status': 'active'}
            mock_contract.get_employee_contract_status.return_value = 'approved'
            mock_system.get_company_data.return_value = {'name': '테스트법인'}
            mock_service.get_salary_info.return_value = {}
            mock_service.get_benefit_info.return_value = {}
            mock_service.get_contract_info.return_value = {}
            mock_service.get_insurance_info.return_value = {}
            mock_service.get_salary_history_list.return_value = []
            mock_service.get_salary_payment_list.return_value = []
            mock_service.get_promotion_list.return_value = []
            mock_service.get_evaluation_list.return_value = []
            mock_service.get_training_list.return_value = []
            mock_service.get_attendance_summary.return_value = {}
            mock_service.get_asset_list.return_value = []
            mock_service.get_education_list.return_value = []
            mock_service.get_career_list.return_value = []
            mock_service.get_certificate_list.return_value = []
            mock_service.get_family_list.return_value = []
            mock_service.get_language_list.return_value = []
            mock_service.get_military_info.return_value = None
            mock_service.get_hr_project_list.return_value = []
            mock_service.get_project_participation_list.return_value = []
            mock_service.get_award_list.return_value = []
            mock_service.get_attachment_by_category.return_value = None
            mock_service.get_attachment_list.return_value = []

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.EMPLOYEE_ID] = 1
                sess[SessionKeys.USER_ID] = 1
                sess[SessionKeys.COMPANY_ID] = 1

            response = auth_client_corporate_full.get('/my/company')
            assert response.status_code == 200

    def test_company_info_pending_contract(self, auth_client_corporate_full):
        """계약 미승인 시 대기 페이지"""
        with patch('app.blueprints.mypage.employee_service') as mock_service, \
             patch('app.blueprints.mypage.contract_service') as mock_contract:
            mock_service.get_employee_by_id.return_value = {'id': 1, 'name': '홍길동'}
            mock_contract.get_employee_contract_status.return_value = 'pending'

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.EMPLOYEE_ID] = 1
                sess[SessionKeys.USER_ID] = 1
                sess[SessionKeys.COMPANY_ID] = 1

            response = auth_client_corporate_full.get('/my/company')
            assert response.status_code == 200

    def test_company_info_employee_not_found(self, auth_client_corporate_full):
        """직원 정보 없을 때"""
        with patch('app.blueprints.mypage.employee_service') as mock_service:
            mock_service.get_employee_by_id.return_value = None

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.EMPLOYEE_ID] = 999
                sess[SessionKeys.USER_ID] = 1
                sess[SessionKeys.COMPANY_ID] = 1

            response = auth_client_corporate_full.get('/my/company', follow_redirects=False)
            assert response.status_code == 302

    def test_company_info_pending_info_redirect(self, auth_client_corporate_full):
        """프로필 미완성 시 리다이렉트"""
        with patch('app.blueprints.mypage.employee_service') as mock_service, \
             patch('app.blueprints.mypage.contract_service') as mock_contract:
            mock_service.get_employee_by_id.return_value = {'id': 1, 'name': '홍길동', 'status': 'pending_info', 'get': lambda key, default: {'id': 1, 'name': '홍길동', 'status': 'pending_info'}.get(key, default)}
            mock_contract.get_employee_contract_status.return_value = 'approved'

            with auth_client_corporate_full.session_transaction() as sess:
                sess[SessionKeys.EMPLOYEE_ID] = 1
                sess[SessionKeys.USER_ID] = 1
                sess[SessionKeys.COMPANY_ID] = 1

            response = auth_client_corporate_full.get('/my/company', follow_redirects=False)
            assert response.status_code == 302
            assert 'profile/complete' in response.location or 'complete' in response.location


