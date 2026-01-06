"""
사번 자동생성 유틸리티

형식: {PREFIX}-{YYYY}-{NNNN} (예: EMP-2025-0001)
SystemSetting을 통해 설정 가능
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from datetime import datetime


# 지연 초기화용
_employee_repo = None


def _get_employee_repo():
    """지연 초기화된 Employee Repository"""
    global _employee_repo
    if _employee_repo is None:
        from app.domains.employee.repositories import employee_repository
        _employee_repo = employee_repository
    return _employee_repo


def get_employee_number_config():
    """
    시스템 설정에서 사번 생성 규칙 조회

    Returns:
        dict: 사번 설정 정보
    """
    from app.extensions import system_setting_repo

    if system_setting_repo:
        return system_setting_repo.get_employee_number_config()

    # 기본값
    return {
        'prefix': 'EMP',
        'separator': '-',
        'include_year': True,
        'sequence_digits': 4,
        'auto_generate': True,
    }


def generate_employee_number():
    """
    새 사번 생성 (시스템 설정 기반)

    Returns:
        str: 새 사번 (예: EMP-2025-0001)
    """
    config = get_employee_number_config()

    prefix = config.get('prefix', 'EMP')
    separator = config.get('separator', '-')
    include_year = config.get('include_year', True)
    digits = config.get('sequence_digits', 4)

    year = datetime.now().year

    # 패턴에 따라 마지막 사번 조회
    if include_year:
        pattern = f'{prefix}{separator}{year}{separator}%'
    else:
        pattern = f'{prefix}{separator}%'

    # Phase 31: Repository 패턴 적용
    last_employee = _get_employee_repo().find_last_by_number_pattern(pattern)

    if last_employee and last_employee.employee_number:
        # 마지막 순번 추출 후 +1
        try:
            parts = last_employee.employee_number.split(separator)
            last_seq = int(parts[-1])
            new_seq = last_seq + 1
        except (IndexError, ValueError):
            new_seq = 1
    else:
        new_seq = 1

    # 사번 포맷팅
    if include_year:
        return f'{prefix}{separator}{year}{separator}{new_seq:0{digits}d}'
    else:
        return f'{prefix}{separator}{new_seq:0{digits}d}'


def is_valid_employee_number(employee_number):
    """
    사번 형식 검증 (시스템 설정 기반)

    Args:
        employee_number: 검증할 사번

    Returns:
        bool: 유효 여부
    """
    if not employee_number:
        return False

    config = get_employee_number_config()
    prefix = config.get('prefix', 'EMP')
    separator = config.get('separator', '-')
    include_year = config.get('include_year', True)
    digits = config.get('sequence_digits', 4)

    parts = employee_number.split(separator)

    if include_year:
        if len(parts) != 3:
            return False
        emp_prefix, year, seq = parts

        if emp_prefix != prefix:
            return False

        try:
            year_int = int(year)
            if year_int < 2000 or year_int > 2100:
                return False
        except ValueError:
            return False
    else:
        if len(parts) != 2:
            return False
        emp_prefix, seq = parts

        if emp_prefix != prefix:
            return False

    try:
        seq_int = int(seq)
        max_seq = 10 ** digits - 1
        if seq_int < 1 or seq_int > max_seq:
            return False
    except ValueError:
        return False

    return True


def is_employee_number_exists(employee_number, exclude_id=None):
    """
    사번 중복 확인

    Args:
        employee_number: 확인할 사번
        exclude_id: 제외할 직원 ID (수정 시 사용)

    Returns:
        bool: 존재 여부
    """
    # Phase 31: Repository 패턴 적용
    return _get_employee_repo().exists_by_employee_number(employee_number, exclude_id)
