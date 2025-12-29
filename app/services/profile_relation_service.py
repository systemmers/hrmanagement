"""
Profile Relation Service - 프로필 관련 데이터 통합 서비스

Personal과 Employee_Sub의 이력 CRUD를 통합합니다.
학력, 경력, 자격증, 어학, 병역 등 1:N 관계 데이터의 공통 처리를 제공합니다.

Phase 9: Personal/Employee_Sub 통합
- owner_type 파라미터로 profile_id/employee_id 구분
- RelationDataUpdater 패턴 활용

Phase 10: 트랜잭션 안전성 개선
- commit 파라미터로 트랜잭션 제어 (기본값: True, 하위 호환)
- 일괄 작업 시 commit=False로 호출 후 caller에서 단일 commit

Phase 27.1: 추가 관계 모델 CRUD
- FamilyMember, HrProject, ProjectParticipation, Award 추가
"""
from typing import Dict, List, Optional, Tuple, Type, Any

from app.types import OwnerType, JsonData
from dataclasses import dataclass

from ..database import db
from ..models import Education, Career, Certificate, Language, MilitaryService
from ..models.family_member import FamilyMember
from ..models.hr_project import HrProject
from ..models.project_participation import ProjectParticipation
from ..models.award import Award
from ..models.profile import Profile
from ..models.employee import Employee


@dataclass
class RelationOwner:
    """관계 데이터의 소유자 정보"""
    owner_type: str  # 'profile' | 'employee'
    owner_id: int
    owner_field: str  # 'profile_id' | 'employee_id'


