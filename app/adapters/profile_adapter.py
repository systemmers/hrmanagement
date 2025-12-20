"""
Profile Adapter - 법인/개인 계정 데이터 모델 통합 어댑터

데이터 모델 차이를 추상화하여 템플릿에서 일관된 인터페이스 제공
- EmployeeProfileAdapter: 법인 직원용 (Employee 모델)
- PersonalProfileAdapter: 일반 개인용 (PersonalProfile 모델)
- CorporateAdminProfileAdapter: 법인 관리자용 (CorporateAdminProfile 모델)
- create_profile_adapter(): 팩토리 함수
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Union


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

    @abstractmethod
    def get_account_type(self) -> str:
        """계정 타입 반환 ('corporate', 'personal', 'corporate_admin')"""
        pass

    def is_section_visible(self, section_name: str) -> bool:
        """
        섹션 가시성 확인

        Phase 6 최적화: 섹션 가시성 로직 통합
        템플릿에서 {% if adapter.is_section_visible('education') %} 형태로 사용

        Args:
            section_name: 섹션 이름

        Returns:
            해당 섹션이 표시 가능한지 여부
        """
        return section_name in self.get_available_sections()

    def get_section_visibility(self) -> Dict[str, bool]:
        """
        모든 섹션의 가시성 딕셔너리 반환

        템플릿에서 {% if sections.education %} 형태로 사용
        """
        all_sections = [
            'basic', 'organization', 'contract', 'salary',
            'benefit', 'insurance', 'education', 'career',
            'certificate', 'language', 'military', 'family',
            'award', 'project_participation', 'hr_project',
            'employment_contract', 'personnel_movement', 'attendance_assets',
            'company_info'
        ]
        available = set(self.get_available_sections())
        return {section: section in available for section in all_sections}

    def to_template_context(self, variable_name: str = 'profile') -> Dict[str, Any]:
        """
        템플릿 렌더링용 통합 컨텍스트 생성

        Phase 6 최적화: 중복 호출 제거, 캐싱 적용

        Args:
            variable_name: 템플릿에서 사용할 변수명 ('employee' 또는 'profile')

        Returns:
            템플릿에 전달할 컨텍스트 딕셔너리
        """
        # 기본 정보 (1회만 호출)
        basic = self.get_basic_info()

        # 이력 데이터 (1회만 호출, 캐싱 효과)
        educations = self.get_education_list()
        careers = self.get_career_list()
        certificates = self.get_certificate_list()
        languages = self.get_language_list()
        military = self.get_military_info()
        awards = self.get_award_list() if hasattr(self, 'get_award_list') else []
        family = self.get_family_list() if hasattr(self, 'get_family_list') else []
        project_participations = self.get_project_participation_list() if hasattr(self, 'get_project_participation_list') else []

        # 통합 프로필 객체 생성 (템플릿에서 employee.name 또는 profile.name 형태로 접근)
        profile_obj = type('ProfileContext', (), {
            **basic,
            'id': self.get_profile_id(),
            'photo': self.get_photo_url(),
            # 이력 데이터 속성 추가 (템플릿에서 employee.educations 접근 가능)
            'educations': educations,
            'careers': careers,
            'certificates': certificates,
            'languages': languages,
            'military_service': military,
            'awards': awards,
            'family_members': family,
            'project_participations': project_participations,
        })()

        # 컨텍스트 구성 (중복 호출 제거)
        context = {
            variable_name: profile_obj,
            'adapter': self,  # 어댑터 직접 접근 (섹션 가시성 확인용)
            'is_corporate': self.is_corporate(),
            'account_type': self.get_account_type(),
            'available_sections': self.get_available_sections(),
            'sections': self.get_section_visibility(),  # 섹션 가시성 딕셔너리
            # 기본/이력 데이터 (이미 조회한 값 재사용)
            'basic_info': basic,
            'organization_info': self.get_organization_info(),
            'education_list': educations,
            'career_list': careers,
            'certificate_list': certificates,
            'language_list': languages,
            'military': military,
            'award_list': awards,
            'family_list': family,
            'project_participation_list': project_participations,
        }

        # 법인 전용 필드 (조건부 추가)
        if self.is_corporate():
            context.update({
                'contract_info': self.get_contract_info(),
                'salary_info': self.get_salary_info(),
                'benefit_info': self.get_benefit_info(),
                'insurance_info': self.get_insurance_info(),
            })

        return context


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
            'marital_status': self.employee.marital_status,
            # 실제 거주 주소
            'actual_postal_code': self.employee.actual_postal_code,
            'actual_address': self.employee.actual_address,
            'actual_detailed_address': self.employee.actual_detailed_address,
            # 비상연락처
            'emergency_contact': self.employee.emergency_contact,
            'emergency_relation': self.employee.emergency_relation,
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

    def get_hr_project_list(self) -> List[Dict[str, Any]]:
        """인사이력 프로젝트 목록 반환 (법인 전용)"""
        return [proj.to_dict() for proj in self.employee.hr_projects.all()]

    def get_project_participation_list(self) -> List[Dict[str, Any]]:
        """프로젝트 참여이력 목록 반환"""
        return [proj.to_dict() for proj in self.employee.project_participations.all()]

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

    def get_account_type(self) -> str:
        """계정 타입 반환"""
        return 'corporate'


class PersonalProfileAdapter(ProfileAdapter):
    """일반 개인용 어댑터 (PersonalProfile 모델 래핑)"""

    AVAILABLE_SECTIONS = [
        'basic', 'education', 'career',
        'certificate', 'language', 'military', 'award', 'project_participation'
    ]

    def __init__(self, profile):
        """
        Args:
            profile: PersonalProfile 모델 인스턴스
        """
        self.profile = profile

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 개인정보 반환 - 법인과 동일한 필드 구조"""
        return {
            'id': self.profile.id,
            'name': self.profile.name,
            'english_name': self.profile.english_name,
            'chinese_name': self.profile.chinese_name,
            'resident_number': self.profile.resident_number,
            'birth_date': self.profile.birth_date,
            'lunar_birth': self.profile.lunar_birth,
            'gender': self.profile.gender,
            'mobile_phone': self.profile.mobile_phone,
            'phone': self.profile.mobile_phone,  # 템플릿 호환 필드
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
            'marital_status': self.profile.marital_status,
            # 실제 거주 주소
            'actual_postal_code': self.profile.actual_postal_code,
            'actual_address': self.profile.actual_address,
            'actual_detailed_address': self.profile.actual_detailed_address,
            # 비상연락처
            'emergency_contact': self.profile.emergency_contact,
            'emergency_relation': self.profile.emergency_relation,
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

    def get_award_list(self) -> List[Dict[str, Any]]:
        """수상 내역 목록 반환 (PersonalAward 사용)"""
        return [award.to_dict() for award in self.profile.awards.all()]

    def get_family_list(self) -> List[Dict[str, Any]]:
        """가족 정보 목록 반환 (PersonalFamily 사용)"""
        if hasattr(self.profile, 'families'):
            return [member.to_dict() for member in self.profile.families.all()]
        return []

    def get_project_participation_list(self) -> List[Dict[str, Any]]:
        """프로젝트 참여이력 목록 반환 (PersonalProjectParticipation 사용)"""
        if hasattr(self.profile, 'project_participations'):
            return [proj.to_dict() for proj in self.profile.project_participations.all()]
        return []

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

    def get_account_type(self) -> str:
        """계정 타입 반환"""
        return 'personal'


class CorporateAdminProfileAdapter(ProfileAdapter):
    """법인 관리자용 어댑터 (CorporateAdminProfile 모델 래핑)

    법인 관리자(account_type='corporate', employee_id=None)를 위한 경량 프로필 시스템.
    직원 정보 없이 회사 관리 기능에 필요한 최소한의 프로필 정보만 제공.
    """

    AVAILABLE_SECTIONS = [
        'basic', 'company_info'
    ]

    def __init__(self, admin_profile):
        """
        Args:
            admin_profile: CorporateAdminProfile 모델 인스턴스
        """
        self.admin_profile = admin_profile

    def get_basic_info(self) -> Dict[str, Any]:
        """기본 정보 반환"""
        return {
            'id': self.admin_profile.id,
            'name': self.admin_profile.name,
            'english_name': self.admin_profile.english_name,
            'chinese_name': None,
            'birth_date': None,
            'lunar_birth': None,
            'gender': None,
            'mobile_phone': self.admin_profile.mobile_phone,
            'home_phone': None,
            'email': self.admin_profile.email,
            'address': None,
            'detailed_address': None,
            'postal_code': None,
            'photo': self.admin_profile.photo,
            'employee_number': None,
            'nationality': None,
            'blood_type': None,
            'religion': None,
            'hobby': None,
            'specialty': None,
            'disability_info': None,
            'position': self.admin_profile.position,
            'department': self.admin_profile.department,
            'office_phone': self.admin_profile.office_phone,
            'bio': self.admin_profile.bio,
        }

    def get_organization_info(self) -> Optional[Dict[str, Any]]:
        """소속 정보 반환 (회사 정보)"""
        if self.admin_profile.company:
            return {
                'company': self.admin_profile.company.to_dict() if hasattr(self.admin_profile.company, 'to_dict') else None,
                'company_id': self.admin_profile.company_id,
                'department': self.admin_profile.department,
                'position': self.admin_profile.position,
            }
        return None

    def get_contract_info(self) -> Optional[Dict[str, Any]]:
        """계약 정보 반환 (관리자는 None)"""
        return None

    def get_salary_info(self) -> Optional[Dict[str, Any]]:
        """급여 정보 반환 (관리자는 None)"""
        return None

    def get_benefit_info(self) -> Optional[Dict[str, Any]]:
        """복리후생 정보 반환 (관리자는 None)"""
        return None

    def get_insurance_info(self) -> Optional[Dict[str, Any]]:
        """4대보험 정보 반환 (관리자는 None)"""
        return None

    def get_education_list(self) -> List[Dict[str, Any]]:
        """학력 정보 목록 반환 (관리자는 빈 목록)"""
        return []

    def get_career_list(self) -> List[Dict[str, Any]]:
        """경력 정보 목록 반환 (관리자는 빈 목록)"""
        return []

    def get_certificate_list(self) -> List[Dict[str, Any]]:
        """자격증 목록 반환 (관리자는 빈 목록)"""
        return []

    def get_language_list(self) -> List[Dict[str, Any]]:
        """언어능력 목록 반환 (관리자는 빈 목록)"""
        return []

    def get_military_info(self) -> Optional[Dict[str, Any]]:
        """병역 정보 반환 (관리자는 None)"""
        return None

    def is_corporate(self) -> bool:
        """법인 소속 여부 (항상 True)"""
        return True

    def is_admin(self) -> bool:
        """관리자 여부 (항상 True)"""
        return True

    def get_available_sections(self) -> List[str]:
        """사용 가능한 섹션 목록"""
        return self.AVAILABLE_SECTIONS.copy()

    def get_profile_id(self) -> int:
        """프로필 ID (admin_profile.id)"""
        return self.admin_profile.id

    def get_display_name(self) -> str:
        """표시용 이름 (이름 + 직책)"""
        parts = [self.admin_profile.name]
        if self.admin_profile.position:
            parts.append(self.admin_profile.position)
        return ' '.join(parts)

    def get_photo_url(self) -> Optional[str]:
        """프로필 사진 URL"""
        return self.admin_profile.photo

    def get_user_id(self) -> int:
        """연결된 User ID"""
        return self.admin_profile.user_id

    def get_company_id(self) -> int:
        """연결된 Company ID"""
        return self.admin_profile.company_id

    def get_account_type(self) -> str:
        """계정 타입 반환"""
        return 'corporate_admin'


# =============================================================================
# Factory Functions
# =============================================================================

def create_profile_adapter(
    model_instance,
    model_type: Optional[str] = None
) -> ProfileAdapter:
    """
    모델 인스턴스에 맞는 어댑터 생성

    Args:
        model_instance: Employee, PersonalProfile, 또는 CorporateAdminProfile 인스턴스
        model_type: 모델 타입 힌트 ('employee', 'personal', 'corporate_admin')
                   None이면 자동 감지

    Returns:
        적절한 ProfileAdapter 서브클래스 인스턴스

    Raises:
        ValueError: 지원하지 않는 모델 타입
    """
    # 모델 타입 자동 감지
    if model_type is None:
        class_name = model_instance.__class__.__name__
        if class_name == 'Employee':
            model_type = 'employee'
        elif class_name == 'PersonalProfile':
            model_type = 'personal'
        elif class_name == 'CorporateAdminProfile':
            model_type = 'corporate_admin'
        else:
            raise ValueError(f"지원하지 않는 모델 타입: {class_name}")

    # 어댑터 생성
    if model_type == 'employee':
        return EmployeeProfileAdapter(model_instance)
    elif model_type == 'personal':
        return PersonalProfileAdapter(model_instance)
    elif model_type == 'corporate_admin':
        return CorporateAdminProfileAdapter(model_instance)
    else:
        raise ValueError(f"지원하지 않는 모델 타입: {model_type}")
