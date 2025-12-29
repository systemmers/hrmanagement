"""
공통 Type Aliases

프로젝트 전반에서 사용되는 타입 정의를 중앙화합니다.
Phase 7: Type Hints 강화

사용 예:
    from app.types import FormData, FieldMapping, ConverterFunc
"""
from typing import Any, Callable, Dict, List, Optional, TypeVar, Union
from werkzeug.datastructures import ImmutableMultiDict


# ========================================
# 기본 타입 Aliases
# ========================================

# 폼 데이터 타입 (Flask request.form)
FormData = Union[Dict[str, Any], ImmutableMultiDict[str, str]]

# JSON 데이터 타입
JsonData = Dict[str, Any]

# 필드 값 타입
FieldValue = Optional[Union[str, int, float, bool, List[Any], Dict[str, Any]]]


# ========================================
# 필드 관련 타입
# ========================================

# 필드 매핑 (필드명 -> 필드명)
FieldMapping = Dict[str, str]

# 필드 옵션 (value -> label)
FieldOptions = Dict[str, str]

# 섹션별 필드 목록
SectionFields = Dict[str, List[str]]


# ========================================
# 함수 타입 (Callable)
# ========================================

# 값 변환 함수 (str -> Any)
ConverterFunc = Callable[[str], Any]

# 검증 함수 (Any -> bool)
ValidatorFunc = Callable[[Any], bool]

# 데이터 추출 함수 (FormData -> Dict)
ExtractorFunc = Callable[[FormData], Dict[str, Any]]

# 데이터 업데이트 함수 (id, FormData -> bool)
UpdaterFunc = Callable[[int, FormData], bool]


# ========================================
# 제네릭 타입
# ========================================

# 모델 타입 변수
T = TypeVar('T')

# Owner ID (employee_id 또는 profile_id)
OwnerId = int

# Owner 타입 리터럴
OwnerType = str  # 'employee' | 'profile'


# ========================================
# 결과 타입
# ========================================

# 단순 결과 (성공 여부, 메시지)
SimpleResult = tuple[bool, Optional[str]]

# 데이터 결과 (성공 여부, 데이터, 메시지)
DataResult = tuple[bool, Optional[Dict[str, Any]], Optional[str]]
