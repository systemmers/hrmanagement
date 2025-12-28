"""
관계형 데이터 업데이트 함수

직원의 가족, 학력, 경력, 자격증 등 관계형 데이터 업데이트를 처리합니다.

Phase 27.1: 개발 원칙 준수 리팩토링
- DRY: atomic_transaction() 사용으로 트랜잭션 패턴 중복 제거
- SSOT: transaction.py의 atomic_transaction() 단일 진실 공급원
- 레이어 분리: Service 경유 (profile_relation_service)
- SRP: 폼 추출(form_extractors) / 데이터 저장(relation_updaters) 분리
"""
from ...utils.transaction import atomic_transaction
from ...services.profile_relation_service import profile_relation_service
from .form_extractors import (
    extract_family_list,
    extract_education_list,
    extract_career_list,
    extract_certificate_list,
    extract_language_list,
    extract_military_data,
    extract_hr_project_list,
    extract_project_participation_list,
    extract_award_list,
)


class EmployeeRelationUpdater:
    """직원 관계형 데이터 업데이트 클래스

    Phase 27.1: Service 패턴 + atomic_transaction 적용
    - 기존 RelatedDataUpdater 대체
    - 트랜잭션 안전성 보장
    - 레이어 분리 원칙 준수
    """

    def __init__(self):
        self.service = profile_relation_service
        self.owner_type = 'employee'

    def update_family(self, employee_id: int, form_data) -> bool:
        """가족정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_family_list(form_data)
            self.service.delete_all_families(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('name'):
                    self.service.add_family(employee_id, item, self.owner_type, commit=False)
        return True

    def update_education(self, employee_id: int, form_data) -> bool:
        """학력정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_education_list(form_data)
            self.service.delete_all_educations(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(employee_id, item, self.owner_type, commit=False)
        return True

    def update_career(self, employee_id: int, form_data) -> bool:
        """경력정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_career_list(form_data)
            self.service.delete_all_careers(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(employee_id, item, self.owner_type, commit=False)
        return True

    def update_certificate(self, employee_id: int, form_data) -> bool:
        """자격증정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('certificate_name'):
                    self.service.add_certificate(employee_id, item, self.owner_type, commit=False)
        return True

    def update_language(self, employee_id: int, form_data) -> bool:
        """언어능력정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_language_list(form_data)
            self.service.delete_all_languages(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language_name'):
                    self.service.add_language(employee_id, item, self.owner_type, commit=False)
        return True

    def update_military(self, employee_id: int, form_data) -> bool:
        """병역정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            data = extract_military_data(form_data)
            self.service.delete_all_military(employee_id, self.owner_type, commit=False)
            if data and data.get('military_status'):
                self.service.add_military(employee_id, data, self.owner_type, commit=False)
        return True

    def update_hr_project(self, employee_id: int, form_data) -> bool:
        """인사이력 프로젝트 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_hr_project_list(form_data)
            self.service.delete_all_hr_projects(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('project_name'):
                    self.service.add_hr_project(employee_id, item, self.owner_type, commit=False)
        return True

    def update_project_participation(self, employee_id: int, form_data) -> bool:
        """프로젝트 참여이력 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_project_participation_list(form_data)
            self.service.delete_all_project_participations(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('project_name'):
                    self.service.add_project_participation(employee_id, item, self.owner_type, commit=False)
        return True

    def update_award(self, employee_id: int, form_data) -> bool:
        """수상정보 업데이트 (트랜잭션 안전)"""
        with atomic_transaction():
            items = extract_award_list(form_data)
            self.service.delete_all_awards(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('award_name'):
                    self.service.add_award(employee_id, item, self.owner_type, commit=False)
        return True

    def update_all_relations(self, employee_id: int, form_data) -> bool:
        """모든 관계형 데이터 단일 트랜잭션 업데이트

        트랜잭션 안전성: 하나라도 실패하면 전체 롤백
        """
        with atomic_transaction():
            # 가족
            items = extract_family_list(form_data)
            self.service.delete_all_families(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('name'):
                    self.service.add_family(employee_id, item, self.owner_type, commit=False)

            # 학력
            items = extract_education_list(form_data)
            self.service.delete_all_educations(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('school_name'):
                    self.service.add_education(employee_id, item, self.owner_type, commit=False)

            # 경력
            items = extract_career_list(form_data)
            self.service.delete_all_careers(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('company_name'):
                    self.service.add_career(employee_id, item, self.owner_type, commit=False)

            # 자격증
            items = extract_certificate_list(form_data)
            self.service.delete_all_certificates(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('certificate_name'):
                    self.service.add_certificate(employee_id, item, self.owner_type, commit=False)

            # 언어능력
            items = extract_language_list(form_data)
            self.service.delete_all_languages(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('language_name'):
                    self.service.add_language(employee_id, item, self.owner_type, commit=False)

            # 병역
            data = extract_military_data(form_data)
            self.service.delete_all_military(employee_id, self.owner_type, commit=False)
            if data and data.get('military_status'):
                self.service.add_military(employee_id, data, self.owner_type, commit=False)

            # 인사이력 프로젝트
            items = extract_hr_project_list(form_data)
            self.service.delete_all_hr_projects(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('project_name'):
                    self.service.add_hr_project(employee_id, item, self.owner_type, commit=False)

            # 프로젝트 참여이력
            items = extract_project_participation_list(form_data)
            self.service.delete_all_project_participations(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('project_name'):
                    self.service.add_project_participation(employee_id, item, self.owner_type, commit=False)

            # 수상
            items = extract_award_list(form_data)
            self.service.delete_all_awards(employee_id, self.owner_type, commit=False)
            for item in items:
                if item.get('award_name'):
                    self.service.add_award(employee_id, item, self.owner_type, commit=False)

        return True


# 싱글톤 인스턴스
employee_relation_updater = EmployeeRelationUpdater()


# ========================================
# 래퍼 함수 (기존 API 호환)
# ========================================

def update_family_data(employee_id, form_data):
    """가족정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_family(employee_id, form_data)


def update_education_data(employee_id, form_data):
    """학력정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_education(employee_id, form_data)


def update_career_data(employee_id, form_data):
    """경력정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_career(employee_id, form_data)


def update_certificate_data(employee_id, form_data):
    """자격증정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_certificate(employee_id, form_data)


def update_language_data(employee_id, form_data):
    """언어능력정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_language(employee_id, form_data)


def update_military_data(employee_id, form_data, commit: bool = True):
    """병역정보 업데이트 (기존 API 호환)

    Note: commit 파라미터는 하위 호환을 위해 유지하지만,
    내부적으로는 atomic_transaction()에서 트랜잭션 관리
    """
    return employee_relation_updater.update_military(employee_id, form_data)


def update_hr_project_data(employee_id, form_data):
    """인사이력 프로젝트 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_hr_project(employee_id, form_data)


def update_project_participation_data(employee_id, form_data):
    """프로젝트 참여이력 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_project_participation(employee_id, form_data)


def update_award_data(employee_id, form_data):
    """수상정보 업데이트 (기존 API 호환)"""
    return employee_relation_updater.update_award(employee_id, form_data)
