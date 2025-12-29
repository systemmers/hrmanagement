"""
관계형 데이터 업데이트 함수 (Personal Blueprint)

ProfileRelationService를 활용하여 트랜잭션 안전성을 보장합니다.

Phase 27.1: 개발 원칙 준수 리팩토링
- DRY: atomic_transaction() 사용으로 트랜잭션 패턴 중복 제거
- SSOT: transaction.py의 atomic_transaction() 단일 진실 공급원
- employees/relation_updaters.py 패턴과 일관성 유지
"""
from app.types import FormData, OwnerType
from ...utils.transaction import atomic_transaction
from ...services.profile_relation_service import profile_relation_service
from .form_extractors import (
    extract_education_list,
    extract_career_list,
    extract_certificate_list,
    extract_language_list,
    extract_military_data,
)


class ProfileRelationUpdater:
    """프로필 관계형 데이터 업데이트 클래스

    Phase 27.1: atomic_transaction() 적용
    - 트랜잭션 안전성 보장
    - DRY 원칙 준수
    """

    def __init__(self, owner_type: OwnerType = 'profile') -> None:
        """
        Args:
            owner_type: 'profile' (개인계정) 또는 'employee' (법인직원)
        """
        self.owner_type: OwnerType = owner_type
        self.service = profile_relation_service

    def update_educations(self, owner_id: int, form_data: FormData) -> bool:
        """학력 정보 일괄 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_education_list(form_data)
            self.service.delete_all_educations(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(owner_id, item, self.owner_type, commit=False)
        return True

    def update_careers(self, owner_id: int, form_data: FormData) -> bool:
        """경력 정보 일괄 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_career_list(form_data)
            self.service.delete_all_careers(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(owner_id, item, self.owner_type, commit=False)
        return True

    def update_certificates(self, owner_id: int, form_data: FormData) -> bool:
        """자격증 정보 일괄 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('name'):
                    self.service.add_certificate(owner_id, item, self.owner_type, commit=False)
        return True

    def update_languages(self, owner_id: int, form_data: FormData) -> bool:
        """언어능력 정보 일괄 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_language_list(form_data)
            self.service.delete_all_languages(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language'):
                    self.service.add_language(owner_id, item, self.owner_type, commit=False)
        return True

    def update_military(self, owner_id: int, form_data: FormData) -> bool:
        """병역 정보 업데이트 (1:1 관계, 트랜잭션 안전)"""
        with atomic_transaction():
            data = extract_military_data(form_data)
            if data:
                self.service.update_or_create_military(owner_id, data, self.owner_type, commit=False)
        return True

    def update_all_relations(self, owner_id: int, form_data) -> bool:
        """모든 관계형 데이터 일괄 업데이트 (단일 트랜잭션)

        트랜잭션 안전성: 하나라도 실패하면 전체 롤백
        """
        with atomic_transaction():
            # 학력
            items = extract_education_list(form_data)
            self.service.delete_all_educations(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(owner_id, item, self.owner_type, commit=False)

            # 경력
            items = extract_career_list(form_data)
            self.service.delete_all_careers(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(owner_id, item, self.owner_type, commit=False)

            # 자격증
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('name'):
                    self.service.add_certificate(owner_id, item, self.owner_type, commit=False)

            # 언어능력
            items = extract_language_list(form_data)
            self.service.delete_all_languages(owner_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language'):
                    self.service.add_language(owner_id, item, self.owner_type, commit=False)

            # 병역
            military_data = extract_military_data(form_data)
            if military_data:
                self.service.update_or_create_military(owner_id, military_data, self.owner_type, commit=False)

        return True


# 싱글톤 인스턴스 (개인계정용)
profile_relation_updater = ProfileRelationUpdater(owner_type='profile')


# ========================================
# 래퍼 함수 (기존 API 호환)
# ========================================

def update_profile_relations(profile_id: int, form_data) -> bool:
    """프로필 관계형 데이터 일괄 업데이트 (트랜잭션 안전)

    Args:
        profile_id: 프로필 ID
        form_data: request.form 데이터

    Returns:
        bool: 성공 여부

    Raises:
        Exception: 업데이트 실패 시
    """
    return profile_relation_updater.update_all_relations(profile_id, form_data)
