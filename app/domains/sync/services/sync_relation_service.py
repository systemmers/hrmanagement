"""
관계형 데이터 동기화 서비스

학력, 경력, 자격증, 어학, 병역 등 관계형 데이터의 동기화를 담당합니다.

Phase 30: 레이어 분리 - db.session 제거, Repository 패턴 적용
"""
from typing import Dict, Any
import json

from app.domains.employee.models import Employee
from app.domains.employee.models import Profile
from app.models import SyncLog


class SyncRelationService:
    """관계형 데이터 동기화 처리

    Phase 30: Repository DI 패턴 적용
    """

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id
        # Repository 지연 초기화용
        self._sync_log_repo = None
        self._education_repo = None
        self._career_repo = None
        self._certificate_repo = None
        self._language_repo = None
        self._military_repo = None
        self._family_repo = None

    # ========================================
    # Repository Properties (지연 초기화)
    # ========================================

    @property
    def sync_log_repo(self):
        """지연 초기화된 SyncLog Repository"""
        if self._sync_log_repo is None:
            from app.domains.sync.repositories.sync_log_repository import sync_log_repository
            self._sync_log_repo = sync_log_repository
        return self._sync_log_repo

    @property
    def education_repo(self):
        """지연 초기화된 Education Repository"""
        if self._education_repo is None:
            from app.domains.employee.repositories import EducationRepository
            self._education_repo = EducationRepository()
        return self._education_repo

    @property
    def career_repo(self):
        """지연 초기화된 Career Repository"""
        if self._career_repo is None:
            from app.domains.employee.repositories import CareerRepository
            self._career_repo = CareerRepository()
        return self._career_repo

    @property
    def certificate_repo(self):
        """지연 초기화된 Certificate Repository"""
        if self._certificate_repo is None:
            from app.domains.employee.repositories import CertificateRepository
            self._certificate_repo = CertificateRepository()
        return self._certificate_repo

    @property
    def language_repo(self):
        """지연 초기화된 Language Repository"""
        if self._language_repo is None:
            from app.domains.employee.repositories import LanguageRepository
            self._language_repo = LanguageRepository()
        return self._language_repo

    @property
    def military_repo(self):
        """지연 초기화된 MilitaryService Repository"""
        if self._military_repo is None:
            from app.domains.employee.repositories import MilitaryServiceRepository
            self._military_repo = MilitaryServiceRepository()
        return self._military_repo

    @property
    def family_repo(self):
        """지연 초기화된 FamilyMember Repository"""
        if self._family_repo is None:
            from app.domains.employee.repositories import FamilyMemberRepository
            self._family_repo = FamilyMemberRepository()
        return self._family_repo

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정"""
        self._current_user_id = user_id

    def sync_relations(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        syncable: Dict,
        sync_type: str
    ) -> Dict[str, Any]:
        """
        관계 데이터 동기화 (학력, 경력 등)

        Args:
            contract_id: 계약 ID
            profile: 개인 프로필
            employee: 직원 객체
            syncable: 동기화 가능 필드 설정
            sync_type: 동기화 유형

        Returns:
            동기화 결과 {'synced_relations': [], 'changes': [], 'log_ids': []}
        """
        changes = []
        log_ids = []
        synced_relations = []

        # 학력 동기화
        if syncable.get('education'):
            result = self._sync_education(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('education')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 경력 동기화
        if syncable.get('career'):
            result = self._sync_career(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('career')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 자격증 동기화
        if syncable.get('certificates'):
            result = self._sync_certificates(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('certificates')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 어학 동기화
        if syncable.get('languages'):
            result = self._sync_languages(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('languages')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 병역 동기화
        if syncable.get('military'):
            result = self._sync_military(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('military')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 가족 동기화
        if syncable.get('family'):
            result = self._sync_family_members(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('family')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        return {
            'synced_relations': synced_relations,
            'changes': changes,
            'log_ids': log_ids
        }

    def _sync_education(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """학력 정보 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import Education

        personal_edus = list(profile.educations.all())
        if not personal_edus:
            return {'synced': False}

        # Phase 30: Repository 사용 - 기존 직원 학력 삭제
        self.education_repo.delete_by_employee_id(employee.id, commit=False)

        for pe in personal_edus:
            edu = Education(
                employee_id=employee.id,
                school_type=pe.school_type,
                school_name=pe.school_name,
                major=pe.major,
                degree=pe.degree,
                admission_date=pe.admission_date,
                graduation_date=pe.graduation_date,
                graduation_status=pe.graduation_status,
                gpa=getattr(pe, 'gpa', None),
                location=getattr(pe, 'location', None),
                note=getattr(pe, 'note', None),
            )
            # Phase 30: Repository 사용
            self.education_repo.create_model(edu, commit=False)

        # Phase 30: Repository 사용 - 로그 생성
        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='education',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_edus)}),
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'education', 'count': len(personal_edus)}],
            'log_ids': [log.id]
        }

    def _sync_career(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """경력 정보 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import Career

        personal_careers = list(profile.careers.all())
        if not personal_careers:
            return {'synced': False}

        # Phase 30: Repository 사용
        self.career_repo.delete_by_employee_id(employee.id, commit=False)

        for pc in personal_careers:
            career = Career(
                employee_id=employee.id,
                company_name=pc.company_name,
                department=pc.department,
                position=pc.position,
                job_grade=getattr(pc, 'job_grade', None),
                job_title=getattr(pc, 'job_title', None),
                job_role=getattr(pc, 'job_role', None),
                job_description=getattr(pc, 'job_description', None),
                start_date=pc.start_date,
                end_date=pc.end_date,
                is_current=getattr(pc, 'is_current', False),
                resignation_reason=getattr(pc, 'resignation_reason', None),
                note=getattr(pc, 'note', None),
            )
            self.career_repo.create_model(career, commit=False)

        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='career',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_careers)}),
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'career', 'count': len(personal_careers)}],
            'log_ids': [log.id]
        }

    def _sync_certificates(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """자격증 정보 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import Certificate

        personal_certs = list(profile.certificates.all())
        if not personal_certs:
            return {'synced': False}

        # Phase 30: Repository 사용
        self.certificate_repo.delete_by_employee_id(employee.id, commit=False)

        for pc in personal_certs:
            cert = Certificate(
                employee_id=employee.id,
                certificate_name=pc.certificate_name,
                issuing_organization=pc.issuing_organization,
                acquisition_date=getattr(pc, 'acquisition_date', None),
                expiry_date=getattr(pc, 'expiry_date', None),
                certificate_number=getattr(pc, 'certificate_number', None),
                grade=getattr(pc, 'grade', None),
                note=getattr(pc, 'note', None),
            )
            self.certificate_repo.create_model(cert, commit=False)

        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='certificate',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_certs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'certificate', 'count': len(personal_certs)}],
            'log_ids': [log.id]
        }

    def _sync_languages(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """어학 능력 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import Language

        personal_langs = list(profile.languages.all())
        if not personal_langs:
            return {'synced': False}

        # Phase 30: Repository 사용
        self.language_repo.delete_by_employee_id(employee.id, commit=False)

        for pl in personal_langs:
            lang = Language(
                employee_id=employee.id,
                language_name=pl.language_name,
                level=getattr(pl, 'level', None),
                exam_name=getattr(pl, 'exam_name', None),
                score=getattr(pl, 'score', None),
                acquisition_date=getattr(pl, 'acquisition_date', None),
                expiry_date=getattr(pl, 'expiry_date', None),
                note=getattr(pl, 'note', None),
            )
            self.language_repo.create_model(lang, commit=False)

        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='language',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_langs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'language', 'count': len(personal_langs)}],
            'log_ids': [log.id]
        }

    def _sync_military(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """병역 정보 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import MilitaryService

        # Profile.military_services는 dynamic 관계
        personal_military = profile.military_services.first()
        if not personal_military:
            return {'synced': False}

        # Phase 30: Repository 사용 - 기존 병역 정보 삭제
        self.military_repo.delete_by_employee_id(employee.id, commit=False)

        military = MilitaryService(
            employee_id=employee.id,
            military_status=getattr(personal_military, 'military_status', None),
            service_type=getattr(personal_military, 'service_type', None),
            branch=getattr(personal_military, 'branch', None),
            rank=getattr(personal_military, 'rank', None),
            enlistment_date=getattr(personal_military, 'enlistment_date', None),
            discharge_date=getattr(personal_military, 'discharge_date', None),
            discharge_reason=getattr(personal_military, 'discharge_reason', None),
            exemption_reason=getattr(personal_military, 'exemption_reason', None),
            note=getattr(personal_military, 'note', None),
        )
        self.military_repo.create_model(military, commit=False)

        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='military_service',
            field_name=None,
            old_value=None,
            new_value='synced',
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'military_service', 'synced': True}],
            'log_ids': [log.id]
        }

    def _sync_family_members(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """가족 정보 동기화

        Phase 30: Repository 패턴 적용
        """
        from app.domains.employee.models import FamilyMember

        personal_family = list(profile.family_members.all())
        if not personal_family:
            return {'synced': False}

        # Phase 30: Repository 사용 - 기존 가족 정보 삭제
        self.family_repo.delete_by_employee_id(employee.id, commit=False)

        for pf in personal_family:
            family = FamilyMember(
                employee_id=employee.id,
                relation=pf.relation,
                name=pf.name,
                birth_date=pf.birth_date,
                occupation=pf.occupation,
                contact=pf.contact,
                is_cohabitant=pf.is_cohabitant,
                is_dependent=pf.is_dependent,
                note=pf.note,
            )
            self.family_repo.create_model(family, commit=False)

        log = self.sync_log_repo.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='family_member',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_family)}),
            direction='personal_to_employee',
            user_id=self._current_user_id,
            commit=False
        )

        return {
            'synced': True,
            'changes': [{'entity': 'family_member', 'count': len(personal_family)}],
            'log_ids': [log.id]
        }
