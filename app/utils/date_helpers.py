"""
날짜 파싱 헬퍼 함수

DRY 원칙 적용: 폼 및 API 요청의 날짜 파싱 로직 중앙화

Usage:
    from app.utils.date_helpers import parse_form_date, parse_iso_date

    # 폼 날짜 파싱 (%Y-%m-%d)
    contract_start = parse_form_date(request.form.get('contract_start_date'))

    # ISO 날짜 파싱
    start_date = parse_iso_date(request.args.get('start_date'))
"""
from datetime import datetime, date
from typing import Optional


def parse_form_date(date_str: str) -> Optional[date]:
    """폼 날짜 문자열을 date 객체로 변환

    Args:
        date_str: 'YYYY-MM-DD' 형식의 날짜 문자열

    Returns:
        date 객체 또는 None (파싱 실패 시)

    Example:
        >>> parse_form_date('2025-01-06')
        datetime.date(2025, 1, 6)
        >>> parse_form_date('')
        None
        >>> parse_form_date('invalid')
        None
    """
    if not date_str:
        return None
    try:
        return datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        return None


def parse_iso_date(date_str: str) -> Optional[datetime]:
    """ISO 형식 날짜 문자열을 datetime 객체로 변환

    Args:
        date_str: ISO 형식 날짜 문자열 (예: '2025-01-06T10:30:00')

    Returns:
        datetime 객체 또는 None (파싱 실패 시)

    Example:
        >>> parse_iso_date('2025-01-06T10:30:00')
        datetime.datetime(2025, 1, 6, 10, 30)
        >>> parse_iso_date('2025-01-06')
        datetime.datetime(2025, 1, 6, 0, 0)
        >>> parse_iso_date('')
        None
    """
    if not date_str:
        return None
    try:
        return datetime.fromisoformat(date_str)
    except ValueError:
        return None
