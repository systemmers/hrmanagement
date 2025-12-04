"""
멀티테넌시 헬퍼 모듈

현재 로그인한 사용자의 회사/조직 정보를 조회하는 유틸리티 함수를 제공합니다.
세션 기반으로 멀티테넌시 필터링에 필요한 ID를 반환합니다.
"""
from flask import session

from ..models.company import Company


def get_current_company_id():
    """현재 회사 ID 반환

    Returns:
        int or None: 회사 ID (로그인하지 않은 경우 None)
    """
    return session.get('company_id')


def get_current_company():
    """현재 회사 객체 반환

    Returns:
        Company or None: 회사 객체 (없는 경우 None)
    """
    company_id = session.get('company_id')
    if not company_id:
        return None
    return Company.query.get(company_id)


def get_current_organization_id():
    """현재 로그인한 회사의 root_organization_id 반환

    멀티테넌시 필터링에 사용됩니다.
    직원, 조직 등의 데이터를 현재 회사 범위로 제한할 때 사용합니다.

    Returns:
        int or None: 조직 ID (회사가 없거나 설정되지 않은 경우 None)
    """
    company_id = session.get('company_id')
    if not company_id:
        return None
    company = Company.query.get(company_id)
    return company.root_organization_id if company else None


def get_current_user_id():
    """현재 로그인한 사용자 ID 반환

    Returns:
        int or None: 사용자 ID (로그인하지 않은 경우 None)
    """
    return session.get('user_id')


def get_current_account_type():
    """현재 로그인한 계정 타입 반환

    Returns:
        str or None: 'personal', 'corporate', 'employee_sub' 중 하나 (로그인하지 않은 경우 None)
    """
    return session.get('account_type')


def is_corporate_account():
    """현재 로그인한 계정이 법인 계정인지 확인

    Returns:
        bool: 법인 계정이면 True
    """
    return session.get('account_type') == 'corporate'


def is_personal_account():
    """현재 로그인한 계정이 개인 계정인지 확인

    Returns:
        bool: 개인 계정이면 True
    """
    return session.get('account_type') == 'personal'
