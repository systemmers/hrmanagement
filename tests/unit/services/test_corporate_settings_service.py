"""
CorporateSettingsService 단위 테스트

법인 설정 서비스의 핵심 비즈니스 로직 테스트:
- 분류 옵션 관리
- 법인 설정 조회/수정
- 번호 카테고리 관리
"""
import pytest
from unittest.mock import Mock, patch

from app.services.corporate_settings_service import CorporateSettingsService


class TestCorporateSettingsServiceInit:
    """CorporateSettingsService 초기화 테스트"""

    def test_init(self):
        """서비스 초기화"""
        service = CorporateSettingsService()
        assert service is not None
        assert hasattr(service, 'classification_repo')
        assert hasattr(service, 'settings_repo')
        assert hasattr(service, 'number_category_repo')


class TestCorporateSettingsServiceClassifications:
    """분류 옵션 관리 테스트"""

    def test_get_all_classifications(self):
        """모든 분류 옵션 조회"""
        service = CorporateSettingsService()
        expected = {'departments': [], 'positions': []}
        mock_repo = Mock()
        mock_repo.get_all_options.return_value = expected
        service.classification_repo = mock_repo

        result = service.get_all_classifications(company_id=1)

        assert result == expected
        mock_repo.get_all_options.assert_called_once_with(1)

    def test_get_organization_options(self):
        """조직 구조 분류 옵션 조회"""
        service = CorporateSettingsService()
        expected = {'departments': []}
        mock_repo = Mock()
        mock_repo.get_organization_options.return_value = expected
        service.classification_repo = mock_repo

        result = service.get_organization_options(company_id=1)

        assert result == expected

    def test_get_employment_options(self):
        """고용 정책 분류 옵션 조회"""
        service = CorporateSettingsService()
        expected = {'positions': []}
        mock_repo = Mock()
        mock_repo.get_employment_options.return_value = expected
        service.classification_repo = mock_repo

        result = service.get_employment_options(company_id=1)

        assert result == expected

    def test_get_classifications_by_category(self):
        """카테고리별 분류 옵션 조회"""
        service = CorporateSettingsService()
        expected = [{'id': 1, 'value': '개발팀'}]
        mock_repo = Mock()
        mock_repo.get_by_category_for_company.return_value = expected
        service.classification_repo = mock_repo

        result = service.get_classifications_by_category('department', company_id=1)

        assert result == expected
        mock_repo.get_by_category_for_company.assert_called_once_with('department', 1)

    def test_add_classification(self):
        """분류 옵션 추가"""
        service = CorporateSettingsService()
        expected = {'id': 1, 'category': 'department', 'value': 'DEV', 'label': '개발팀'}
        mock_repo = Mock()
        mock_repo.add_option_for_company.return_value = expected
        service.classification_repo = mock_repo

        result = service.add_classification(
            company_id=1,
            category='department',
            value='DEV',
            label='개발팀'
        )

        assert result == expected
        mock_repo.add_option_for_company.assert_called_once()

    def test_update_classification(self):
        """분류 옵션 수정"""
        service = CorporateSettingsService()
        expected = {'id': 1, 'label': '개발부서'}
        mock_repo = Mock()
        mock_repo.update_option.return_value = expected
        service.classification_repo = mock_repo

        result = service.update_classification(
            option_id=1,
            company_id=1,
            data={'label': '개발부서'}
        )

        assert result == expected

    def test_delete_classification(self):
        """분류 옵션 삭제"""
        service = CorporateSettingsService()
        mock_repo = Mock()
        mock_repo.delete_option_for_company.return_value = True
        service.classification_repo = mock_repo

        result = service.delete_classification(option_id=1, company_id=1)

        assert result is True
        mock_repo.delete_option_for_company.assert_called_once_with(1, 1)

    def test_toggle_system_option(self):
        """시스템 옵션 활성화/비활성화"""
        service = CorporateSettingsService()
        expected = {'success': True}
        mock_repo = Mock()
        mock_repo.toggle_system_option.return_value = expected
        service.classification_repo = mock_repo

        result = service.toggle_system_option(
            company_id=1,
            category='department',
            value='DEV',
            is_active=True
        )

        assert result == expected


class TestCorporateSettingsServiceSettings:
    """법인 설정 관리 테스트"""

    def test_get_settings(self):
        """법인 설정 조회"""
        service = CorporateSettingsService()
        expected = {'key1': 'value1'}
        mock_repo = Mock()
        mock_repo.get_by_company.return_value = expected
        service.settings_repo = mock_repo

        result = service.get_settings(company_id=1)

        assert result == expected


class TestCorporateSettingsServiceNumberCategory:
    """번호 카테고리 관리 테스트"""

    def test_get_number_categories(self):
        """번호 카테고리 조회"""
        service = CorporateSettingsService()
        expected = [{'id': 1, 'code': 'EMP'}]
        mock_repo = Mock()
        mock_repo.get_by_company.return_value = expected
        service.number_category_repo = mock_repo

        result = service.get_number_categories(company_id=1)

        assert result == expected

