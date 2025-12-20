"""
Personal Service

개인 계정 관련 비즈니스 로직을 처리합니다.
- 회원가입
- 프로필 관리
- 학력/경력/자격증/어학/병역 CRUD
"""
from typing import Dict, Optional, Tuple, List
from app.database import db
from app.models.user import User
from app.repositories.user_repository import UserRepository
from app.repositories.personal_profile_repository import (
    PersonalProfileRepository,
    PersonalEducationRepository,
    PersonalCareerRepository,
    PersonalCertificateRepository,
    PersonalLanguageRepository,
    PersonalMilitaryRepository
)


class PersonalService:
    """개인 계정 서비스"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = PersonalProfileRepository()
        self.education_repo = PersonalEducationRepository()
        self.career_repo = PersonalCareerRepository()
        self.certificate_repo = PersonalCertificateRepository()
        self.language_repo = PersonalLanguageRepository()
        self.military_repo = PersonalMilitaryRepository()

    # ========================================
    # 회원가입
    # ========================================

    def validate_registration(self, username: str, email: str,
                              password: str, password_confirm: str,
                              name: str) -> List[str]:
        """회원가입 유효성 검사"""
        errors = []

        if not username:
            errors.append('아이디를 입력해주세요.')
        if not email:
            errors.append('이메일을 입력해주세요.')
        if not password:
            errors.append('비밀번호를 입력해주세요.')
        if password != password_confirm:
            errors.append('비밀번호가 일치하지 않습니다.')
        if len(password) < 8:
            errors.append('비밀번호는 최소 8자 이상이어야 합니다.')
        if not name:
            errors.append('이름을 입력해주세요.')

        # 중복 확인
        if username and self.user_repo.username_exists(username):
            errors.append('이미 사용 중인 아이디입니다.')
        if email and self.user_repo.email_exists(email):
            errors.append('이미 사용 중인 이메일입니다.')

        return errors

    def register(self, username: str, email: str, password: str,
                 name: str, mobile_phone: str = None) -> Tuple[bool, Optional[User], Optional[str]]:
        """개인 회원가입 처리

        Returns:
            Tuple[성공여부, User객체, 에러메시지]
        """
        try:
            # 사용자 계정 생성
            user = User(
                username=username,
                email=email,
                role=User.ROLE_EMPLOYEE,
                account_type=User.ACCOUNT_PERSONAL,
                is_active=True
            )
            user.set_password(password)
            db.session.add(user)
            db.session.flush()

            # 개인 프로필 생성
            self.profile_repo.create_profile(
                user_id=user.id,
                name=name,
                email=email,
                mobile_phone=mobile_phone
            )

            return True, user, None

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    # ========================================
    # 프로필 조회/수정
    # ========================================

    def get_user_with_profile(self, user_id: int) -> Tuple[Optional[User], Optional[object]]:
        """사용자와 프로필 동시 조회"""
        user = self.user_repo.get_by_id(user_id)
        if not user:
            return None, None

        # get_by_id는 Dict를 반환하므로 모델 객체 직접 조회
        user_obj = User.query.get(user_id)
        profile = self.profile_repo.get_by_user_id(user_id)
        return user_obj, profile

    def get_dashboard_data(self, user_id: int) -> Optional[Dict]:
        """대시보드용 데이터 조회

        프로필이 없어도 user 정보는 반환합니다.
        호출측에서 profile이 None인지 확인하여 프로필 생성 페이지로 안내해야 합니다.
        """
        user, profile = self.get_user_with_profile(user_id)
        if not user:
            return None

        return {
            'user': user,
            'profile': profile,  # None일 수 있음
            'stats': self.profile_repo.get_profile_stats(profile) if profile else {}
        }

    def ensure_profile_exists(self, user_id: int, default_name: str) -> object:
        """프로필이 없으면 생성, 있으면 반환"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = self.profile_repo.create_profile(
                user_id=user_id,
                name=default_name
            )
        return profile

    def update_profile(self, user_id: int, data: Dict) -> Tuple[bool, Optional[str]]:
        """프로필 정보 수정"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False, '프로필을 찾을 수 없습니다.'

        try:
            self.profile_repo.update_profile(profile, data)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # 학력 CRUD
    # ========================================

    def get_educations(self, profile_id: int) -> List[Dict]:
        """학력 목록 조회"""
        return self.education_repo.get_by_profile_id(profile_id)

    def add_education(self, profile_id: int, data: Dict) -> Dict:
        """학력 추가"""
        education = self.education_repo.create(profile_id, data)
        return education.to_dict()

    def delete_education(self, education_id: int, profile_id: int) -> bool:
        """학력 삭제"""
        return self.education_repo.delete_by_id_and_profile(education_id, profile_id)

    def delete_all_educations(self, profile_id: int) -> int:
        """프로필의 모든 학력 삭제"""
        return self.education_repo.delete_all_by_profile(profile_id)

    # ========================================
    # 경력 CRUD
    # ========================================

    def get_careers(self, profile_id: int) -> List[Dict]:
        """경력 목록 조회"""
        return self.career_repo.get_by_profile_id(profile_id)

    def add_career(self, profile_id: int, data: Dict) -> Dict:
        """경력 추가"""
        career = self.career_repo.create(profile_id, data)
        return career.to_dict()

    def delete_career(self, career_id: int, profile_id: int) -> bool:
        """경력 삭제"""
        return self.career_repo.delete_by_id_and_profile(career_id, profile_id)

    def delete_all_careers(self, profile_id: int) -> int:
        """프로필의 모든 경력 삭제"""
        return self.career_repo.delete_all_by_profile(profile_id)

    # ========================================
    # 자격증 CRUD
    # ========================================

    def get_certificates(self, profile_id: int) -> List[Dict]:
        """자격증 목록 조회"""
        return self.certificate_repo.get_by_profile_id(profile_id)

    def add_certificate(self, profile_id: int, data: Dict) -> Dict:
        """자격증 추가"""
        certificate = self.certificate_repo.create(profile_id, data)
        return certificate.to_dict()

    def delete_certificate(self, certificate_id: int, profile_id: int) -> bool:
        """자격증 삭제"""
        return self.certificate_repo.delete_by_id_and_profile(certificate_id, profile_id)

    def delete_all_certificates(self, profile_id: int) -> int:
        """프로필의 모든 자격증 삭제"""
        return self.certificate_repo.delete_all_by_profile(profile_id)

    # ========================================
    # 어학 CRUD
    # ========================================

    def get_languages(self, profile_id: int) -> List[Dict]:
        """어학 목록 조회"""
        return self.language_repo.get_by_profile_id(profile_id)

    def add_language(self, profile_id: int, data: Dict) -> Dict:
        """어학 추가"""
        language = self.language_repo.create(profile_id, data)
        return language.to_dict()

    def delete_language(self, language_id: int, profile_id: int) -> bool:
        """어학 삭제"""
        return self.language_repo.delete_by_id_and_profile(language_id, profile_id)

    def delete_all_languages(self, profile_id: int) -> int:
        """프로필의 모든 어학 삭제"""
        return self.language_repo.delete_all_by_profile(profile_id)

    # ========================================
    # 병역 CRUD
    # ========================================

    def get_military(self, profile_id: int) -> Optional[Dict]:
        """병역 정보 조회"""
        military = self.military_repo.get_by_profile_id(profile_id)
        return military.to_dict() if military else None

    def save_military(self, profile_id: int, data: Dict) -> Dict:
        """병역 정보 저장/수정"""
        military = self.military_repo.save(profile_id, data)
        return military.to_dict()

    # ========================================
    # 회사 인사카드 (Phase 2)
    # ========================================

    def get_approved_contracts(self, user_id: int) -> List[Dict]:
        """승인된 계약 목록 조회

        개인 계정이 계약한 법인들의 목록을 반환합니다.
        """
        from app.models.person_contract import PersonCorporateContract
        from app.models.company import Company

        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            status='approved'
        ).all()

        result = []
        for contract in contracts:
            company = Company.query.get(contract.company_id)
            if company:
                result.append({
                    'id': contract.id,
                    'company_id': contract.company_id,
                    'company_name': company.name,
                    'company_logo': getattr(company, 'logo_url', None),
                    'position': contract.position,
                    'department': contract.department,
                    'contract_start_date': contract.contract_start_date,
                    'contract_end_date': contract.contract_end_date,
                    'approved_at': contract.approved_at,
                })

        return result

    def get_company_card_data(self, user_id: int, contract_id: int) -> Optional[Dict]:
        """회사 인사카드 데이터 조회

        특정 계약에 대한 회사 인사카드 정보를 반환합니다.
        employee 데이터, 이력 정보를 포함하여 공유 파셜 템플릿과 호환됩니다.
        """
        from app.models.person_contract import PersonCorporateContract
        from app.models.company import Company

        # 계약 정보 조회 및 권한 확인
        contract = PersonCorporateContract.query.filter_by(
            id=contract_id,
            person_user_id=user_id,
            status='approved'
        ).first()

        if not contract:
            return None

        # 회사 정보 조회
        company = Company.query.get(contract.company_id)
        if not company:
            return None

        # 개인 프로필 조회 (헤더 표시용)
        profile = self.profile_repo.get_by_user_id(user_id)
        user = User.query.get(user_id)

        # 승인된 계약 수 조회
        contract_count = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            status='approved'
        ).count()

        # employee 데이터 구성 (공유 파셜 템플릿 호환 - _basic_info.html 필드 포함)
        employee_data = None
        if profile:
            employee_data = {
                'id': user.id if user else user_id,
                # 개인 기본정보 필드
                'name': profile.name,
                'english_name': getattr(profile, 'english_name', None),
                'chinese_name': getattr(profile, 'chinese_name', None),
                'photo': profile.photo or '/static/images/face/face_01_m.png',
                'email': profile.email,
                'phone': profile.mobile_phone or getattr(profile, 'phone', None),
                'home_phone': getattr(profile, 'home_phone', None),
                'address': profile.address,
                'detailed_address': getattr(profile, 'detailed_address', None),
                'postal_code': getattr(profile, 'postal_code', None),
                'actual_address': getattr(profile, 'actual_address', None),
                'actual_detailed_address': getattr(profile, 'actual_detailed_address', None),
                'birth_date': profile.birth_date,
                'lunar_birth': getattr(profile, 'lunar_birth', False),
                'gender': getattr(profile, 'gender', None),
                'marital_status': getattr(profile, 'marital_status', None),
                'resident_number': getattr(profile, 'resident_number', None),
                'nationality': getattr(profile, 'nationality', None),
                'emergency_contact': getattr(profile, 'emergency_contact', None),
                'emergency_relation': getattr(profile, 'emergency_relation', None),
                'blood_type': getattr(profile, 'blood_type', None),
                'religion': getattr(profile, 'religion', None),
                'hobby': getattr(profile, 'hobby', None),
                'specialty': getattr(profile, 'specialty', None),
                'disability_info': getattr(profile, 'disability_info', None),
                # 소속정보 (계약 기반)
                'department': contract.department,
                'team': contract.department,  # team이 없으면 department 사용
                'position': contract.position,
                'job_title': getattr(contract, 'job_title', None),
                'employee_number': contract.employee_number or f'EMP-{user_id:03d}',
                'employment_type': getattr(contract, 'employment_type', contract.contract_type),
                'work_location': getattr(contract, 'work_location', '본사'),
                'internal_phone': getattr(contract, 'internal_phone', None),
                'company_email': getattr(contract, 'company_email', None),
                'hire_date': contract.contract_start_date,
                'status': 'active',
                # 계약 관련 추가 필드
                'contract_period': getattr(contract, 'contract_period', '무기한'),
                'probation_end': getattr(contract, 'probation_end', None),
                'resignation_date': getattr(contract, 'resignation_date', None),
                # 통계
                'contract_count': contract_count,
                'created_at': user.created_at.strftime('%Y-%m-%d') if user and user.created_at else '-',
            }

        # 이력 정보 조회 (프로필 ID 기반)
        education_list = []
        career_list = []
        certificate_list = []
        language_list = []
        military = None
        award_list = []
        family_list = []

        if profile:
            education_list = self.get_educations(profile.id)
            career_list = self.get_careers(profile.id)
            certificate_list = self.get_certificates(profile.id)
            language_list = self.get_languages(profile.id)
            military = self.get_military(profile.id)
            # award_list와 family_list는 별도 repository 필요 (현재 미구현)

        # 인사카드 데이터 구성
        return {
            'employee': employee_data,
            'contract': {
                'id': contract.id,
                'position': contract.position,
                'department': contract.department,
                'employee_number': contract.employee_number,
                'contract_type': contract.contract_type,
                'contract_start_date': contract.contract_start_date,
                'contract_end_date': contract.contract_end_date,
                'approved_at': contract.approved_at,
                # 계약정보 추가 필드
                'contract_date': contract.contract_start_date,
                'contract_period': getattr(contract, 'contract_period', '무기한'),
                'employee_type': getattr(contract, 'employee_type', None),
                'work_type': getattr(contract, 'work_type', None),
            },
            'company': {
                'id': company.id,
                'name': company.name,
                'business_number': getattr(company, 'business_number', None),
                'address': getattr(company, 'address', None),
                'phone': getattr(company, 'phone', None),
            },
            'contract_info': {
                'contract_type': contract.contract_type,
                'start_date': contract.contract_start_date,
                'end_date': contract.contract_end_date,
            },
            # 이력 정보 (공유 파셜용 - _history_info.html)
            'education_list': education_list,
            'career_list': career_list,
            'certificate_list': certificate_list,
            'language_list': language_list,
            'military': military,
            'award_list': award_list,
            'family_list': family_list,
            # 인사기록 정보 (공유 파셜용 - _hr_records.html)
            # 현재 개인 계정에서는 해당 데이터가 없으므로 빈 값으로 반환
            'salary_history_list': [],
            'salary_payment_list': [],
            'promotion_list': [],
            'evaluation_list': [],
            'training_list': [],
            'attendance_summary': None,
            'asset_list': [],
        }


# 싱글톤 인스턴스
personal_service = PersonalService()
