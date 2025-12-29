"""
알림 API Blueprint

Phase 5: 알림 시스템
- 알림 목록 조회
- 알림 읽음 처리
- 알림 설정 관리
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, request, session
from functools import wraps

from app.constants.session_keys import SessionKeys
from app.services.notification_service import notification_service
from app.models.notification import Notification
from app.utils.api_helpers import api_success, api_error, api_not_found

notifications_bp = Blueprint('notifications', __name__, url_prefix='/api/notifications')


# ===== 데코레이터 =====

def login_required(f):
    """로그인 필수 데코레이터"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if not session.get(SessionKeys.USER_ID):
            return api_error('로그인이 필요합니다.', status_code=401)
        return f(*args, **kwargs)
    return decorated_function


# ===== 알림 조회 API =====

@notifications_bp.route('', methods=['GET'])
@login_required
def get_notifications():
    """
    알림 목록 조회

    Query Params:
    - unread_only: 읽지 않은 알림만 (기본: false)
    - type: 알림 유형 필터 (선택)
    - limit: 조회 제한 (기본 50)
    - offset: 오프셋 (기본 0)

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
    읽지 않은 알림 개수

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
    알림 상세 조회

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


# ===== 알림 상태 관리 API =====

@notifications_bp.route('/<int:notification_id>/read', methods=['POST'])
@login_required
def mark_as_read(notification_id):
    """
    알림 읽음 처리

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
    모든 알림 읽음 처리

    Request Body (선택):
    {
        "type": "contract_request"  # 특정 유형만 읽음 처리
    }

    Response:
    {
        "success": true,
        "count": 10  # 읽음 처리된 알림 수
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
    알림 삭제

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


# ===== 알림 통계 API =====

@notifications_bp.route('/stats', methods=['GET'])
@login_required
def get_stats():
    """
    알림 통계 조회

    Query Params:
    - days: 조회 기간 (기본 30일)

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


# ===== 알림 설정 API =====

@notifications_bp.route('/preferences', methods=['GET'])
@login_required
def get_preferences():
    """
    알림 설정 조회

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
    알림 설정 업데이트

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


# ===== 알림 유형 정보 =====

@notifications_bp.route('/types', methods=['GET'])
@login_required
def get_notification_types():
    """
    알림 유형 목록

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
