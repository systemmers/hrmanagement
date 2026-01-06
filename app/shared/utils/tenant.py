"""
멀티테넌시 헬퍼 모듈

현재 로그인한 사용자의 회사/조직 정보를 조회하는 유틸리티 함수를 제공합니다.
세션 기반으로 멀티테넌시 필터링에 필요한 ID를 반환합니다.
Phase 6: 백엔드 리팩토링 - 요청 스코프 캐싱 추가
Phase 8: 상수 모듈 적용
"""
from flask import session, g

from ..constants.session_keys import SessionKeys, AccountType
from app.models import Company


def get_current_company_id():
    """현재 회사 ID 반환

    Returns:
        int or None: 회사 ID (로그인하지 않은 경우 None)
    """
    return session.get(SessionKeys.COMPANY_ID)


def get_current_company():
    """현재 회사 객체 반환 (요청 스코프 캐싱)

    동일 요청 내에서 여러 번 호출해도 DB는 한 번만 조회합니다.

    Returns:
        Company or None: 회사 객체 (없는 경우 None)
    """
    if hasattr(g, '_current_company'):
        return g._current_company

    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        g._current_company = None
        return None

    company = Company.query.get(company_id)
    g._current_company = company
    return company


def get_current_organization_id():
    """현재 로그인한 회사의 root_organization_id 반환 (요청 스코프 캐싱)

    멀티테넌시 필터링에 사용됩니다.
    직원, 조직 등의 데이터를 현재 회사 범위로 제한할 때 사용합니다.
    동일 요청 내에서 여러 번 호출해도 DB는 한 번만 조회합니다.

    Returns:
        int or None: 조직 ID (회사가 없거나 설정되지 않은 경우 None)
    """
    if hasattr(g, '_current_organization_id'):
        return g._current_organization_id

    company = get_current_company()
    org_id = company.root_organization_id if company else None
    g._current_organization_id = org_id
    return org_id


def get_current_user_id():
    """현재 로그인한 사용자 ID 반환

    Returns:
        int or None: 사용자 ID (로그인하지 않은 경우 None)
    """
    return session.get(SessionKeys.USER_ID)


def get_current_account_type():
    """현재 로그인한 계정 타입 반환

    Returns:
        str or None: 'personal', 'corporate', 'employee_sub' 중 하나 (로그인하지 않은 경우 None)
    """
    return session.get(SessionKeys.ACCOUNT_TYPE)


def is_corporate_account():
    """현재 로그인한 계정이 법인 계정인지 확인

    Returns:
        bool: 법인 계정이면 True
    """
    return session.get(SessionKeys.ACCOUNT_TYPE) == AccountType.CORPORATE


def is_personal_account():
    """현재 로그인한 계정이 개인 계정인지 확인

    Returns:
        bool: 개인 계정이면 True
    """
    return session.get(SessionKeys.ACCOUNT_TYPE) == AccountType.PERSONAL
