"""
CompanyService 단위 테스트

법인 서비스의 핵심 비즈니스 로직 테스트:
- 법인 조회
- 법인 정보 수정
"""
import pytest
from unittest.mock import Mock, patch

from app.services.company_service import CompanyService, company_service
from app.shared.base import ServiceResult


@pytest.fixture
def mock_repos(app):
    """CompanyService의 Repository를 Mock으로 대체하는 fixture"""
    mock_company_repo = Mock()

    with patch.object(company_service, 'company_repo', mock_company_repo):
        yield company_service, mock_company_repo


class TestCompanyServiceInit:
    """CompanyService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert company_service is not None
        assert isinstance(company_service, CompanyService)

    def test_service_has_repo_attribute(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(company_service, 'company_repo')


class TestCompanyServiceQueries:
    """법인 조회 테스트"""

    def test_get_by_id_returns_company(self, mock_repos):
        """ID로 법인 조회"""
        service, mock_repo = mock_repos

        mock_company = Mock()
        mock_company.id = 1
        mock_company.name = 'Test Corp'
        mock_repo.find_by_id.return_value = mock_company

        result = service.get_by_id(1)

        assert result is not None
        assert result.name == 'Test Corp'

    def test_get_by_id_not_found(self, mock_repos):
        """존재하지 않는 법인 조회"""
        service, mock_repo = mock_repos

        mock_repo.find_by_id.return_value = None

        result = service.get_by_id(999)

        assert result is None

    def test_get_with_stats_returns_dict(self, mock_repos):
        """법인 정보 + 통계 조회"""
        service, mock_repo = mock_repos

        expected = {
            'id': 1,
            'name': 'Test Corp',
            'employee_count': 10,
            'active_contracts': 8
        }
        mock_repo.get_with_stats.return_value = expected

        result = service.get_with_stats(1)

        assert result is not None
        assert result['employee_count'] == 10


class TestCompanyServiceValidation:
    """법인 유효성 검증 테스트"""

    def test_exists_by_business_number_true(self, mock_repos):
        """존재하는 사업자등록번호"""
        service, mock_repo = mock_repos

        mock_repo.exists_by_business_number.return_value = True

        result = service.exists_by_business_number('123-45-67890')

        assert result is True

    def test_exists_by_business_number_false(self, mock_repos):
        """존재하지 않는 사업자등록번호"""
        service, mock_repo = mock_repos

        mock_repo.exists_by_business_number.return_value = False

        result = service.exists_by_business_number('000-00-00000')

        assert result is False


class TestCompanyServiceUpdate:
    """법인 정보 수정 테스트"""

    def test_update_company_info_success(self, mock_repos):
        """법인 정보 수정 성공"""
        service, mock_repo = mock_repos

        mock_company = Mock()
        mock_company.id = 1
        mock_company.name = 'Old Name'
        mock_company.to_dict = Mock(return_value={'id': 1, 'name': 'New Name'})
        mock_repo.find_by_id.return_value = mock_company

        with patch('app.services.company_service.atomic_transaction'):
            result = service.update_company_info(
                company_id=1,
                form_data={
                    'company_name': 'New Name',
                    'representative': 'CEO Name',
                    'phone': '02-1234-5678'
                }
            )

        assert isinstance(result, ServiceResult)
        assert result.success is True

    def test_update_company_info_not_found(self, mock_repos):
        """존재하지 않는 법인 수정"""
        service, mock_repo = mock_repos

        mock_repo.find_by_id.return_value = None

        result = service.update_company_info(
            company_id=999,
            form_data={'company_name': 'New Name'}
        )

        assert isinstance(result, ServiceResult)
        assert result.success is False

    def test_update_company_info_partial_data(self, mock_repos):
        """일부 데이터만 수정"""
        service, mock_repo = mock_repos

        mock_company = Mock()
        mock_company.id = 1
        mock_company.name = 'Original Name'
        mock_company.representative = 'Original Rep'
        mock_company.to_dict = Mock(return_value={'id': 1, 'name': 'Original Name'})
        mock_repo.find_by_id.return_value = mock_company

        with patch('app.services.company_service.atomic_transaction'):
            result = service.update_company_info(
                company_id=1,
                form_data={'phone': '02-9999-8888'}  # 전화번호만 수정
            )

        assert isinstance(result, ServiceResult)


class TestCompanyServiceIntegration:
    """통합 시나리오 테스트"""

    def test_get_and_update_flow(self, mock_repos):
        """조회 후 수정 플로우"""
        service, mock_repo = mock_repos

        # 조회
        mock_company = Mock()
        mock_company.id = 1
        mock_company.name = 'Test Corp'
        mock_company.to_dict = Mock(return_value={'id': 1, 'name': 'Updated Corp'})
        mock_repo.find_by_id.return_value = mock_company

        company = service.get_by_id(1)
        assert company is not None

        # 수정
        with patch('app.services.company_service.atomic_transaction'):
            result = service.update_company_info(
                company_id=1,
                form_data={'company_name': 'Updated Corp'}
            )

        assert result.success is True
