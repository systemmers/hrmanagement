# app/domains/platform/__init__.py
"""
플랫폼 도메인 패키지

플랫폼 관리 기능을 포함합니다:
- 시스템 설정
- 플랫폼 대시보드
"""

_system_setting_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _system_setting_repo
    # Phase 7에서 실제 Repository import 및 초기화 예정
    pass


def get_system_setting_repo():
    return _system_setting_repo
