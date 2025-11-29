"""
사번 자동생성 유틸리티

형식: EMP-YYYY-NNNN (예: EMP-2025-0001)
"""
from datetime import datetime
from app.database import db
from app.models.employee import Employee


def generate_employee_number():
    """
    새 사번 생성

    Returns:
        str: 새 사번 (예: EMP-2025-0001)
    """
    year = datetime.now().year

    # 해당 연도의 마지막 사번 조회
    last_employee = (
        Employee.query
        .filter(Employee.employee_number.like(f'EMP-{year}-%'))
        .order_by(Employee.employee_number.desc())
        .first()
    )

    if last_employee and last_employee.employee_number:
        # 마지막 순번 추출 후 +1
        try:
            last_seq = int(last_employee.employee_number.split('-')[2])
            new_seq = last_seq + 1
        except (IndexError, ValueError):
            new_seq = 1
    else:
        new_seq = 1

    return f'EMP-{year}-{new_seq:04d}'


def is_valid_employee_number(employee_number):
    """
    사번 형식 검증

    Args:
        employee_number: 검증할 사번

    Returns:
        bool: 유효 여부
    """
    if not employee_number:
        return False

    parts = employee_number.split('-')
    if len(parts) != 3:
        return False

    prefix, year, seq = parts

    if prefix != 'EMP':
        return False

    try:
        year_int = int(year)
        if year_int < 2000 or year_int > 2100:
            return False
    except ValueError:
        return False

    try:
        seq_int = int(seq)
        if seq_int < 1 or seq_int > 9999:
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
    query = Employee.query.filter(Employee.employee_number == employee_number)

    if exclude_id:
        query = query.filter(Employee.id != exclude_id)

    return query.first() is not None
