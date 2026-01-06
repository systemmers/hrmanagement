"""
User Domain Models

Phase 2 Migration: 모델을 도메인 내부로 이동 완료
기존 경로(app.models.user, app.models.notification 등)에서도 import 가능
"""

# 도메인 내부에서 import
from .user import User
from .notification import Notification, NotificationPreference
from .corporate_admin_profile import CorporateAdminProfile
from .personal import PersonalProfile

__all__ = [
    'User',
    'Notification',
    'NotificationPreference',
    'CorporateAdminProfile',
    'PersonalProfile',
]
