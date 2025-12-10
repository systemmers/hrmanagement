"""
Profile Adapter - 법인/개인 계정 데이터 모델 통합 어댑터

데이터 모델 차이를 추상화하여 템플릿에서 일관된 인터페이스 제공
- EmployeeProfileAdapter: 법인 직원용 (Employee 모델)
- PersonalProfileAdapter: 일반 개인용 (PersonalProfile 모델)
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional


class ProfileAdapter(ABC):
    """프로필 데이터 접근을 위한 추상 어댑터"""

    @abstractmethod
    def get_basic_info(self) -> Dict[str, Any]:
        """기본 정보 (이름, 연락처 등) 반환"""
        pass

    @abstractmethod
    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """소속 정보 반환 (법인 전용, 개인은 None)"""
        pass

    @abstractmethod
    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환 (법인 전용)"""
        pass

    @abstractmethod
    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환"""
        pass

    @abstractmethod
    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환"""
        pass

    @abstractmethod
    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환"""
        pass

    @abstractmethod
    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환"""
        pass

    @abstractmethod
    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환"""
        pass

    @abstractmethod
    def is_corporate(self) -> bool:
        """법인 직원 여부"""
        pass

    @abstractmethod
    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        pass

    @abstractmethod
    def get_profile_id(self) -> int:
        """프로필 ID 반환"""
        pass

    @abstractmethod
    def get_display_name(self) -> str:
        """표시용 이름 반환"""
        pass

    @abstractmethod
    def get_photo_url(self) -> Optional[str]:
        """프로필 사진 URL 반환"""
        pass


class EmployeeProfileAdapter(ProfileAdapter):
    """법인 직원용 어댑터 (Employee 모델 래핑)"""

    AVAILABLE_SECTIONS = [
        'basic', 'organization', 'contract', 'salary',
        'benefit', 'insurance', 'education', 'career',
        'certificate', 'language', 'military',
        'employment_contract', 'personnel_movement', 'attendance_assets'
    ]

    def __init__(self, employee):
        """
        Args:
            employee: Employee 모델 인스턴스
        """
        self.employee = employee

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 개인정보 반환"""
        return {
            'id': self.employee.id,
            'name': self.employee.name,
            'english_name': self.employee.english_name,
            'chinese_name': self.employee.chinese_name,
            'birth_date': self.employee.birth_date,
            'lunar_birth': self.employee.lunar_birth,
            'gender': self.employee.gender,
            'mobile_phone': self.employee.mobile_phone,
            'home_phone': self.employee.home_phone,
            'email': self.employee.email,
            'address': self.employee.address,
            'detailed_address': self.employee.detailed_address,
            'postal_code': self.employee.postal_code,
            'photo': self.employee.photo,
            'employee_number': self.employee.employee_number,
            'nationality': self.employee.nationality,
            'blood_type': self.employee.blood_type,
            'religion': self.employee.religion,
            'hobby': self.employee.hobby,
            'specialty': self.employee.specialty,
            'disability_info': self.employee.disability_info,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """소속 정보 반환"""
        return {
            'organization': self.employee.organization.to_dict() if self.employee.organization else None,
            'organization_id': self.employee.organization_id,
            'department': self.employee.department,
            'position': self.employee.position,
            'team': self.employee.team,
            'job_title': self.employee.job_title,
            'hire_date': self.employee.hire_date,
            'status': self.employee.status,
            'work_location': self.employee.work_location,
            'internal_phone': self.employee.internal_phone,
            'company_email': self.employee.company_email,
        }

    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환"""
        if self.employee.contract:
            return self.employee.contract.to_dict()
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환"""
        if self.employee.salary:
            return self.employee.salary.to_dict()
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환"""
        if self.employee.benefit:
            return self.employee.benefit.to_dict()
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환"""
        if self.employee.insurance:
            return self.employee.insurance.to_dict()
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환"""
        return [edu.to_dict() for edu in self.employee.educations.all()]

    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환"""
        return [career.to_dict() for career in self.employee.careers.all()]

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환"""
        return [cert.to_dict() for cert in self.employee.certificates.all()]

    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환"""
        return [lang.to_dict() for lang in self.employee.languages.all()]

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환"""
        if self.employee.military_service:
            return self.employee.military_service.to_dict()
        return None

    def get_family_list(self) -> List[Dict[str, Any]]:
        """가족 정보 목록 반환 (법인 전용)"""
        return [member.to_dict() for member in self.employee.family_members.all()]

    def get_salary_history_list(self) -> List[Dict[str, Any]]:
        """급여 이력 목록 반환 (법인 전용)"""
        return [hist.to_dict() for hist in self.employee.salary_histories.all()]

    def get_promotion_list(self) -> List[Dict[str, Any]]:
        """승진 이력 목록 반환 (법인 전용)"""
        return [promo.to_dict() for promo in self.employee.promotions.all()]

    def get_evaluation_list(self) -> List[Dict[str, Any]]:
        """평가 목록 반환 (법인 전용)"""
        return [eval_.to_dict() for eval_ in self.employee.evaluations.all()]

    def get_training_list(self) -> List[Dict[str, Any]]:
        """교육 이력 목록 반환 (법인 전용)"""
        return [train.to_dict() for train in self.employee.trainings.all()]

    def get_attendance_list(self) -> List[Dict[str, Any]]:
        """근태 기록 목록 반환 (법인 전용)"""
        return [att.to_dict() for att in self.employee.attendances.all()]

    def get_project_list(self) -> List[Dict[str, Any]]:
        """프로젝트 목록 반환"""
        return [proj.to_dict() for proj in self.employee.projects.all()]

    def get_award_list(self) -> List[Dict[str, Any]]:
        """수상 이력 목록 반환"""
        return [award.to_dict() for award in self.employee.awards.all()]

    def get_asset_list(self) -> List[Dict[str, Any]]:
        """비품 목록 반환 (법인 전용)"""
        return [asset.to_dict() for asset in self.employee.assets.all()]

    def is_corporate(self) -> bool:
        """법인 직원 여부 (항상 True)"""
        return True

    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        return self.AVAILABLE_SECTIONS.copy()

    def get_profile_id(self) -> int:
        """프로필 ID (employee.id)"""
        return self.employee.id

    def get_display_name(self) -> str:
        """표시용 이름 (이름 + 직급)"""
        parts = [self.employee.name]
        if self.employee.position:
            parts.append(self.employee.position)
        return ' '.join(parts)

    def get_photo_url(self) -> Optional[str]:
        """프로필 사진 URL"""
        return self.employee.photo


class PersonalProfileAdapter(ProfileAdapter):
    """일반 개인용 어댑터 (PersonalProfile 모델 래핑)"""

    AVAILABLE_SECTIONS = [
        'basic', 'education', 'career',
        'certificate', 'language', 'military'
    ]

    def __init__(self, profile):
        """
        Args:
            profile: PersonalProfile 모델 인스턴스
        """
        self.profile = profile

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 개인정보 반환"""
        return {
            'id': self.profile.id,
            'name': self.profile.name,
            'english_name': self.profile.english_name,
            'chinese_name': self.profile.chinese_name,
            'birth_date': self.profile.birth_date,
            'lunar_birth': self.profile.lunar_birth,
            'gender': self.profile.gender,
            'mobile_phone': self.profile.mobile_phone,
            'home_phone': self.profile.home_phone,
            'email': self.profile.email,
            'address': self.profile.address,
            'detailed_address': self.profile.detailed_address,
            'postal_code': self.profile.postal_code,
            'photo': self.profile.photo,
            'employee_number': None,  # 개인은 사번 없음
            'nationality': self.profile.nationality,
            'blood_type': self.profile.blood_type,
            'religion': self.profile.religion,
            'hobby': self.profile.hobby,
            'specialty': self.profile.specialty,
            'disability_info': self.profile.disability_info,
            'is_public': self.profile.is_public,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """소속 정보 반환 (개인은 None)"""
        return None

    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환 (개인은 None)"""
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환 (개인은 None)"""
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환 (개인은 None)"""
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환 (개인은 None)"""
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환 (PersonalEducation 사용)"""
        return [edu.to_dict() for edu in self.profile.educations.all()]

    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환 (PersonalCareer 사용)"""
        return [career.to_dict() for career in self.profile.careers.all()]

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환 (PersonalCertificate 사용)"""
        return [cert.to_dict() for cert in self.profile.certificates.all()]

    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환 (PersonalLanguage 사용)"""
        return [lang.to_dict() for lang in self.profile.languages.all()]

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환 (PersonalMilitaryService 사용)"""
        if self.profile.military_service:
            return self.profile.military_service.to_dict()
        return None

    def is_corporate(self) -> bool:
        """법인 직원 여부 (항상 False)"""
        return False

    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        return self.AVAILABLE_SECTIONS.copy()

    def get_profile_id(self) -> int:
        """프로필 ID (profile.id)"""
        return self.profile.id

    def get_display_name(self) -> str:
        """표시용 이름"""
        return self.profile.name

    def get_photo_url(self) -> Optional[str]:
        """프로필 사진 URL"""
        return self.profile.photo

    def get_user_id(self) -> int:
        """연결된 User ID"""
        return self.profile.user_id
