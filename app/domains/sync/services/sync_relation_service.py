"""
관계형 데이터 동기화 서비스

학력, 경력, 자격증, 어학, 병역 등 관계형 데이터의 동기화를 담당합니다.

Phase 30: 레이어 분리 - db.session 제거, Repository 패턴 적용
Phase 33: 첨부파일 동기화 추가
"""
from typing import Dict, Any, List
import json
import os
import shutil
from datetime import datetime

from app.domains.employee.models import Employee
from app.domains.employee.models import Profile
from app.domains.contract.models import SyncLog


class SyncRelationService:
    """관계형 데이터 동기화 처리

    Phase 30: Repository DI 패턴 적용
    Phase 33: 첨부파일 동기화 추가
    """

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id
        # Repository 지연 초기화용
        self._sync_log_repo = None
        self._education_repo = None
        self._career_repo = None
        self._certificate_repo = None
        self._language_repo = None
        self._family_repo = None
        self._attachment_repo = None

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
    def family_repo(self):
        """지연 초기화된 FamilyMember Repository"""
        if self._family_repo is None:
            from app.domains.employee.repositories import FamilyMemberRepository
            self._family_repo = FamilyMemberRepository()
        return self._family_repo

    @property
    def attachment_repo(self):
        """지연 초기화된 Attachment Repository"""
        if self._attachment_repo is None:
            from app.domains.attachment.repositories import attachment_repository
            self._attachment_repo = attachment_repository
        return self._attachment_repo

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

        # 가족 동기화
        if syncable.get('family'):
            result = self._sync_family_members(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('family')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # Phase 33: 첨부파일 동기화 (DataSharingSettings 기반)
        if syncable.get('attachments', True):  # 기본값 True
            result = self._sync_attachments(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('attachments')
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

    def _sync_attachments(
        self,
        contract_id: int,
        profile: Profile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """첨부파일 동기화 (Phase 33)

        DataSharingSettings에 따라 개인 프로필 첨부파일을 직원으로 동기화합니다.
        파일은 복제되고 source 추적 정보가 설정됩니다.

        Args:
            contract_id: 계약 ID
            profile: 개인 프로필
            employee: 직원 객체
            sync_type: 동기화 유형

        Returns:
            동기화 결과
        """
        from flask import current_app
        from app.domains.attachment.models import Attachment, SourceType
        from app.domains.attachment.constants import AttachmentCategory, OwnerType
        from app.domains.attachment.services import attachment_service
        from app.domains.contract.services import contract_service

        # DataSharingSettings 조회
        data_sharing = contract_service.get_data_sharing_settings(contract_id)
        if not data_sharing:
            return {'synced': False}

        # 동기화 대상 카테고리 결정
        sync_categories = []
        if data_sharing.share_profile_photo:
            sync_categories.append(AttachmentCategory.PROFILE_PHOTO)
        if data_sharing.share_documents:
            sync_categories.append(AttachmentCategory.DOCUMENT)

        if not sync_categories:
            return {'synced': False}

        # 프로필 첨부파일 조회
        profile_attachments = self.attachment_repo.get_by_owner(
            OwnerType.PROFILE, profile.id
        )

        if not profile_attachments:
            return {'synced': False}

        synced_count = 0
        log_ids = []

        for pa in profile_attachments:
            # 카테고리 필터링
            if pa.category not in sync_categories:
                continue

            # 기존 동기화된 파일 삭제 (같은 계약에서 동기화된 것만)
            self._delete_synced_attachments_by_category(
                employee.id, pa.category, contract_id
            )

            # 파일 복제 (실제 파일 복사)
            new_file_path = self._copy_attachment_file(
                pa.file_path,
                OwnerType.EMPLOYEE,
                employee.id,
                pa.category
            )

            if not new_file_path:
                continue

            # 새 Attachment 레코드 생성 (source 추적 정보 포함)
            new_attachment = Attachment(
                owner_type=OwnerType.EMPLOYEE,
                owner_id=employee.id,
                employee_id=employee.id,  # 레거시 호환
                file_name=pa.file_name,
                file_path=new_file_path,
                file_type=pa.file_type,
                file_size=pa.file_size,
                category=pa.category,
                upload_date=datetime.now().strftime('%Y-%m-%d'),
                note=pa.note,
                display_order=pa.display_order,
                # Phase 33: source 추적
                source_type=SourceType.SYNCED,
                source_contract_id=contract_id,
                is_deletable_on_termination=True,
            )
            self.attachment_repo.create_model(new_attachment, commit=False)
            synced_count += 1

        if synced_count > 0:
            log = self.sync_log_repo.create_log(
                contract_id=contract_id,
                sync_type=sync_type,
                entity_type='attachment',
                field_name=None,
                old_value=None,
                new_value=json.dumps({'count': synced_count, 'categories': sync_categories}),
                direction='personal_to_employee',
                user_id=self._current_user_id,
                commit=False
            )
            log_ids.append(log.id)

        return {
            'synced': synced_count > 0,
            'changes': [{'entity': 'attachment', 'count': synced_count}] if synced_count > 0 else [],
            'log_ids': log_ids
        }

    def _delete_synced_attachments_by_category(
        self,
        employee_id: int,
        category: str,
        contract_id: int
    ) -> int:
        """특정 계약에서 동기화된 특정 카테고리 첨부파일 삭제

        Args:
            employee_id: 직원 ID
            category: 카테고리
            contract_id: 계약 ID

        Returns:
            삭제된 개수
        """
        from app.domains.attachment.models import Attachment, SourceType
        from app.domains.attachment.constants import OwnerType

        attachments = Attachment.query.filter(
            Attachment.owner_type == OwnerType.EMPLOYEE,
            Attachment.owner_id == employee_id,
            Attachment.category == category,
            Attachment.source_type == SourceType.SYNCED,
            Attachment.source_contract_id == contract_id
        ).all()

        count = 0
        for att in attachments:
            # 파일 삭제는 선택사항 (파일 시스템 정리는 별도 처리)
            self.attachment_repo.delete(att.id, commit=False)
            count += 1

        return count

    def _copy_attachment_file(
        self,
        source_path: str,
        target_owner_type: str,
        target_owner_id: int,
        category: str
    ) -> str:
        """첨부파일 복제

        Args:
            source_path: 원본 파일 경로 (웹 경로)
            target_owner_type: 대상 소유자 타입
            target_owner_id: 대상 소유자 ID
            category: 카테고리

        Returns:
            새 파일 웹 경로 (실패 시 None)
        """
        from flask import current_app
        import uuid

        if not source_path:
            return None

        # 웹 경로 → 파일 시스템 경로 변환
        # /static/uploads/... → {static_folder}/uploads/...
        if source_path.startswith('/static/'):
            relative_path = source_path[8:]  # '/static/' 제거
            source_file_path = os.path.join(current_app.static_folder, relative_path)
        else:
            return None

        if not os.path.exists(source_file_path):
            return None

        # 대상 폴더 생성
        target_folder = os.path.join(
            current_app.static_folder,
            'uploads',
            'attachments'
        )
        os.makedirs(target_folder, exist_ok=True)

        # 새 파일명 생성
        _, ext = os.path.splitext(source_path)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_id = uuid.uuid4().hex[:6]
        new_filename = f"{target_owner_type}_{target_owner_id}_{timestamp}_{unique_id}{ext}"
        target_file_path = os.path.join(target_folder, new_filename)

        try:
            shutil.copy2(source_file_path, target_file_path)
            return f"/static/uploads/attachments/{new_filename}"
        except Exception:
            return None
