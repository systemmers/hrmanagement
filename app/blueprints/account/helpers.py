"""
계정 관리 헬퍼 함수

DRY 원칙 적용: 계정 관련 검증 로직 중앙화

Usage:
    from .helpers import validate_password_change

    is_valid, error = validate_password_change(current, new, confirm)
    if not is_valid:
        flash(error, 'error')
        return render_template('account/password.html')
"""
from typing import Tuple, Optional


def validate_password_change(
    current_password: str,
    new_password: str,
    confirm_password: str
) -> Tuple[bool, Optional[str]]:
    """비밀번호 변경 유효성 검사

    Args:
        current_password: 현재 비밀번호
        new_password: 새 비밀번호
        confirm_password: 새 비밀번호 확인

    Returns:
        (is_valid, error_message): 검증 성공 시 (True, None),
                                   실패 시 (False, 에러 메시지)

    Example:
        >>> validate_password_change('', 'newpass', 'newpass')
        (False, '모든 필드를 입력해주세요.')
        >>> validate_password_change('old', 'new1', 'new2')
        (False, '새 비밀번호가 일치하지 않습니다.')
        >>> validate_password_change('old', 'short', 'short')
        (False, '비밀번호는 최소 8자 이상이어야 합니다.')
        >>> validate_password_change('old', 'validpass', 'validpass')
        (True, None)
    """
    # 필수 입력 검증
    if not all([current_password, new_password, confirm_password]):
        return False, '모든 필드를 입력해주세요.'

    # 새 비밀번호 일치 검증
    if new_password != confirm_password:
        return False, '새 비밀번호가 일치하지 않습니다.'

    # 비밀번호 길이 검증
    if len(new_password) < 8:
        return False, '비밀번호는 최소 8자 이상이어야 합니다.'

    return True, None
