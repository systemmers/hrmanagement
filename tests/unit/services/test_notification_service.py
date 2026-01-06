"""
NotificationService 단위 테스트

알림 서비스의 핵심 비즈니스 로직 테스트:
- 알림 생성
- 알림 조회
- 읽음 처리
"""
import pytest
from unittest.mock import Mock, patch

from app.services.notification_service import NotificationService, notification_service


class TestNotificationServiceInit:
    """NotificationService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert notification_service is not None
        assert isinstance(notification_service, NotificationService)


class TestNotificationServiceCreate:
    """알림 생성 테스트"""

    def test_create_notification_success(self, session):
        """알림 생성 성공"""
        with patch('app.services.notification_service.Notification') as mock_notif, \
             patch('app.services.notification_service.NotificationPreference') as mock_pref, \
             patch('app.services.notification_service.db') as mock_db:
            mock_pref.query.filter_by.return_value.first.return_value = None
            mock_notif_instance = Mock()
            mock_notif.return_value = mock_notif_instance

            result = notification_service.create_notification(
                user_id=1,
                notification_type='contract_request',
                title='테스트 알림',
                message='테스트 메시지'
            )

            assert result is not None

    def test_create_notification_preference_disabled(self, session):
        """알림 수신 설정이 비활성화된 경우"""
        with patch('app.services.notification_service.NotificationPreference') as mock_pref:
            mock_pref_instance = Mock()
            mock_pref_instance.receive_contract_notifications = False
            mock_pref.query.filter_by.return_value.first.return_value = mock_pref_instance

            result = notification_service.create_notification(
                user_id=1,
                notification_type='contract_request',
                title='테스트 알림'
            )

            assert result is None


class TestNotificationServiceQueries:
    """알림 조회 테스트"""

    def test_get_user_notifications_success(self, session):
        """사용자 알림 조회 성공"""
        from datetime import datetime
        with patch('app.services.notification_service.Notification') as mock_notif, \
             patch('app.services.notification_service.db') as mock_db:
            mock_db.or_.return_value = Mock()
            mock_notif_instance = Mock()
            mock_notif_instance.to_dict.return_value = {'id': 1, 'title': 'Test'}
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_notif_instance]
            mock_notif.query = mock_query
            mock_notif.expires_at.is_.return_value = Mock()
            mock_notif.expires_at.__gt__ = Mock(return_value=Mock())

            result = notification_service.get_notifications(user_id=1, limit=10)

            assert isinstance(result, list)

    def test_get_unread_count_success(self, session):
        """미읽음 알림 수 조회 성공"""
        from datetime import datetime
        with patch('app.services.notification_service.Notification') as mock_notif, \
             patch('app.services.notification_service.db') as mock_db:
            mock_db.or_.return_value = Mock()
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.count.return_value = 5
            mock_notif.query = mock_query
            mock_notif.expires_at.is_.return_value = Mock()
            mock_notif.expires_at.__gt__ = Mock(return_value=Mock())

            result = notification_service.get_unread_count(user_id=1)

            assert result == 5


class TestNotificationServiceMarkRead:
    """알림 읽음 처리 테스트"""

    def test_mark_as_read_success(self, session):
        """알림 읽음 처리 성공"""
        with patch('app.services.notification_service.Notification') as mock_notif, \
             patch('app.services.notification_service.db') as mock_db:
            mock_notif_instance = Mock()
            mock_notif_instance.mark_as_read = Mock()
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.first.return_value = mock_notif_instance
            mock_notif.query = mock_query
            mock_db.session.commit = Mock()

            result = notification_service.mark_as_read(notification_id=1, user_id=1)

            assert result is True
            mock_notif_instance.mark_as_read.assert_called_once()

