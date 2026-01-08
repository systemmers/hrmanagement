"""
Account Management Helper Functions

DRY principle: Centralized account-related validation logic

Usage:
    from .helpers import validate_password_change

    is_valid, error = validate_password_change(current, new, confirm)
    if not is_valid:
        flash(error, 'error')
        return render_template('domains/user/account/password.html')
"""
from typing import Tuple, Optional


def validate_password_change(
    current_password: str,
    new_password: str,
    confirm_password: str
) -> Tuple[bool, Optional[str]]:
    """Password change validation

    Args:
        current_password: Current password
        new_password: New password
        confirm_password: New password confirmation

    Returns:
        (is_valid, error_message): (True, None) on success,
                                   (False, error message) on failure

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
    # Required field validation
    if not all([current_password, new_password, confirm_password]):
        return False, '모든 필드를 입력해주세요.'

    # New password match validation
    if new_password != confirm_password:
        return False, '새 비밀번호가 일치하지 않습니다.'

    # Password length validation
    if len(new_password) < 8:
        return False, '비밀번호는 최소 8자 이상이어야 합니다.'

    return True, None
