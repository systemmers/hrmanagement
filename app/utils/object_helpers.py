"""
Object Access Helpers

Dict/Model 객체 접근 통합 유틸리티
Phase 23: 클린업 - isinstance(obj, dict) 패턴 통합
"""
from typing import Any, Optional


def safe_get(obj: Any, key: str, default: Any = None) -> Any:
    """
    dict 또는 object에서 안전하게 값 추출

    Args:
        obj: dict 또는 object
        key: 추출할 키/속성명
        default: 기본값

    Returns:
        추출된 값 또는 기본값

    Example:
        # Before
        file_id = data.get('fileId') if isinstance(data, dict) else data.file_id

        # After
        file_id = safe_get(data, 'file_id')
    """
    if obj is None:
        return default
    if isinstance(obj, dict):
        return obj.get(key, default)
    return getattr(obj, key, default)


def safe_get_nested(obj: Any, *keys: str, default: Any = None) -> Any:
    """
    중첩된 dict/object에서 안전하게 값 추출

    Args:
        obj: dict 또는 object
        *keys: 순차적으로 접근할 키들
        default: 기본값

    Returns:
        추출된 값 또는 기본값

    Example:
        safe_get_nested(data, 'user', 'profile', 'name')
    """
    result = obj
    for key in keys:
        if result is None:
            return default
        result = safe_get(result, key, default=None)
    return result if result is not None else default
