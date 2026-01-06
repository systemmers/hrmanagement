# app/domains/user/__init__.py
"""
사용자 도메인 패키지

사용자 관련 모든 기능을 포함합니다:
- 사용자 CRUD
- 인증/권한
- 알림
"""

_user_repo = None
_notification_repo = None
_corporate_admin_profile_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _user_repo, _notification_repo, _corporate_admin_profile_repo
    # Phase 6에서 실제 Repository import 및 초기화 예정
    pass


def get_user_repo():
    return _user_repo


def get_notification_repo():
    return _notification_repo


def get_corporate_admin_profile_repo():
    return _corporate_admin_profile_repo
