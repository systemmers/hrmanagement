"""
ContractSettingsService 단위 테스트

계약 설정 서비스의 핵심 비즈니스 로직 테스트:
- 데이터 공유 설정 조회/수정
- 동기화 로그 조회
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.contract.services.contract_settings_service import (
    ContractSettingsService,
    contract_settings_service
)
from app.shared.base import ServiceResult


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_contract_repo = Mock()
    with patch.object(extensions, 'person_contract_repo', mock_contract_repo):
        yield contract_settings_service


class TestContractSettingsServiceInit:
    """ContractSettingsService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert contract_settings_service is not None
        assert isinstance(contract_settings_service, ContractSettingsService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(contract_settings_service, 'contract_repo')


class TestContractSettingsServiceSharingSettings:
    """데이터 공유 설정 테스트"""

    def test_get_sharing_settings_success(self, mock_repos):
        """데이터 공유 설정 조회 성공"""
        expected = {'share_basic_info': True, 'share_contact': True}
        mock_repos.contract_repo.get_sharing_settings.return_value = expected

        result = mock_repos.get_sharing_settings(contract_id=1)

        assert result == expected
        mock_repos.contract_repo.get_sharing_settings.assert_called_once_with(1)

    def test_get_sharing_settings_model(self, mock_repos, session):
        """데이터 공유 설정 모델 조회"""
        with patch('app.services.contract.contract_settings_service.DataSharingSettings') as mock_model:
            mock_settings = Mock()
            mock_model.query.filter_by.return_value.first.return_value = mock_settings

            result = mock_repos.get_sharing_settings_model(contract_id=1)

            assert result == mock_settings

    def test_update_sharing_settings_success(self, mock_repos):
        """데이터 공유 설정 업데이트 성공"""
        settings_data = {'share_basic_info': True, 'is_realtime_sync': False}
        expected = {'id': 1, **settings_data}
        mock_repos.contract_repo.update_sharing_settings.return_value = expected

        result = mock_repos.update_sharing_settings(contract_id=1, settings=settings_data)

        assert result.success is True
        assert result.data == expected

    def test_update_sharing_settings_error(self, mock_repos):
        """데이터 공유 설정 업데이트 실패"""
        mock_repos.contract_repo.update_sharing_settings.side_effect = ValueError('에러')

        result = mock_repos.update_sharing_settings(contract_id=1, settings={})

        assert result.success is False
        assert '에러' in result.message


class TestContractSettingsServiceSyncLogs:
    """동기화 로그 테스트"""

    def test_get_sync_logs_success(self, mock_repos):
        """동기화 로그 조회 성공"""
        expected = [{'id': 1, 'sync_type': 'manual'}]
        mock_repos.contract_repo.get_sync_logs.return_value = expected

        result = mock_repos.get_sync_logs(contract_id=1, limit=50)

        assert result == expected
        mock_repos.contract_repo.get_sync_logs.assert_called_once_with(1, 50)

    def test_get_sync_logs_filtered(self, mock_repos, session):
        """동기화 로그 필터링 조회"""
        with patch('app.services.contract.contract_settings_service.SyncLog') as mock_log:
            mock_log1 = Mock()
            mock_log1.to_dict.return_value = {'id': 1, 'sync_type': 'manual'}
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_log1]
            mock_log.query = mock_query

            result = mock_repos.get_sync_logs_filtered(contract_id=1, sync_type='manual', limit=50)

            assert len(result) == 1
            assert result[0]['sync_type'] == 'manual'