class ProfileRelationService:
    """프로필 관련 데이터 통합 서비스

    Personal(profile_id)과 Employee_Sub(employee_id)의
    이력 데이터 CRUD를 통합 처리합니다.
    """

    # 모델 매핑
    MODEL_MAP = {
        'education': Education,
        'career': Career,
        'certificate': Certificate,
        'language': Language,
        'military': MilitaryService,
        'family': FamilyMember,
        'hr_project': HrProject,
        'project_participation': ProjectParticipation,
        'award': Award,
    }

    def _get_owner(self, owner_id: int, owner_type: OwnerType) -> RelationOwner:
        """소유자 정보 생성"""
        owner_field = 'profile_id' if owner_type == 'profile' else 'employee_id'
        return RelationOwner(
            owner_type=owner_type,
            owner_id=owner_id,
            owner_field=owner_field
        )

    def _get_filter_kwargs(self, owner: RelationOwner) -> Dict[str, int]:
        """소유자 기반 필터 조건 생성"""
        return {owner.owner_field: owner.owner_id}

    # ========================================
    # 학력 (Education) CRUD
    # ========================================

    def get_educations(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """학력 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        educations = Education.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).order_by(Education.graduation_date.desc()).all()
        return [e.to_dict() for e in educations]

    def add_education(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """학력 추가

        Args:
            commit: True면 즉시 커밋, False면 caller가 커밋 책임 (트랜잭션 안전성)
        """
        owner = self._get_owner(owner_id, owner_type)
        education = Education(
            **{owner.owner_field: owner_id},
            school_name=data.get('school_name'),
            school_type=data.get('school_type'),
            degree=data.get('degree'),
            major=data.get('major'),
            graduation_date=data.get('graduation_date'),
            gpa=data.get('gpa'),
            graduation_status=data.get('status') or data.get('graduation_status'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(education)
        if commit:
            db.session.commit()
        return education.to_dict()

    def delete_education(
        self,
        education_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """학력 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        education = Education.query.filter_by(
            id=education_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not education:
            return False
        db.session.delete(education)
        if commit:
            db.session.commit()
        return True

    def delete_all_educations(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 학력 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Education.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 경력 (Career) CRUD
    # ========================================

    def get_careers(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """경력 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        careers = Career.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).order_by(Career.start_date.desc()).all()
        return [c.to_dict() for c in careers]

    def add_career(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """경력 추가"""
        owner = self._get_owner(owner_id, owner_type)
        career = Career(
            **{owner.owner_field: owner_id},
            company_name=data.get('company_name'),
            department=data.get('department'),
            position=data.get('position'),
            # 직급 체계 필드
            job_grade=data.get('job_grade'),
            job_title=data.get('job_title'),
            job_role=data.get('job_role'),
            job_description=data.get('job_description') or data.get('responsibilities'),
            # 기간
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
            # 급여 체계 필드
            salary=data.get('salary'),
            salary_type=data.get('salary_type'),
            monthly_salary=data.get('monthly_salary'),
            pay_step=data.get('pay_step'),
            # 기타
            resignation_reason=data.get('resignation_reason'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(career)
        if commit:
            db.session.commit()
        return career.to_dict()

    def delete_career(
        self,
        career_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """경력 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        career = Career.query.filter_by(
            id=career_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not career:
            return False
        db.session.delete(career)
        if commit:
            db.session.commit()
        return True

    def delete_all_careers(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 경력 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Career.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 자격증 (Certificate) CRUD
    # ========================================

    def get_certificates(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """자격증 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        certificates = Certificate.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).order_by(Certificate.issue_date.desc()).all()
        return [c.to_dict() for c in certificates]

    def add_certificate(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """자격증 추가"""
        owner = self._get_owner(owner_id, owner_type)
        certificate = Certificate(
            **{owner.owner_field: owner_id},
            certificate_name=data.get('name') or data.get('certificate_name'),
            issuing_organization=data.get('issuer') or data.get('issuing_organization'),
            acquisition_date=data.get('issue_date') or data.get('acquisition_date'),
            expiry_date=data.get('expiry_date'),
            certificate_number=data.get('certificate_number'),
            grade=data.get('grade'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(certificate)
        if commit:
            db.session.commit()
        return certificate.to_dict()

    def delete_certificate(
        self,
        certificate_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """자격증 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        certificate = Certificate.query.filter_by(
            id=certificate_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not certificate:
            return False
        db.session.delete(certificate)
        if commit:
            db.session.commit()
        return True

    def delete_all_certificates(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 자격증 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Certificate.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 어학 (Language) CRUD
    # ========================================

    def get_languages(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """어학 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        languages = Language.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).all()
        return [lang.to_dict() for lang in languages]

    def add_language(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """어학 추가"""
        owner = self._get_owner(owner_id, owner_type)
        language = Language(
            **{owner.owner_field: owner_id},
            language_name=data.get('language_name') or data.get('language'),
            level=data.get('level') or data.get('proficiency'),
            exam_name=data.get('exam_name') or data.get('test_name'),
            score=data.get('score') or data.get('test_score'),
            acquisition_date=data.get('acquisition_date') or data.get('test_date'),
            note=data.get('note') or data.get('notes')
        )
        db.session.add(language)
        if commit:
            db.session.commit()
        return language.to_dict()

    def delete_language(
        self,
        language_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """어학 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        language = Language.query.filter_by(
            id=language_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not language:
            return False
        db.session.delete(language)
        if commit:
            db.session.commit()
        return True

    def delete_all_languages(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 어학 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Language.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 병역 (Military) CRUD
    # ========================================

    def get_military(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> Optional[Dict]:
        """병역 정보 조회 (1:1 관계)"""
        owner = self._get_owner(owner_id, owner_type)
        military = MilitaryService.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).first()
        return military.to_dict() if military else None

    def get_military_list(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """병역 목록 조회 (1:N 지원)"""
        owner = self._get_owner(owner_id, owner_type)
        militaries = MilitaryService.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).all()
        return [m.to_dict() for m in militaries]

    def add_military(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """병역 추가"""
        owner = self._get_owner(owner_id, owner_type)
        military = MilitaryService(
            **{owner.owner_field: owner_id},
            military_status=data.get('military_status') or data.get('status'),
            service_type=data.get('service_type') or data.get('duty'),
            branch=data.get('branch'),
            rank=data.get('rank'),
            enlistment_date=data.get('start_date') or data.get('enlistment_date'),
            discharge_date=data.get('end_date') or data.get('discharge_date'),
            discharge_reason=data.get('discharge_reason') or data.get('discharge_type'),
            exemption_reason=data.get('exemption_reason'),
            specialty=data.get('specialty'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(military)
        if commit:
            db.session.commit()
        return military.to_dict()

    def update_or_create_military(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """병역 정보 업데이트 또는 생성 (1:1 관계용)"""
        owner = self._get_owner(owner_id, owner_type)
        military = MilitaryService.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).first()

        if military:
            # 기존 데이터 업데이트
            military.military_status = data.get('military_status') or data.get('status')
            military.service_type = data.get('service_type') or data.get('duty')
            military.branch = data.get('branch')
            military.rank = data.get('rank')
            military.enlistment_date = data.get('start_date') or data.get('enlistment_date')
            military.discharge_date = data.get('end_date') or data.get('discharge_date')
            military.discharge_reason = data.get('discharge_reason') or data.get('discharge_type')
            military.exemption_reason = data.get('exemption_reason')
            military.specialty = data.get('specialty')
            military.note = data.get('notes') or data.get('note')
        else:
            # 새로 생성
            military = MilitaryService(
                **{owner.owner_field: owner_id},
                military_status=data.get('military_status') or data.get('status'),
                service_type=data.get('service_type') or data.get('duty'),
                branch=data.get('branch'),
                rank=data.get('rank'),
                enlistment_date=data.get('start_date') or data.get('enlistment_date'),
                discharge_date=data.get('end_date') or data.get('discharge_date'),
                discharge_reason=data.get('discharge_reason') or data.get('discharge_type'),
                exemption_reason=data.get('exemption_reason'),
                specialty=data.get('specialty'),
                note=data.get('notes') or data.get('note')
            )
            db.session.add(military)

        if commit:
            db.session.commit()
        return military.to_dict()

    def delete_military(
        self,
        military_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """병역 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        military = MilitaryService.query.filter_by(
            id=military_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not military:
            return False
        db.session.delete(military)
        if commit:
            db.session.commit()
        return True

    def delete_all_military(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 병역 정보 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = MilitaryService.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 가족 (FamilyMember) CRUD (Phase 27.1)
    # ========================================

    def get_families(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """가족 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        families = FamilyMember.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).all()
        return [f.to_dict() for f in families]

    def add_family(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """가족 추가"""
        owner = self._get_owner(owner_id, owner_type)
        family = FamilyMember(
            **{owner.owner_field: owner_id},
            relation=data.get('relation'),
            name=data.get('name'),
            birth_date=data.get('birth_date'),
            occupation=data.get('occupation'),
            contact=data.get('contact') or data.get('phone'),
            is_cohabitant=data.get('is_cohabitant', False),
            is_dependent=data.get('is_dependent', False),
            note=data.get('note') or data.get('notes')
        )
        db.session.add(family)
        if commit:
            db.session.commit()
        return family.to_dict()

    def delete_family(
        self,
        family_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """가족 삭제 (소유권 확인)"""
        owner = self._get_owner(owner_id, owner_type)
        family = FamilyMember.query.filter_by(
            id=family_id,
            **self._get_filter_kwargs(owner)
        ).first()
        if not family:
            return False
        db.session.delete(family)
        if commit:
            db.session.commit()
        return True

    def delete_all_families(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 가족 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = FamilyMember.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 인사이력 프로젝트 (HrProject) CRUD (Phase 27.1)
    # NOTE: HrProject는 employee_id만 지원 (profile_id 없음)
    # ========================================

    def get_hr_projects(
        self,
        owner_id: int,
        owner_type: OwnerType = 'employee'
    ) -> List[Dict]:
        """인사이력 프로젝트 목록 조회"""
        if owner_type != 'employee':
            return []  # HrProject는 employee만 지원
        projects = HrProject.query.filter_by(employee_id=owner_id).all()
        return [p.to_dict() for p in projects]

    def add_hr_project(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'employee',
        commit: bool = True
    ) -> Optional[Dict]:
        """인사이력 프로젝트 추가"""
        if owner_type != 'employee':
            return None  # HrProject는 employee만 지원
        project = HrProject(
            employee_id=owner_id,
            project_name=data.get('project_name') or data.get('name'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            role=data.get('role'),
            duty=data.get('duty'),
            client=data.get('client'),
            note=data.get('note') or data.get('notes')
        )
        db.session.add(project)
        if commit:
            db.session.commit()
        return project.to_dict()

    def delete_all_hr_projects(
        self,
        owner_id: int,
        owner_type: OwnerType = 'employee',
        commit: bool = True
    ) -> int:
        """모든 인사이력 프로젝트 삭제"""
        if owner_type != 'employee':
            return 0  # HrProject는 employee만 지원
        count = HrProject.query.filter_by(employee_id=owner_id).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 프로젝트 참여이력 (ProjectParticipation) CRUD (Phase 27.1)
    # ========================================

    def get_project_participations(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """프로젝트 참여이력 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        participations = ProjectParticipation.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).all()
        return [p.to_dict() for p in participations]

    def add_project_participation(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """프로젝트 참여이력 추가"""
        owner = self._get_owner(owner_id, owner_type)
        participation = ProjectParticipation(
            **{owner.owner_field: owner_id},
            project_name=data.get('project_name') or data.get('name'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            role=data.get('role'),
            duty=data.get('duty'),
            client=data.get('client'),
            note=data.get('note') or data.get('notes')
        )
        db.session.add(participation)
        if commit:
            db.session.commit()
        return participation.to_dict()

    def delete_all_project_participations(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 프로젝트 참여이력 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = ProjectParticipation.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 수상 (Award) CRUD (Phase 27.1)
    # ========================================

    def get_awards(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """수상 목록 조회"""
        owner = self._get_owner(owner_id, owner_type)
        awards = Award.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).all()
        return [a.to_dict() for a in awards]

    def add_award(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Dict:
        """수상 추가"""
        owner = self._get_owner(owner_id, owner_type)
        award = Award(
            **{owner.owner_field: owner_id},
            award_date=data.get('award_date') or data.get('date'),
            award_name=data.get('award_name') or data.get('name'),
            institution=data.get('institution') or data.get('issuer'),
            note=data.get('note') or data.get('notes')
        )
        db.session.add(award)
        if commit:
            db.session.commit()
        return award.to_dict()

    def delete_all_awards(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """모든 수상 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Award.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        if commit:
            db.session.commit()
        return count

    # ========================================
    # 통합 조회 메서드
    # ========================================

    def get_all_relations(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> Dict[str, List[Dict]]:
        """모든 관계 데이터 한번에 조회"""
        return {
            'educations': self.get_educations(owner_id, owner_type),
            'careers': self.get_careers(owner_id, owner_type),
            'certificates': self.get_certificates(owner_id, owner_type),
            'languages': self.get_languages(owner_id, owner_type),
            'military': self.get_military_list(owner_id, owner_type),
        }

    def get_relation_counts(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> Dict[str, int]:
        """관계 데이터 카운트 조회"""
        owner = self._get_owner(owner_id, owner_type)
        filter_kwargs = self._get_filter_kwargs(owner)

        return {
            'education_count': Education.query.filter_by(**filter_kwargs).count(),
            'career_count': Career.query.filter_by(**filter_kwargs).count(),
            'certificate_count': Certificate.query.filter_by(**filter_kwargs).count(),
            'language_count': Language.query.filter_by(**filter_kwargs).count(),
            'military_count': MilitaryService.query.filter_by(**filter_kwargs).count(),
        }


# 싱글톤 인스턴스
profile_relation_service = ProfileRelationService()
