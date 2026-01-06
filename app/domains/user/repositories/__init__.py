"""
User Domain Repositories

Phase 7: 도메인 중심 마이그레이션 완료
도메인 내 실제 구현 파일을 export
"""

# 도메인 내 실제 구현에서 import
from .user_repository import UserRepository, user_repository
from .notification_repository import (
    NotificationRepository,
    NotificationPreferenceRepository,
    notification_repository,
    notification_preference_repository,
)
from .corporate_admin_profile_repository import CorporateAdminProfileRepository
from .personal_profile_repository import (
    PersonalProfileRepository,
    personal_profile_repository,
)

__all__ = [
    # Classes
    'UserRepository',
    'CorporateAdminProfileRepository',
    'NotificationRepository',
    'NotificationPreferenceRepository',
    'PersonalProfileRepository',
    # Singleton instances
    'user_repository',
    'notification_repository',
    'notification_preference_repository',
    'personal_profile_repository',
]
