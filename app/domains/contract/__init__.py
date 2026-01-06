# app/domains/contract/__init__.py
"""
계약 도메인 패키지

계약 관련 모든 기능을 포함합니다:
- 계약 요청/승인/거절
- 계약 종료
- 계약 설정
"""

_person_contract_repo = None


def init_repositories():
    """도메인 Repository 초기화"""
    global _person_contract_repo
    # Phase 4에서 실제 Repository import 및 초기화 예정
    pass


def get_person_contract_repo():
    return _person_contract_repo
