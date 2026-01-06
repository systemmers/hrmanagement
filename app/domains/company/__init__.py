# app/domains/company/__init__.py
"""
법인 도메인 패키지

법인 관련 모든 기능을 포함합니다:
- 법인 CRUD
- 조직 구조
- 법인 설정
- 분류 옵션
"""

_company_repo = None
_organization_repo = None
_company_settings_repo = None
_classification_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _company_repo, _organization_repo
    global _company_settings_repo, _classification_repo
    # Phase 5에서 실제 Repository import 및 초기화 예정
    pass


def get_company_repo():
    return _company_repo


def get_organization_repo():
    return _organization_repo


def get_company_settings_repo():
    return _company_settings_repo


def get_classification_repo():
    return _classification_repo
