"""
파일 처리 헬퍼 함수

DRY 원칙 적용: 파일 확장자 추출 등 공통 파일 처리 로직 중앙화

Usage:
    from app.shared.utils.file_helpers import get_file_extension, is_allowed_extension

    ext = get_file_extension('photo.jpg')  # 'jpg'
    if is_allowed_extension(filename, {'jpg', 'png', 'gif'}):
        ...
"""
from typing import Set


def get_file_extension(filename: str) -> str:
    """파일명에서 확장자 추출

    Args:
        filename: 파일명 (예: 'photo.jpg', 'document.pdf')

    Returns:
        소문자 확장자 문자열 (확장자 없으면 빈 문자열)

    Example:
        >>> get_file_extension('photo.jpg')
        'jpg'
        >>> get_file_extension('DOCUMENT.PDF')
        'pdf'
        >>> get_file_extension('noextension')
        ''
        >>> get_file_extension('')
        ''
    """
    if not filename or '.' not in filename:
        return ''
    return filename.rsplit('.', 1)[1].lower()


def is_allowed_extension(filename: str, allowed_extensions: Set[str]) -> bool:
    """파일 확장자가 허용 목록에 있는지 검사

    Args:
        filename: 파일명
        allowed_extensions: 허용 확장자 집합 (소문자)

    Returns:
        허용된 확장자인 경우 True

    Example:
        >>> is_allowed_extension('photo.jpg', {'jpg', 'png', 'gif'})
        True
        >>> is_allowed_extension('script.exe', {'jpg', 'png', 'gif'})
        False
    """
    ext = get_file_extension(filename)
    return ext in allowed_extensions if ext else False
