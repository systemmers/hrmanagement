"""
Field Registry Base Classes

필드 정의 및 섹션 정의를 위한 기본 데이터 구조.
SSOT(Single Source of Truth) 원칙에 따라 필드 메타데이터를 중앙 관리.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Any, Optional, Callable
from collections import OrderedDict


class FieldType(Enum):
    """필드 입력 타입"""
    TEXT = 'text'
    TEXTAREA = 'textarea'
    EMAIL = 'email'
    TEL = 'tel'
    NUMBER = 'number'
    DATE = 'date'
    SELECT = 'select'
    CHECKBOX = 'checkbox'
    RADIO = 'radio'
    HIDDEN = 'hidden'
    FILE = 'file'
    PASSWORD = 'password'


class Visibility(Enum):
    """계정 타입별 필드 가시성"""
    ALL = 'all'                      # 모든 계정에서 표시
    PERSONAL = 'personal'            # 개인 계정만
    CORPORATE = 'corporate'          # 법인 계정만
    EMPLOYEE_SUB = 'employee_sub'    # 법인 직원 계정만
    PERSONAL_AND_EMPLOYEE = 'personal_and_employee'  # 개인 + 직원
    CORPORATE_ONLY = 'corporate_only'  # 법인 관리자만 (직원 제외)


@dataclass
class Option:
    """Select/Radio 옵션"""
    value: str
    label: str
    disabled: bool = False


@dataclass
class FieldDefinition:
    """
    필드 메타데이터 정의

    Attributes:
        name: 정규 필드명 (snake_case, 모델 속성명과 일치)
        label: 한글 라벨
        field_type: 입력 타입 (FieldType)
        order: 정렬 순서 (낮을수록 먼저 표시)
        required: 필수 입력 여부
        aliases: 호환 별칭 목록 (예: ['name_en'] -> english_name)
        options: 직접 지정된 옵션 목록 (select/radio용)
        options_category: ClassificationOption 참조 카테고리명
        visibility: 계정 타입별 가시성 규칙
        placeholder: 입력 힌트
        max_length: 최대 글자 수
        min_length: 최소 글자 수
        pattern: 정규식 패턴 (validation용)
        readonly: 읽기 전용 여부
        help_text: 도움말 텍스트
        css_class: 추가 CSS 클래스
        attributes: 추가 HTML 속성
    """
    name: str
    label: str
    field_type: FieldType = FieldType.TEXT
    order: int = 0
    required: bool = False
    aliases: List[str] = field(default_factory=list)
    options: List[Option] = field(default_factory=list)
    options_category: str = ''
    visibility: Visibility = Visibility.ALL
    placeholder: str = ''
    max_length: Optional[int] = None
    min_length: Optional[int] = None
    pattern: str = ''
    readonly: bool = False
    help_text: str = ''
    css_class: str = ''
    attributes: Dict[str, Any] = field(default_factory=dict)

    def is_visible_for(self, account_type: str) -> bool:
        """특정 계정 타입에서 필드가 표시되는지 확인"""
        if self.visibility == Visibility.ALL:
            return True
        if self.visibility == Visibility.PERSONAL:
            return account_type == 'personal'
        if self.visibility == Visibility.CORPORATE:
            return account_type in ('corporate', 'employee_sub')
        if self.visibility == Visibility.EMPLOYEE_SUB:
            return account_type == 'employee_sub'
        if self.visibility == Visibility.PERSONAL_AND_EMPLOYEE:
            return account_type in ('personal', 'employee_sub')
        if self.visibility == Visibility.CORPORATE_ONLY:
            return account_type == 'corporate'
        return True

    def get_options_list(self) -> List[Dict[str, Any]]:
        """옵션 목록을 딕셔너리 리스트로 반환 (JS/템플릿용)"""
        return [
            {'value': opt.value, 'label': opt.label, 'disabled': opt.disabled}
            for opt in self.options
        ]

    def to_dict(self) -> Dict[str, Any]:
        """필드 정의를 딕셔너리로 변환 (API/JS용)"""
        return {
            'name': self.name,
            'label': self.label,
            'type': self.field_type.value,
            'order': self.order,
            'required': self.required,
            'aliases': self.aliases,
            'options': self.get_options_list(),
            'optionsCategory': self.options_category,
            'visibility': self.visibility.value,
            'placeholder': self.placeholder,
            'maxLength': self.max_length,
            'minLength': self.min_length,
            'pattern': self.pattern,
            'readonly': self.readonly,
            'helpText': self.help_text,
            'cssClass': self.css_class,
            'attributes': self.attributes,
        }


@dataclass
class SectionDefinition:
    """
    섹션 메타데이터 정의

    Attributes:
        id: 섹션 ID (고유 식별자)
        title: 한글 제목
        icon: 아이콘 클래스 (예: 'bi bi-person')
        fields: 섹션 내 필드 목록 (순서 포함)
        is_dynamic: 동적 추가/삭제 가능 여부 (예: 학력, 경력)
        visibility: 계정 타입별 가시성
        order: 섹션 정렬 순서
        description: 섹션 설명
        collapsed: 기본 접힌 상태 여부
        max_items: 동적 섹션일 경우 최대 항목 수
        min_items: 동적 섹션일 경우 최소 항목 수
    """
    id: str
    title: str
    icon: str = ''
    fields: List[FieldDefinition] = field(default_factory=list)
    is_dynamic: bool = False
    visibility: Visibility = Visibility.ALL
    order: int = 0
    description: str = ''
    collapsed: bool = False
    max_items: Optional[int] = None
    min_items: int = 0

    def __post_init__(self):
        """필드 목록을 order 기준으로 정렬"""
        self.fields = sorted(self.fields, key=lambda f: f.order)

    def get_field(self, name: str) -> Optional[FieldDefinition]:
        """필드명 또는 별칭으로 필드 정의 조회"""
        for f in self.fields:
            if f.name == name or name in f.aliases:
                return f
        return None

    def get_visible_fields(self, account_type: str) -> List[FieldDefinition]:
        """특정 계정 타입에서 표시되는 필드 목록"""
        return [f for f in self.fields if f.is_visible_for(account_type)]

    def get_ordered_names(self, account_type: Optional[str] = None) -> List[str]:
        """정렬된 필드명 목록 반환"""
        if account_type:
            return [f.name for f in self.get_visible_fields(account_type)]
        return [f.name for f in self.fields]

    def get_field_mapping(self) -> Dict[str, str]:
        """별칭 -> 정규 필드명 매핑 딕셔너리"""
        mapping = {}
        for f in self.fields:
            mapping[f.name] = f.name  # 정규 필드명도 포함
            for alias in f.aliases:
                mapping[alias] = f.name
        return mapping

    def normalize_field_name(self, name: str) -> str:
        """별칭을 정규 필드명으로 변환"""
        mapping = self.get_field_mapping()
        return mapping.get(name, name)

    def is_visible_for(self, account_type: str) -> bool:
        """특정 계정 타입에서 섹션이 표시되는지 확인"""
        if self.visibility == Visibility.ALL:
            return True
        if self.visibility == Visibility.PERSONAL:
            return account_type == 'personal'
        if self.visibility == Visibility.CORPORATE:
            return account_type in ('corporate', 'employee_sub')
        if self.visibility == Visibility.EMPLOYEE_SUB:
            return account_type == 'employee_sub'
        if self.visibility == Visibility.PERSONAL_AND_EMPLOYEE:
            return account_type in ('personal', 'employee_sub')
        if self.visibility == Visibility.CORPORATE_ONLY:
            return account_type == 'corporate'
        return True

    def to_dict(self) -> Dict[str, Any]:
        """섹션 정의를 딕셔너리로 변환 (API/JS용)"""
        return {
            'id': self.id,
            'title': self.title,
            'icon': self.icon,
            'fields': [f.to_dict() for f in self.fields],
            'isDynamic': self.is_dynamic,
            'visibility': self.visibility.value,
            'order': self.order,
            'description': self.description,
            'collapsed': self.collapsed,
            'maxItems': self.max_items,
            'minItems': self.min_items,
        }


def create_field(
    name: str,
    label: str,
    order: int,
    field_type: FieldType = FieldType.TEXT,
    **kwargs
) -> FieldDefinition:
    """필드 정의 생성 헬퍼 함수"""
    return FieldDefinition(
        name=name,
        label=label,
        order=order,
        field_type=field_type,
        **kwargs
    )


def create_section(
    id: str,
    title: str,
    fields: List[FieldDefinition],
    order: int = 0,
    **kwargs
) -> SectionDefinition:
    """섹션 정의 생성 헬퍼 함수"""
    return SectionDefinition(
        id=id,
        title=title,
        fields=fields,
        order=order,
        **kwargs
    )
