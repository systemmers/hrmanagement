"""
PersonalProfile Repository

개인 프로필 및 관련 데이터(학력, 경력, 자격증, 어학, 병역)의 CRUD 기능을 제공합니다.

Phase 1 리팩토링: BaseProfileRelationRepository 및 BaseProfileOneToOneRepository 활용
"""
from typing import List, Optional, Dict
from app.database import db
from app.models.personal import (
    PersonalProfile, PersonalEducation, PersonalCareer,
    PersonalCertificate, PersonalLanguage, PersonalMilitaryService
)
from .base_repository import BaseRepository, BaseProfileRelationRepository, BaseProfileOneToOneRepository


class PersonalProfileRepository(BaseRepository):
    """개인 프로필 저장소"""

    def __init__(self):
        super().__init__(PersonalProfile)

    def get_by_user_id(self, user_id: int) -> Optional[PersonalProfile]:
        """사용자 ID로 프로필 조회 (모델 객체 반환)"""
        return PersonalProfile.query.filter_by(user_id=user_id).first()

    def get_dict_by_user_id(self, user_id: int) -> Optional[Dict]:
        """사용자 ID로 프로필 조회 (딕셔너리 반환)"""
        profile = self.get_by_user_id(user_id)
        return profile.to_dict() if profile else None

    def create_profile(self, user_id: int, name: str, **kwargs) -> PersonalProfile:
        """새 프로필 생성"""
        profile = PersonalProfile(
            user_id=user_id,
            name=name,
            email=kwargs.get('email'),
            mobile_phone=kwargs.get('mobile_phone'),
            english_name=kwargs.get('english_name'),
            chinese_name=kwargs.get('chinese_name'),
            birth_date=kwargs.get('birth_date'),
            gender=kwargs.get('gender'),
            is_public=kwargs.get('is_public', False)
        )
        db.session.add(profile)
        db.session.commit()
        return profile

    def update_profile(self, profile: PersonalProfile, data: Dict) -> PersonalProfile:
        """프로필 정보 수정"""
        allowed_fields = [
            'name', 'english_name', 'chinese_name', 'resident_number',
            'birth_date', 'lunar_birth', 'gender', 'photo',
            'mobile_phone', 'home_phone', 'email', 'postal_code',
            'address', 'detailed_address', 'nationality', 'blood_type',
            'religion', 'hobby', 'specialty', 'is_public'
        ]
        for field in allowed_fields:
            if field in data:
                setattr(profile, field, data[field])
        db.session.commit()
        return profile

    def get_profile_stats(self, profile: PersonalProfile) -> Dict:
        """프로필 통계 정보"""
        return {
            'education_count': profile.educations.count() if profile.educations else 0,
            'career_count': profile.careers.count() if profile.careers else 0,
            'certificate_count': profile.certificates.count() if profile.certificates else 0,
            'language_count': profile.languages.count() if profile.languages else 0,
            'has_military': profile.military_service is not None
        }


class PersonalEducationRepository(BaseProfileRelationRepository):
    """개인 학력 저장소 (BaseProfileRelationRepository 상속)"""

    def __init__(self):
        super().__init__(PersonalEducation)

    def create(self, profile_id: int, data: Dict) -> PersonalEducation:
        """학력 추가 (필드 매핑 포함)"""
        return self.create_for_profile(profile_id, {
            'school_type': data.get('school_type'),
            'school_name': data.get('school_name'),
            'major': data.get('major'),
            'degree': data.get('degree'),
            'admission_date': data.get('admission_date'),
            'graduation_date': data.get('graduation_date'),
            'status': data.get('status'),
            'gpa': data.get('gpa'),
            'notes': data.get('notes')
        })


class PersonalCareerRepository(BaseProfileRelationRepository):
    """개인 경력 저장소 (BaseProfileRelationRepository 상속)"""

    def __init__(self):
        super().__init__(PersonalCareer)

    def create(self, profile_id: int, data: Dict) -> PersonalCareer:
        """경력 추가 (필드 매핑 포함)"""
        return self.create_for_profile(profile_id, {
            'company_name': data.get('company_name'),
            'department': data.get('department'),
            'position': data.get('position'),
            'job_title': data.get('job_title'),
            'job_grade': data.get('job_grade'),
            'job_role': data.get('job_role'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'is_current': data.get('is_current', False),
            'responsibilities': data.get('responsibilities'),
            'achievements': data.get('achievements'),
            'reason_for_leaving': data.get('reason_for_leaving'),
            'salary_type': data.get('salary_type'),
            'salary': data.get('salary'),
            'monthly_salary': data.get('monthly_salary'),
            'pay_step': data.get('pay_step')
        })


class PersonalCertificateRepository(BaseProfileRelationRepository):
    """개인 자격증 저장소 (BaseProfileRelationRepository 상속)"""

    def __init__(self):
        super().__init__(PersonalCertificate)

    def create(self, profile_id: int, data: Dict) -> PersonalCertificate:
        """자격증 추가 (필드 매핑 포함)"""
        return self.create_for_profile(profile_id, {
            'name': data.get('name'),
            'issuing_organization': data.get('issuing_organization'),
            'issue_date': data.get('issue_date'),
            'expiry_date': data.get('expiry_date'),
            'certificate_number': data.get('certificate_number'),
            'grade': data.get('grade'),
            'notes': data.get('notes')
        })


class PersonalLanguageRepository(BaseProfileRelationRepository):
    """개인 어학 저장소 (BaseProfileRelationRepository 상속)"""

    def __init__(self):
        super().__init__(PersonalLanguage)

    def create(self, profile_id: int, data: Dict) -> PersonalLanguage:
        """어학 추가 (필드 매핑 포함)"""
        return self.create_for_profile(profile_id, {
            'language': data.get('language'),
            'proficiency': data.get('proficiency'),
            'test_name': data.get('test_name'),
            'score': data.get('score'),
            'test_date': data.get('test_date'),
            'notes': data.get('notes')
        })


class PersonalMilitaryRepository(BaseProfileOneToOneRepository):
    """개인 병역 저장소 (BaseProfileOneToOneRepository 상속)"""

    def __init__(self):
        super().__init__(PersonalMilitaryService)

    def save(self, profile_id: int, data: Dict) -> PersonalMilitaryService:
        """병역 정보 저장/수정 (upsert)"""
        return self.save_for_profile(profile_id, {
            'service_type': data.get('service_type'),
            'branch': data.get('branch'),
            'rank': data.get('rank'),
            'start_date': data.get('start_date'),
            'end_date': data.get('end_date'),
            'discharge_type': data.get('discharge_type'),
            'specialty': data.get('specialty'),
            'duty': data.get('duty'),
            'notes': data.get('notes')
        })
