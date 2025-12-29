"""
동기화 필드 매핑 SSOT (Single Source of Truth)

개인(PersonalProfile) <-> 법인(Employee) 간 필드 매핑을 중앙 관리합니다.
새 필드 추가 시 이 파일만 수정하면 됩니다.

Phase 4: sync_service 필드 매핑 중앙화
"""
from dataclasses import dataclass, field
from typing import Dict, List, Tuple, Set


# =====================================================
# 기본 필드 매핑 (PersonalProfile -> Employee)
# =====================================================

BASIC_FIELD_MAPPING: Dict[str, str] = {
    'name': 'name',
    'english_name': 'english_name',
    'chinese_name': 'chinese_name',
    'photo': 'photo',
    'birth_date': 'birth_date',
    'lunar_birth': 'lunar_birth',
    'gender': 'gender',
}

# =====================================================
# 연락처 필드 매핑
# =====================================================

CONTACT_FIELD_MAPPING: Dict[str, str] = {
    'mobile_phone': 'mobile_phone',
    'home_phone': 'home_phone',
    'email': 'email',
    'postal_code': 'postal_code',
    'address': 'address',
    'detailed_address': 'detailed_address',
}

# =====================================================
# 추가 개인정보 필드 매핑
# =====================================================

EXTRA_FIELD_MAPPING: Dict[str, str] = {
    'nationality': 'nationality',
    'blood_type': 'blood_type',
    'religion': 'religion',
    'hobby': 'hobby',
    'specialty': 'specialty',
    'disability_info': 'disability_info',
    'resident_number': 'resident_number',
    'marital_status': 'marital_status',
    # 실제 거주 주소
    'actual_postal_code': 'actual_postal_code',
    'actual_address': 'actual_address',
    'actual_detailed_address': 'actual_detailed_address',
    # 비상연락처
    'emergency_contact': 'emergency_contact',
    'emergency_relation': 'emergency_relation',
}

# =====================================================
# 관계형 데이터 매핑 (source_fk, target_fk)
# =====================================================

RELATION_FIELD_MAPPING: Dict[str, Tuple[str, str]] = {
    'educations': ('profile_id', 'employee_id'),
    'careers': ('profile_id', 'employee_id'),
    'certificates': ('profile_id', 'employee_id'),
    'languages': ('profile_id', 'employee_id'),
    'military': ('profile_id', 'employee_id'),
    'family': ('profile_id', 'employee_id'),
}

# =====================================================
# 공유 설정과 필드 그룹 매핑
# =====================================================

SHARING_FIELD_GROUPS: Dict[str, Dict[str, str]] = {
    'share_basic_info': BASIC_FIELD_MAPPING,
    'share_contact': CONTACT_FIELD_MAPPING,
}


@dataclass
class SyncFieldMapping:
    """
    동기화 필드 매핑 설정 (타입 안전)

    Usage:
        from app.constants.sync_fields import SYNC_MAPPINGS

        # 기본 + 연락처 필드 통합 조회
        all_basic = SYNC_MAPPINGS.get_all_basic_fields()

        # 관계형 매핑 조회
        edu_mapping = SYNC_MAPPINGS.get_relation_mapping('educations')

        # 필드 목록 조회
        basic_fields = SYNC_MAPPINGS.get_basic_field_names()
    """

    basic: Dict[str, str] = field(default_factory=lambda: BASIC_FIELD_MAPPING.copy())
    contact: Dict[str, str] = field(default_factory=lambda: CONTACT_FIELD_MAPPING.copy())
    extra: Dict[str, str] = field(default_factory=lambda: EXTRA_FIELD_MAPPING.copy())
    relation: Dict[str, Tuple[str, str]] = field(default_factory=lambda: RELATION_FIELD_MAPPING.copy())

    def get_all_basic_fields(self) -> Dict[str, str]:
        """기본 + 연락처 + 추가 필드 통합 반환"""
        return {**self.basic, **self.contact, **self.extra}

    def get_basic_and_contact_fields(self) -> Dict[str, str]:
        """기본 + 연락처 필드만 반환"""
        return {**self.basic, **self.contact}

    def get_basic_field_names(self) -> List[str]:
        """기본 필드명 목록"""
        return list(self.basic.keys())

    def get_contact_field_names(self) -> List[str]:
        """연락처 필드명 목록"""
        return list(self.contact.keys())

    def get_extra_field_names(self) -> List[str]:
        """추가 필드명 목록"""
        return list(self.extra.keys())

    def get_all_field_names(self) -> Set[str]:
        """전체 필드명 집합"""
        return set(self.basic.keys()) | set(self.contact.keys()) | set(self.extra.keys())

    def get_relation_mapping(self, relation_name: str) -> Tuple[str, str]:
        """관계 필드 매핑 조회 (source_fk, target_fk)"""
        return self.relation.get(relation_name, (None, None))

    def get_relation_names(self) -> List[str]:
        """관계형 데이터 타입 목록"""
        return list(self.relation.keys())

    def map_field(self, source_field: str) -> str:
        """소스 필드명 -> 타겟 필드명 변환"""
        all_fields = self.get_all_basic_fields()
        return all_fields.get(source_field, source_field)

    def is_syncable_field(self, field_name: str) -> bool:
        """동기화 가능한 필드인지 확인"""
        return field_name in self.get_all_field_names()

    def get_sharing_group_fields(self, sharing_key: str) -> Dict[str, str]:
        """공유 설정 키에 해당하는 필드 그룹 반환"""
        if sharing_key == 'share_basic_info':
            return self.basic.copy()
        elif sharing_key == 'share_contact':
            return self.contact.copy()
        return {}


# =====================================================
# 싱글톤 인스턴스 (SSOT)
# =====================================================

SYNC_MAPPINGS = SyncFieldMapping()

# =====================================================
# 편의 상수 (하위 호환성)
# =====================================================

# 관계형 데이터 타입 목록
SYNCABLE_RELATION_TYPES = [
    'education',
    'career',
    'certificates',
    'languages',
    'military',
    'family',
]


__all__ = [
    # 클래스
    'SyncFieldMapping',
    # 싱글톤 인스턴스
    'SYNC_MAPPINGS',
    # 필드 매핑 딕셔너리
    'BASIC_FIELD_MAPPING',
    'CONTACT_FIELD_MAPPING',
    'EXTRA_FIELD_MAPPING',
    'RELATION_FIELD_MAPPING',
    'SHARING_FIELD_GROUPS',
    # 상수
    'SYNCABLE_RELATION_TYPES',
]
