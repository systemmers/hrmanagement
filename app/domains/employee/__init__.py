# app/domains/employee/__init__.py
"""
직원 도메인 패키지

직원 관련 모든 기능을 포함합니다:
- 직원 CRUD
- 직원 관계형 데이터 (학력, 경력, 자격증 등)
- 직원 첨부파일
"""

# Repository 인스턴스 (지연 초기화)
_employee_repo = None
_education_repo = None
_career_repo = None
_certificate_repo = None
_family_member_repo = None
_language_repo = None
_military_service_repo = None
_attachment_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _employee_repo, _education_repo, _career_repo
    global _certificate_repo, _family_member_repo, _language_repo
    global _military_service_repo, _attachment_repo

    # Phase 3에서 실제 Repository import 및 초기화 예정
    pass


def get_employee_repo():
    return _employee_repo


def get_education_repo():
    return _education_repo


def get_career_repo():
    return _career_repo


def get_certificate_repo():
    return _certificate_repo


def get_family_member_repo():
    return _family_member_repo


def get_language_repo():
    return _language_repo


def get_military_service_repo():
    return _military_service_repo


def get_attachment_repo():
    return _attachment_repo
