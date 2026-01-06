"""
User Domain Models

Phase 6: 도메인 중심 마이그레이션
기존 모델을 re-export하여 점진적 마이그레이션 지원
"""

# 기존 모델에서 re-export (중복 정의 방지)
from app.models.user import User
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.models.notification import Notification, NotificationPreference

__all__ = [
    'User',
    'CorporateAdminProfile',
    'Notification',
    'NotificationPreference',
]
