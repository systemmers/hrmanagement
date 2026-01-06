"""
User Domain

사용자 관련 모든 기능을 포함합니다:
- Models: User, CorporateAdminProfile, Notification, NotificationPreference
- Repositories: UserRepository, CorporateAdminProfileRepository, NotificationRepository, NotificationPreferenceRepository
- Services: UserService, UserEmployeeLinkService, NotificationService, CorporateAdminProfileService, PersonalService
- Blueprints: auth_bp, mypage_bp, account_bp

Phase 7: 도메인 중심 마이그레이션 완료
"""

# ========================================
# Repository 인스턴스 (지연 초기화)
# ========================================

_user_repo = None
_corporate_admin_profile_repo = None
_notification_repo = None
_notification_preference_repo = None
_personal_profile_repo = None


def init_repositories():
    """도메인 Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _user_repo, _corporate_admin_profile_repo
    global _notification_repo, _notification_preference_repo
    global _personal_profile_repo

    from .repositories import (
        UserRepository,
        CorporateAdminProfileRepository,
        NotificationRepository,
        NotificationPreferenceRepository,
        PersonalProfileRepository,
    )

    _user_repo = UserRepository()
    _corporate_admin_profile_repo = CorporateAdminProfileRepository()
    _notification_repo = NotificationRepository()
    _notification_preference_repo = NotificationPreferenceRepository()
    _personal_profile_repo = PersonalProfileRepository()


def get_user_repo():
    """UserRepository 인스턴스 반환"""
    return _user_repo


def get_corporate_admin_profile_repo():
    """CorporateAdminProfileRepository 인스턴스 반환"""
    return _corporate_admin_profile_repo


def get_notification_repo():
    """NotificationRepository 인스턴스 반환"""
    return _notification_repo


def get_notification_preference_repo():
    """NotificationPreferenceRepository 인스턴스 반환"""
    return _notification_preference_repo


def get_personal_profile_repo():
    """PersonalProfileRepository 인스턴스 반환"""
    return _personal_profile_repo


# ========================================
# Service 인스턴스 (지연 초기화)
# ========================================

_user_service = None
_user_employee_link_service = None
_notification_service = None
_corporate_admin_profile_service = None
_personal_service = None


def init_services():
    """도메인 Service 초기화

    extensions.py에서 호출됩니다.
    """
    global _user_service, _user_employee_link_service
    global _notification_service, _corporate_admin_profile_service
    global _personal_service

    from .services import (
        UserService,
        UserEmployeeLinkService,
        NotificationService,
        CorporateAdminProfileService,
        PersonalService,
    )

    _user_service = UserService()
    _user_employee_link_service = UserEmployeeLinkService()
    _notification_service = NotificationService()
    _corporate_admin_profile_service = CorporateAdminProfileService()
    _personal_service = PersonalService()


def get_user_service():
    """UserService 인스턴스 반환"""
    return _user_service


def get_user_employee_link_service():
    """UserEmployeeLinkService 인스턴스 반환"""
    return _user_employee_link_service


def get_notification_service():
    """NotificationService 인스턴스 반환"""
    return _notification_service


def get_corporate_admin_profile_service():
    """CorporateAdminProfileService 인스턴스 반환"""
    return _corporate_admin_profile_service


def get_personal_service():
    """PersonalService 인스턴스 반환"""
    return _personal_service


# ========================================
# 외부 인터페이스
# ========================================

__all__ = [
    # Repository Functions
    'init_repositories',
    'get_user_repo',
    'get_corporate_admin_profile_repo',
    'get_notification_repo',
    'get_notification_preference_repo',
    'get_personal_profile_repo',
    # Service Functions
    'init_services',
    'get_user_service',
    'get_user_employee_link_service',
    'get_notification_service',
    'get_corporate_admin_profile_service',
    'get_personal_service',
]
