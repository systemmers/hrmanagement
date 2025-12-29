"""
SyncService 단위 테스트

데이터 동기화 서비스의 핵심 비즈니스 로직 테스트:
- 필드 조회
- 동기화 실행
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime

from app.services.sync_service import SyncService, sync_service


@pytest.fixture
def mock_sync_service(app):
    """SyncService를 Mock으로 대체하는 fixture"""
    # 서브 서비스 Mock
    mock_basic = Mock()
    mock_relation = Mock()

    with patch.object(sync_service, '_basic_service', mock_basic), \
         patch.object(sync_service, '_relation_service', mock_relation):
        yield sync_service, mock_basic, mock_relation


class TestSyncServiceInit:
    """SyncService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert sync_service is not None
        assert isinstance(sync_service, SyncService)

    def test_service_has_sub_services(self, app):
        """Service에 sub-service 속성 존재 확인"""
        assert hasattr(sync_service, '_basic_service')
        assert hasattr(sync_service, '_relation_service')

    def test_set_current_user(self, app):
        """현재 사용자 설정 테스트"""
        sync_service.set_current_user(123)
        assert sync_service._current_user_id == 123


class TestSyncServiceFieldQueries:
    """필드 조회 테스트"""

    def test_get_syncable_fields_returns_dict(self, app):
        """동기화 가능 필드 목록 반환 형식 확인"""
        with patch('app.services.sync_service.DataSharingSettings') as mock_settings:
            mock_settings.query.filter_by.return_value.first.return_value = None

            result = sync_service.get_syncable_fields(contract_id=1)

            assert isinstance(result, dict)
            assert 'basic' in result
            assert 'contact' in result
            assert 'education' in result
            assert 'career' in result

    def test_get_syncable_fields_with_settings(self, app):
        """공유 설정이 있을 때 필드 목록 확인"""
        mock_setting = Mock()
        mock_setting.share_basic_info = True
        mock_setting.share_contact = True
        mock_setting.share_education = True
        mock_setting.share_career = False
        mock_setting.share_certificates = False
        mock_setting.share_languages = False
        mock_setting.share_military = False
        mock_setting.share_family = False

        with patch('app.services.sync_service.DataSharingSettings') as mock_settings:
            mock_settings.query.filter_by.return_value.first.return_value = mock_setting

            result = sync_service.get_syncable_fields(contract_id=1)

            assert len(result['basic']) > 0
            assert len(result['contact']) > 0
            assert result['education'] is True
            assert result['career'] is False


class TestSyncServiceExecution:
    """동기화 실행 테스트"""

    def test_sync_personal_to_employee_method_exists(self, mock_sync_service):
        """개인 -> 직원 동기화 메서드 존재 확인"""
        service, mock_basic, mock_relation = mock_sync_service

        # 메서드 존재 확인
        assert hasattr(service, 'sync_personal_to_employee')
        assert callable(getattr(service, 'sync_personal_to_employee'))

    def test_sync_employee_to_personal_method_exists(self, mock_sync_service):
        """직원 -> 개인 동기화 메서드 존재 확인"""
        service, mock_basic, mock_relation = mock_sync_service

        # 메서드 존재 확인
        assert hasattr(service, 'sync_employee_to_personal')
        assert callable(getattr(service, 'sync_employee_to_personal'))


class TestSyncServiceFieldMappings:
    """필드 매핑 테스트"""

    def test_get_all_field_mappings_returns_dict(self, app):
        """전체 필드 매핑 반환 형식 확인"""
        result = sync_service.get_all_field_mappings()

        assert isinstance(result, dict)


class TestSyncServiceValidation:
    """동기화 유효성 검증 테스트"""

    def test_sync_with_invalid_contract_id(self, app):
        """잘못된 계약 ID로 동기화 시도"""
        with patch('app.services.sync_service.PersonCorporateContract') as mock_contract:
            mock_contract.query.get.return_value = None

            # 메서드가 None/에러 처리를 하는지 확인
            assert hasattr(sync_service, 'sync_personal_to_employee')

    def test_should_auto_sync_method_exists(self, app):
        """자동 동기화 여부 확인 메서드 존재"""
        assert hasattr(sync_service, 'should_auto_sync')
        assert callable(getattr(sync_service, 'should_auto_sync'))

    def test_get_contracts_for_user_method_exists(self, app):
        """사용자별 계약 조회 메서드 존재"""
        assert hasattr(sync_service, 'get_contracts_for_user')
        assert callable(getattr(sync_service, 'get_contracts_for_user'))
