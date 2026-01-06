"""
User Domain: Notifications API Blueprint

Phase 1 Migration: domains/user/blueprints/notifications.py
- Notification list and detail
- Read/unread status management
- Notification preferences
"""
from flask import Blueprint, request, session
from functools import wraps

from app.shared.constants.session_keys import SessionKeys
from app.services.notification_service import notification_service
from app.domains.user.models import Notification
from app.shared.utils.api_helpers import api_success, api_error, api_not_found

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


# ===== Decorators =====

def login_required(f):
    """Login required decorator"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(SessionKeys.USER_ID):
            return api_error('로그인이 필요합니다.', status_code=401)
        return f(*args, **kwargs)
    return decorated_function


# ===== Notification Query API =====

@notifications_bp.route('', methods=['GET'])
@login_required
def get_notifications():
    """
    Get notification list

    Query Params:
    - unread_only: Only unread notifications (default: false)
    - type: Notification type filter (optional)
    - limit: Query limit (default 50)
    - offset: Offset (default 0)

    Response:
    {
        "success": true,
        "notifications": [...],
        "unread_count": 5,
        "total": 50
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    unread_only = request.args.get('unread_only', 'false').lower() == 'true'
    notification_type = request.args.get('type')
    limit = request.args.get('limit', 50, type=int)
    offset = request.args.get('offset', 0, type=int)

    notifications = notification_service.get_notifications(
        user_id=user_id,
        unread_only=unread_only,
        notification_type=notification_type,
        limit=limit,
        offset=offset
    )

    unread_count = notification_service.get_unread_count(user_id)

    return api_success({
        'notifications': notifications,
        'unread_count': unread_count,
        'limit': limit,
        'offset': offset
    })


@notifications_bp.route('/count', methods=['GET'])
@login_required
def get_unread_count():
    """
    Get unread notification count

    Response:
    {
        "success": true,
        "count": 5
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    count = notification_service.get_unread_count(user_id)

    return api_success({'count': count})


@notifications_bp.route('/<int:notification_id>', methods=['GET'])
@login_required
def get_notification(notification_id):
    """
    Get notification detail

    Response:
    {
        "success": true,
        "notification": {...}
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    notification = notification_service.get_notification(
        notification_id=notification_id,
        user_id=user_id
    )

    if not notification:
        return api_not_found('알림')

    return api_success({'notification': notification})


# ===== Notification Status API =====

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """
    Mark notification as read

    Response:
    {
        "success": true
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    result = notification_service.mark_as_read(
        notification_id=notification_id,
        user_id=user_id
    )

    if not result:
        return api_not_found('알림')

    return api_success()


@notifications_bp.route('/read-all', methods=['POST'])
@login_required
def mark_all_as_read():
    """
    Mark all notifications as read

    Request Body (optional):
    {
        "type": "contract_request"  # Mark only specific type as read
    }

    Response:
    {
        "success": true,
        "count": 10  # Number of notifications marked as read
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json() or {}
    notification_type = data.get('type')

    count = notification_service.mark_all_as_read(
        user_id=user_id,
        notification_type=notification_type
    )

    return api_success({'count': count})


@notifications_bp.route('/<int:notification_id>', methods=['DELETE'])
@login_required
def delete_notification(notification_id):
    """
    Delete notification

    Response:
    {
        "success": true
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    result = notification_service.delete_notification(
        notification_id=notification_id,
        user_id=user_id
    )

    if not result:
        return api_not_found('알림')

    return api_success()


# ===== Notification Stats API =====

@notifications_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """
    Get notification statistics

    Query Params:
    - days: Query period (default 30 days)

    Response:
    {
        "success": true,
        "stats": {
            "total": 100,
            "unread": 5,
            "by_type": {...},
            "period_days": 30
        }
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    days = request.args.get('days', 30, type=int)

    stats = notification_service.get_notification_stats(
        user_id=user_id,
        days=days
    )

    return api_success({'stats': stats})


# ===== Notification Preferences API =====

@notifications_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """
    Get notification preferences

    Response:
    {
        "success": true,
        "preferences": {...}
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    preferences = notification_service.get_preferences(user_id)

    return api_success({'preferences': preferences})


@notifications_bp.route('/preferences', methods=['PUT'])
@login_required
def update_preferences():
    """
    Update notification preferences

    Request Body:
    {
        "receive_contract_notifications": true,
        "receive_sync_notifications": true,
        "receive_termination_notifications": true,
        "receive_system_notifications": true,
        "email_notifications_enabled": false,
        "email_digest_frequency": "none"
    }

    Response:
    {
        "success": true,
        "preferences": {...}
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json()

    if not data:
        return api_error('설정 데이터가 필요합니다.')

    preferences = notification_service.update_preferences(
        user_id=user_id,
        settings=data
    )

    return api_success({'preferences': preferences})


# ===== Notification Types Info =====

@notifications_bp.route('/types', methods=['GET'])
@login_required
def get_notification_types():
    """
    Get notification types list

    Response:
    {
        "success": true,
        "types": [...]
    }
    """
    types = [
        {'value': value, 'label': label}
        for value, label in Notification.NOTIFICATION_TYPES
    ]

    return api_success({'types': types})
