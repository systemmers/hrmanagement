"""
Field Registry Module

필드 순서 및 메타데이터 중앙 관리 시스템.
SSOT(Single Source of Truth) 원칙에 따라 모든 필드 정의를 한 곳에서 관리.

Phase 29 (2026-01-05): aliases 시스템 제거 - snake_case 직접 사용

Usage:
    from app.constants.field_registry import FieldRegistry

    # 섹션 조회
    section = FieldRegistry.get_section('personal_basic')

    # 정렬된 필드명 목록
    field_names = FieldRegistry.get_ordered_names('personal_basic', account_type='personal')

    # 데이터를 정렬된 순서로 변환
    ordered_data = FieldRegistry.to_ordered_dict('personal_basic', raw_data, account_type)
"""
from collections import OrderedDict
from typing import Dict, List, Optional, Any

from .base import (
    FieldDefinition,
    SectionDefinition,
    FieldType,
    Visibility,
    Option,
    create_field,
    create_section,
)


class FieldRegistry:
    """
    필드 레지스트리 중앙 관리 클래스

    모든 필드 정의를 중앙에서 관리하며, 섹션별/계정타입별 필드 조회 및
    데이터 정렬 기능을 제공.

    Phase 29: aliases 시스템 제거 - snake_case 직접 사용
    """

    # 섹션 저장소 (섹션 ID -> SectionDefinition)
    _sections: Dict[str, SectionDefinition] = {}

    # 도메인 -> 섹션 ID 매핑 (하나의 도메인이 여러 섹션을 포함할 수 있음)
    _domains: Dict[str, List[str]] = {}

    @classmethod
    def register_section(cls, section: SectionDefinition, domain: str = '') -> None:
        """
        섹션 등록

        Args:
            section: 등록할 섹션 정의
            domain: 도메인명 (예: 'profile', 'employee')
        """
        cls._sections[section.id] = section

        # 도메인에 섹션 추가
        if domain:
            if domain not in cls._domains:
                cls._domains[domain] = []
            if section.id not in cls._domains[domain]:
                cls._domains[domain].append(section.id)

    @classmethod
    def get_section(cls, section_id: str) -> Optional[SectionDefinition]:
        """
        섹션 ID로 섹션 정의 조회

        Args:
            section_id: 섹션 ID

        Returns:
            SectionDefinition or None
        """
        return cls._sections.get(section_id)

    @classmethod
    def get_sections_by_domain(cls, domain: str) -> List[SectionDefinition]:
        """
        도메인에 속한 모든 섹션 조회

        Args:
            domain: 도메인명

        Returns:
            섹션 정의 목록 (order 기준 정렬)
        """
        section_ids = cls._domains.get(domain, [])
        sections = [cls._sections[sid] for sid in section_ids if sid in cls._sections]
        return sorted(sections, key=lambda s: s.order)

    @classmethod
    def get_ordered_names(
        cls,
        section_id: str,
        account_type: Optional[str] = None
    ) -> List[str]:
        """
        섹션의 정렬된 필드명 목록 반환

        Args:
            section_id: 섹션 ID
            account_type: 계정 타입 (필터링용)

        Returns:
            정렬된 필드명 리스트
        """
        section = cls.get_section(section_id)
        if not section:
            return []
        return section.get_ordered_names(account_type)

    @classmethod
    def get_visible_fields(
        cls,
        section_id: str,
        account_type: str
    ) -> List[FieldDefinition]:
        """
        특정 계정 타입에서 표시되는 필드 목록

        Args:
            section_id: 섹션 ID
            account_type: 계정 타입

        Returns:
            가시성 필터링된 필드 정의 목록
        """
        section = cls.get_section(section_id)
        if not section:
            return []
        return section.get_visible_fields(account_type)

    @classmethod
    def normalize_field_name(cls, section_id: str, name: str) -> str:
        """
        필드명 정규화 (Phase 29: 별칭 변환 제거)

        Args:
            section_id: 섹션 ID (미사용, 하위 호환성 유지)
            name: 필드명

        Returns:
            입력된 필드명 그대로 반환
        """
        return name

    @classmethod
    def normalize_data(
        cls,
        section_id: str,
        data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        데이터의 필드명을 모두 정규화

        Args:
            section_id: 섹션 ID
            data: 원본 데이터

        Returns:
            정규화된 필드명을 가진 데이터
        """
        section = cls.get_section(section_id)
        if not section:
            return data

        normalized = {}
        field_mapping = section.get_field_mapping()

        for key, value in data.items():
            canonical_key = field_mapping.get(key, key)
            normalized[canonical_key] = value

        return normalized

    @classmethod
    def to_ordered_dict(
        cls,
        section_id: str,
        data: Dict[str, Any],
        account_type: Optional[str] = None
    ) -> OrderedDict:
        """
        데이터를 필드 순서에 맞게 정렬된 OrderedDict로 변환

        Args:
            section_id: 섹션 ID
            data: 원본 데이터 (dict)
            account_type: 계정 타입 (가시성 필터링용)

        Returns:
            정렬된 OrderedDict
        """
        section = cls.get_section(section_id)
        if not section:
            return OrderedDict(data)

        # 필드명 정규화
        normalized_data = cls.normalize_data(section_id, data)

        # 정렬된 필드명 목록
        ordered_names = section.get_ordered_names(account_type)

        # OrderedDict 생성
        result = OrderedDict()
        for name in ordered_names:
            if name in normalized_data:
                result[name] = normalized_data[name]

        # 정의되지 않은 필드는 마지막에 추가 (하위 호환성)
        for key, value in normalized_data.items():
            if key not in result:
                result[key] = value

        return result

    @classmethod
    def get_field(cls, section_id: str, field_name: str) -> Optional[FieldDefinition]:
        """
        특정 필드 정의 조회

        Args:
            section_id: 섹션 ID
            field_name: 필드명 또는 별칭

        Returns:
            FieldDefinition or None
        """
        section = cls.get_section(section_id)
        if section:
            return section.get_field(field_name)
        return None

    @classmethod
    def get_field_mapping(cls, section_id: str) -> Dict[str, str]:
        """
        섹션의 별칭 -> 정규 필드명 매핑

        Args:
            section_id: 섹션 ID

        Returns:
            매핑 딕셔너리
        """
        section = cls.get_section(section_id)
        if section:
            return section.get_field_mapping()
        return {}

    @classmethod
    def get_js_config(cls, section_id: str, account_type: Optional[str] = None) -> Dict[str, Any]:
        """
        JavaScript용 섹션 설정 반환

        Args:
            section_id: 섹션 ID
            account_type: 계정 타입 (필터링용)

        Returns:
            JS용 설정 딕셔너리
        """
        section = cls.get_section(section_id)
        if not section:
            return {}

        if account_type:
            # 가시성 필터링된 필드만 포함
            visible_fields = section.get_visible_fields(account_type)
            return {
                'id': section.id,
                'title': section.title,
                'icon': section.icon,
                'fields': [f.to_dict() for f in visible_fields],
                'isDynamic': section.is_dynamic,
                'order': section.order,
                'description': section.description,
                'collapsed': section.collapsed,
                'maxItems': section.max_items,
                'minItems': section.min_items,
            }

        return section.to_dict()

    @classmethod
    def get_all_sections(cls) -> List[SectionDefinition]:
        """
        등록된 모든 섹션 조회

        Returns:
            모든 섹션 정의 목록 (order 기준 정렬)
        """
        return sorted(cls._sections.values(), key=lambda s: s.order)

    @classmethod
    def get_all_domains(cls) -> List[str]:
        """
        등록된 모든 도메인 목록

        Returns:
            도메인명 리스트
        """
        return list(cls._domains.keys())

    @classmethod
    def clear(cls) -> None:
        """
        모든 등록 정보 초기화 (테스트용)
        """
        cls._sections.clear()
        cls._domains.clear()


# 모듈 레벨에서 섹션 정의를 자동 로드
def _load_sections():
    """섹션 정의 자동 로드"""
    try:
        from .sections import personal, organization, relations
    except ImportError:
        # 섹션 파일이 아직 없으면 무시
        pass


# 모듈 임포트 시 섹션 로드
_load_sections()


__all__ = [
    'FieldRegistry',
    'FieldDefinition',
    'SectionDefinition',
    'FieldType',
    'Visibility',
    'Option',
    'create_field',
    'create_section',
]
