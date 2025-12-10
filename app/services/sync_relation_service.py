"""
관계형 데이터 동기화 서비스

학력, 경력, 자격증, 어학, 병역 등 관계형 데이터의 동기화를 담당합니다.
"""
from typing import Dict, Any
import json

from app.database import db
from app.models.employee import Employee
from app.models.personal_profile import PersonalProfile
from app.models.person_contract import SyncLog


class SyncRelationService:
    """관계형 데이터 동기화 처리"""

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정"""
        self._current_user_id = user_id

    def sync_relations(
        self,
        contract_id: int,
        profile: PersonalProfile,
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

        return {
            'synced_relations': synced_relations,
            'changes': changes,
            'log_ids': log_ids
        }

    def _sync_education(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """학력 정보 동기화"""
        from app.models.extended import Education

        personal_edus = list(profile.educations.all())
        if not personal_edus:
            return {'synced': False}

        # 기존 직원 학력 삭제 후 새로 추가 (전체 교체 방식)
        employee.educations.delete()

        for pe in personal_edus:
            edu = Education(
                employee_id=employee.id,
                school_type=pe.school_type,
                school_name=pe.school_name,
                major=pe.major,
                degree=pe.degree,
                admission_date=pe.admission_date,
                graduation_date=pe.graduation_date,
                status=pe.status,
            )
            db.session.add(edu)

        # 로그 생성
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='education',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_edus)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'education', 'count': len(personal_edus)}],
            'log_ids': [log.id]
        }

    def _sync_career(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """경력 정보 동기화"""
        from app.models.extended import Career

        personal_careers = list(profile.careers.all())
        if not personal_careers:
            return {'synced': False}

        employee.careers.delete()

        for pc in personal_careers:
            career = Career(
                employee_id=employee.id,
                company_name=pc.company_name,
                department=pc.department,
                position=pc.position,
                job_title=pc.job_title,
                start_date=pc.start_date,
                end_date=pc.end_date,
                is_current=pc.is_current,
                responsibilities=pc.responsibilities,
            )
            db.session.add(career)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='career',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_careers)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'career', 'count': len(personal_careers)}],
            'log_ids': [log.id]
        }

    def _sync_certificates(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """자격증 정보 동기화"""
        from app.models.extended import Certificate

        personal_certs = list(profile.certificates.all())
        if not personal_certs:
            return {'synced': False}

        employee.certificates.delete()

        for pc in personal_certs:
            cert = Certificate(
                employee_id=employee.id,
                name=pc.name,
                issuing_organization=pc.issuing_organization,
                issue_date=pc.issue_date,
                expiry_date=pc.expiry_date,
                certificate_number=pc.certificate_number,
            )
            db.session.add(cert)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='certificate',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_certs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'certificate', 'count': len(personal_certs)}],
            'log_ids': [log.id]
        }

    def _sync_languages(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """어학 능력 동기화"""
        from app.models.extended import Language

        personal_langs = list(profile.languages.all())
        if not personal_langs:
            return {'synced': False}

        employee.languages.delete()

        for pl in personal_langs:
            lang = Language(
                employee_id=employee.id,
                language=pl.language,
                proficiency=pl.proficiency,
                test_name=pl.test_name,
                score=pl.score,
                test_date=pl.test_date,
            )
            db.session.add(lang)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='language',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_langs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'language', 'count': len(personal_langs)}],
            'log_ids': [log.id]
        }

    def _sync_military(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """병역 정보 동기화"""
        from app.models.extended import MilitaryService

        personal_military = profile.military_service
        if not personal_military:
            return {'synced': False}

        # 기존 병역 정보 삭제
        if employee.military_service:
            db.session.delete(employee.military_service)

        military = MilitaryService(
            employee_id=employee.id,
            service_type=personal_military.service_type,
            branch=personal_military.branch,
            rank=personal_military.rank,
            start_date=personal_military.start_date,
            end_date=personal_military.end_date,
            discharge_type=personal_military.discharge_type,
        )
        db.session.add(military)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='military_service',
            field_name=None,
            old_value=None,
            new_value='synced',
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'military_service', 'synced': True}],
            'log_ids': [log.id]
        }
