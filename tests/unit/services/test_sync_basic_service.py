"""
SyncBasicService 단위 테스트

기본 필드 동기화 서비스의 핵심 비즈니스 로직 테스트:
- 개인 프로필 -> 직원 기본 필드 동기화
- 직원 -> 개인 프로필 기본 필드 동기화
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.sync.services.sync_basic_service import SyncBasicService


class TestSyncBasicServiceInit:
    """SyncBasicService 초기화 테스트"""

    def test_init_without_user(self):
        """사용자 없이 초기화"""
        service = SyncBasicService()
        assert service._current_user_id is None

    def test_init_with_user(self):
        """사용자와 함께 초기화"""
        service = SyncBasicService(current_user_id=1)
        assert service._current_user_id == 1

    def test_set_current_user(self):
        """현재 사용자 설정"""
        service = SyncBasicService()
        service.set_current_user(2)
        assert service._current_user_id == 2


class TestSyncBasicServiceSyncPersonalToEmployee:
    """개인 프로필 -> 직원 동기화 테스트"""

    def test_sync_personal_to_employee_with_changes(self, session):
        """변경사항이 있을 때 동기화"""
        service = SyncBasicService(current_user_id=1)

        mock_profile = Mock()
        mock_profile.name = '홍길동'
        mock_profile.email = 'hong@test.com'

        mock_employee = Mock()
        mock_employee.name = '김철수'
        mock_employee.email = 'kim@test.com'

        target_fields = ['name', 'email']
        field_mapper = lambda f: f

        with patch('app.services.sync.sync_basic_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_basic_service.db') as mock_db:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance

            result = service.sync_personal_to_employee(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                target_fields=target_fields,
                field_mapper=field_mapper,
                sync_type='manual'
            )

            assert len(result['synced_fields']) == 2
            assert len(result['changes']) == 2
            assert len(result['log_ids']) == 2

    def test_sync_personal_to_employee_no_changes(self, session):
        """변경사항이 없을 때"""
        service = SyncBasicService(current_user_id=1)

        mock_profile = Mock()
        mock_profile.name = '홍길동'

        mock_employee = Mock()
        mock_employee.name = '홍길동'

        target_fields = ['name']
        field_mapper = lambda f: f

        result = service.sync_personal_to_employee(
            contract_id=1,
            profile=mock_profile,
            employee=mock_employee,
            target_fields=target_fields,
            field_mapper=field_mapper
        )

        assert len(result['synced_fields']) == 0
        assert len(result['changes']) == 0


class TestSyncBasicServiceSyncEmployeeToPersonal:
    """직원 -> 개인 프로필 동기화 테스트"""

    def test_sync_employee_to_personal_with_changes(self, session):
        """변경사항이 있을 때 역방향 동기화"""
        service = SyncBasicService(current_user_id=1)

        mock_profile = Mock()
        mock_profile.name = '홍길동'

        mock_employee = Mock()
        mock_employee.name = '김철수'

        target_fields = ['name']
        field_mapper = lambda f: f

        with patch('app.services.sync.sync_basic_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_basic_service.db') as mock_db:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance

            result = service.sync_employee_to_personal(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                target_fields=target_fields,
                field_mapper=field_mapper
            )

            assert len(result['synced_fields']) == 1
            assert len(result['changes']) == 1


class TestSyncBasicServiceSerializeValue:
    """값 직렬화 테스트"""

    def test_serialize_string(self):
        """문자열 직렬화"""
        service = SyncBasicService()
        result = service._serialize_value('test')
        assert result == 'test'

    def test_serialize_int(self):
        """정수 직렬화"""
        service = SyncBasicService()
        result = service._serialize_value(123)
        assert result == '123'

    def test_serialize_none(self):
        """None 직렬화"""
        service = SyncBasicService()
        result = service._serialize_value(None)
        assert result is None

    def test_serialize_datetime(self):
        """날짜시간 직렬화"""
        from datetime import datetime
        service = SyncBasicService()
        dt = datetime(2024, 1, 1, 12, 0, 0)
        result = service._serialize_value(dt)
        assert '2024-01-01' in result

