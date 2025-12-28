"""
폼 데이터 처리 공통 헬퍼

employees/form_extractors.py와 personal/form_extractors.py에서
공통으로 사용되는 헬퍼 함수를 정의합니다. (DRY 원칙)

Phase 25: 공통 모듈 추출 (2025-12-29)
"""
from typing import Any, Optional

from app.constants.field_registry import FieldRegistry


def parse_boolean(value) -> bool:
    """폼 데이터 boolean 변환 헬퍼

    Args:
        value: 폼에서 전달된 값

    Returns:
        bool: 변환된 boolean 값

    Examples:
        >>> parse_boolean('true')
        True
        >>> parse_boolean('1')
        True
        >>> parse_boolean(True)
        True
        >>> parse_boolean('false')
        False
    """
    return value in ('true', 'True', '1', True)


def normalize_form_field(
    form_data: dict,
    section_id: str,
    field_name: str,
    default: Any = None
) -> Optional[Any]:
    """FieldRegistry 기반 폼 필드값 추출 (SSOT 원칙)

    정규 필드명과 별칭을 모두 검색하여 값을 반환합니다.

    Args:
        form_data: request.form 데이터
        section_id: FieldRegistry 섹션 ID (예: 'personal_basic', 'contact')
        field_name: 정규 필드명 (예: 'english_name', 'resident_number')
        default: 기본값 (기본: None)

    Returns:
        필드값 또는 default

    Examples:
        >>> normalize_form_field(form_data, 'personal_basic', 'english_name')
        # 'english_name' 또는 'name_en' 별칭으로 값 검색
    """
    # 정규 필드명으로 먼저 시도
    value = form_data.get(field_name)
    if value:
        return value

    # FieldRegistry에서 별칭 조회
    section = FieldRegistry.get_section(section_id)
    if section:
        field = section.get_field(field_name)
        if field and field.aliases:
            for alias in field.aliases:
                value = form_data.get(alias)
                if value:
                    return value

    return default


def get_form_value(form_data: dict, key: str, default: Any = '') -> Any:
    """폼 데이터에서 값 추출 (strip 적용)

    Args:
        form_data: request.form 데이터
        key: 필드명
        default: 기본값

    Returns:
        strip된 값 또는 default
    """
    value = form_data.get(key, default)
    if isinstance(value, str):
        value = value.strip()
        return value if value else default
    return value


def parse_int(value, default: int = None) -> Optional[int]:
    """문자열을 정수로 변환

    Args:
        value: 변환할 값
        default: 변환 실패 시 기본값

    Returns:
        정수 또는 default
    """
    if value is None:
        return default
    if isinstance(value, int):
        return value
    if isinstance(value, str):
        value = value.strip()
        if not value:
            return default
        try:
            return int(value)
        except ValueError:
            return default
    return default
