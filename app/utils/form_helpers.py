"""
폼 데이터 처리 공통 헬퍼

employees/form_extractors.py와 personal/form_extractors.py에서
공통으로 사용되는 헬퍼 함수를 정의합니다. (DRY 원칙)

Phase 25: 공통 모듈 추출 (2025-12-29)
Phase 29: normalize_form_field 제거 (2026-01-05) - 별칭 시스템 제거
Phase 31: extract_relation_list 통합 (2026-01-06) - DRY 위반 수정
"""
from typing import Any, Dict, List, Optional

# 타입 별칭 정의
FormData = Any  # werkzeug.datastructures.ImmutableMultiDict
FieldMapping = Dict[str, str]  # {form_suffix: model_field}


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


# Phase 29: normalize_form_field() 함수 제거됨 (2026-01-05)
# 모든 폼 필드는 snake_case로 직접 접근합니다.
# 별칭 시스템이 제거되어 form_data.get('field_name')으로 직접 사용합니다.


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


def extract_relation_list(
    form_data: FormData,
    prefix: str,
    field_mapping: FieldMapping
) -> List[Dict[str, Any]]:
    """동적 관계형 데이터 리스트 추출 (범용, DRY 원칙)

    employees/form_extractors.py와 personal/form_extractors.py에서
    공통으로 사용되는 관계형 데이터 추출 함수입니다.

    Args:
        form_data: request.form 데이터
        prefix: 폼 필드 접두사 (예: 'family_', 'education_')
        field_mapping: {form_suffix: model_field} 매핑

    Returns:
        list[dict]: 관계형 데이터 리스트

    Example:
        >>> extract_relation_list(form_data, 'family_', {
        ...     'relation': 'relation',
        ...     'name': 'name',
        ...     'birth_date': 'birth_date',
        ... })
        [{'relation': '부', 'name': '홍길동', 'birth_date': '1960-01-01'}, ...]
    """
    # 폼 리스트 데이터 수집
    form_lists = {}
    for form_suffix in field_mapping.keys():
        form_key = f"{prefix}{form_suffix}[]"
        form_lists[form_suffix] = form_data.getlist(form_key)

    # 첫 번째 필드를 기준으로 레코드 수 결정
    first_field = list(field_mapping.keys())[0]
    count = len(form_lists.get(first_field, []))

    result = []
    for i in range(count):
        record = {}
        for form_suffix, model_field in field_mapping.items():
            values = form_lists.get(form_suffix, [])
            value = values[i] if i < len(values) else None
            if value:
                value = value.strip() if isinstance(value, str) else value
            record[model_field] = value or None
        result.append(record)

    return result
