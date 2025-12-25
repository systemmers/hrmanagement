"""
Profile Relation Service - 프로필 관련 데이터 통합 서비스

Personal과 Employee_Sub의 이력 CRUD를 통합합니다.
학력, 경력, 자격증, 어학, 병역 등 1:N 관계 데이터의 공통 처리를 제공합니다.

Phase 9: Personal/Employee_Sub 통합
- owner_type 파라미터로 profile_id/employee_id 구분
- RelationDataUpdater 패턴 활용
"""
from typing import Dict, List, Optional, Tuple, Type
from dataclasses import dataclass

from ..database import db
from ..models import Education, Career, Certificate, Language, MilitaryService
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
    }

    def _get_owner(self, owner_id: int, owner_type: str) -> RelationOwner:
        """소유자 정보 생성"""
        owner_field = 'profile_id' if owner_type == 'profile' else 'employee_id'
        return RelationOwner(
            owner_type=owner_type,
            owner_id=owner_id,
            owner_field=owner_field
        )

    def _get_filter_kwargs(self, owner: RelationOwner) -> Dict:
        """소유자 기반 필터 조건 생성"""
        return {owner.owner_field: owner.owner_id}

    # ========================================
    # 학력 (Education) CRUD
    # ========================================

    def get_educations(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
    ) -> Dict:
        """학력 추가"""
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
        db.session.commit()
        return education.to_dict()

    def delete_education(
        self,
        education_id: int,
        owner_id: int,
        owner_type: str = 'profile'
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
        db.session.commit()
        return True

    def delete_all_educations(
        self,
        owner_id: int,
        owner_type: str = 'profile'
    ) -> int:
        """모든 학력 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Education.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        db.session.commit()
        return count

    # ========================================
    # 경력 (Career) CRUD
    # ========================================

    def get_careers(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
    ) -> Dict:
        """경력 추가"""
        owner = self._get_owner(owner_id, owner_type)
        career = Career(
            **{owner.owner_field: owner_id},
            company_name=data.get('company_name'),
            department=data.get('department'),
            position=data.get('position'),
            job_description=data.get('job_description'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date'),
            is_current=data.get('is_current', False),
            salary=data.get('salary'),
            resignation_reason=data.get('resignation_reason'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(career)
        db.session.commit()
        return career.to_dict()

    def delete_career(
        self,
        career_id: int,
        owner_id: int,
        owner_type: str = 'profile'
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
        db.session.commit()
        return True

    def delete_all_careers(
        self,
        owner_id: int,
        owner_type: str = 'profile'
    ) -> int:
        """모든 경력 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Career.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        db.session.commit()
        return count

    # ========================================
    # 자격증 (Certificate) CRUD
    # ========================================

    def get_certificates(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
    ) -> Dict:
        """자격증 추가"""
        owner = self._get_owner(owner_id, owner_type)
        certificate = Certificate(
            **{owner.owner_field: owner_id},
            name=data.get('name'),
            issuer=data.get('issuer'),
            issue_date=data.get('issue_date'),
            expiry_date=data.get('expiry_date'),
            certificate_number=data.get('certificate_number'),
            grade=data.get('grade'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate.to_dict()

    def delete_certificate(
        self,
        certificate_id: int,
        owner_id: int,
        owner_type: str = 'profile'
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
        db.session.commit()
        return True

    def delete_all_certificates(
        self,
        owner_id: int,
        owner_type: str = 'profile'
    ) -> int:
        """모든 자격증 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Certificate.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        db.session.commit()
        return count

    # ========================================
    # 어학 (Language) CRUD
    # ========================================

    def get_languages(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
    ) -> Dict:
        """어학 추가"""
        owner = self._get_owner(owner_id, owner_type)
        language = Language(
            **{owner.owner_field: owner_id},
            language_name=data.get('language_name') or data.get('language'),
            proficiency=data.get('proficiency') or data.get('level'),
            test_name=data.get('test_name'),
            test_score=data.get('test_score'),
            test_date=data.get('test_date'),
            note=data.get('notes') or data.get('note')
        )
        db.session.add(language)
        db.session.commit()
        return language.to_dict()

    def delete_language(
        self,
        language_id: int,
        owner_id: int,
        owner_type: str = 'profile'
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
        db.session.commit()
        return True

    def delete_all_languages(
        self,
        owner_id: int,
        owner_type: str = 'profile'
    ) -> int:
        """모든 어학 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = Language.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        db.session.commit()
        return count

    # ========================================
    # 병역 (Military) CRUD
    # ========================================

    def get_military(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
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
            note=data.get('notes') or data.get('note')
        )
        db.session.add(military)
        db.session.commit()
        return military.to_dict()

    def update_or_create_military(
        self,
        owner_id: int,
        data: Dict,
        owner_type: str = 'profile'
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
                note=data.get('notes') or data.get('note')
            )
            db.session.add(military)

        db.session.commit()
        return military.to_dict()

    def delete_military(
        self,
        military_id: int,
        owner_id: int,
        owner_type: str = 'profile'
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
        db.session.commit()
        return True

    def delete_all_military(
        self,
        owner_id: int,
        owner_type: str = 'profile'
    ) -> int:
        """모든 병역 정보 삭제"""
        owner = self._get_owner(owner_id, owner_type)
        count = MilitaryService.query.filter_by(
            **self._get_filter_kwargs(owner)
        ).delete()
        db.session.commit()
        return count

    # ========================================
    # 통합 조회 메서드
    # ========================================

    def get_all_relations(
        self,
        owner_id: int,
        owner_type: str = 'profile'
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
        owner_type: str = 'profile'
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
