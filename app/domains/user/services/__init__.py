"""
User Domain Services

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현이 이 디렉토리에 위치합니다.
"""

# 로컬 서비스에서 import
from .user_service import UserService, user_service
from .user_employee_link_service import UserEmployeeLinkService, user_employee_link_service
from .notification_service import NotificationService, notification_service
from .corporate_admin_profile_service import CorporateAdminProfileService, corporate_admin_profile_service
from .personal_service import PersonalService, personal_service

__all__ = [
    # Classes
    'UserService',
    'UserEmployeeLinkService',
    'NotificationService',
    'CorporateAdminProfileService',
    'PersonalService',
    # Singleton instances
    'user_service',
    'user_employee_link_service',
    'notification_service',
    'corporate_admin_profile_service',
    'personal_service',
]
