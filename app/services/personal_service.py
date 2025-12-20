"""
Personal Service

개인 계정 관련 비즈니스 로직을 처리합니다.
- 회원가입
- 프로필 관리
- 이력 데이터 CRUD

Phase 4.1: PersonalProfile → Profile 마이그레이션 완료
- ProfileRepository 사용
- 통합 이력 테이블 직접 접근
"""
from typing import Dict, Optional, Tuple, List
from app.database import db
from app.models.user import User
from app.models.profile import Profile
from app.models import (
    Education, Career, Certificate, Language, MilitaryService
)
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository


class PersonalService:
    """개인 계정 서비스 (통합 Profile 모델 사용)"""

    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()

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
        """개인 회원가입 처리 (통합 Profile 모델 사용)

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

            # 통합 Profile 생성
            profile = Profile(
                user_id=user.id,
                name=name,
                email=email,
                mobile_phone=mobile_phone
            )
            db.session.add(profile)
            db.session.commit()

            return True, user, None

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    # ========================================
    # 프로필 조회/수정
    # ========================================

    def get_user_with_profile(self, user_id: int) -> Tuple[Optional[User], Optional[Profile]]:
        """사용자와 프로필 동시 조회"""
        user = User.query.get(user_id)
        if not user:
            return None, None

        profile = self.profile_repo.get_by_user_id(user_id)
        return user, profile

    def get_dashboard_data(self, user_id: int) -> Optional[Dict]:
        """대시보드용 데이터 조회

        프로필이 없어도 user 정보는 반환합니다.
        호출측에서 profile이 None인지 확인하여 프로필 생성 페이지로 안내해야 합니다.
        """
        user, profile = self.get_user_with_profile(user_id)
        if not user:
            return None

        # 통합 Profile 모델에서 이력 통계 조회
        stats = {}
        if profile:
            stats = {
                'education_count': profile.educations.count() if profile.educations else 0,
                'career_count': profile.careers.count() if profile.careers else 0,
                'certificate_count': profile.certificates.count() if profile.certificates else 0,
                'language_count': profile.languages.count() if profile.languages else 0,
                'has_military': profile.military_services.count() > 0 if profile.military_services else False
            }

        return {
            'user': user,
            'profile': profile,  # None일 수 있음
            'stats': stats
        }

    def ensure_profile_exists(self, user_id: int, default_name: str) -> Profile:
        """프로필이 없으면 생성, 있으면 반환"""
        return self.profile_repo.get_or_create_for_user(user_id, default_name)

    def update_profile(self, user_id: int, data: Dict) -> Tuple[bool, Optional[str]]:
        """프로필 정보 수정"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False, '프로필을 찾을 수 없습니다.'

        try:
            self.profile_repo.update_by_user_id(user_id, data)
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # 학력 (Education) CRUD
    # ========================================

    def get_educations(self, profile_id: int) -> List[Dict]:
        """학력 목록 조회"""
        profile = Profile.query.get(profile_id)
        if not profile:
            return []
        return [e.to_dict() for e in profile.educations.all()]

    def add_education(self, profile_id: int, data: Dict) -> Dict:
        """학력 추가"""
        education = Education(
            profile_id=profile_id,
            school_name=data.get('school_name'),
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

    def delete_education(self, education_id: int, profile_id: int) -> bool:
        """학력 삭제 (소유권 확인)"""
        education = Education.query.filter_by(
            id=education_id, profile_id=profile_id
        ).first()
        if not education:
            return False
        db.session.delete(education)
        db.session.commit()
        return True

    def delete_all_educations(self, profile_id: int) -> int:
        """프로필의 모든 학력 삭제"""
        count = Education.query.filter_by(profile_id=profile_id).delete()
        db.session.commit()
        return count

    # ========================================
    # 경력 (Career) CRUD
    # ========================================

    def get_careers(self, profile_id: int) -> List[Dict]:
        """경력 목록 조회"""
        profile = Profile.query.get(profile_id)
        if not profile:
            return []
        return [c.to_dict() for c in profile.careers.all()]

    def add_career(self, profile_id: int, data: Dict) -> Dict:
        """경력 추가"""
        career = Career(
            profile_id=profile_id,
            company_name=data.get('company_name'),
            department=data.get('department'),
            position=data.get('position'),
            job_grade=data.get('job_grade'),
            job_title=data.get('job_title'),
            job_role=data.get('job_role'),
            responsibilities=data.get('responsibilities'),
            salary_type=data.get('salary_type'),
            salary=data.get('salary'),
            monthly_salary=data.get('monthly_salary'),
            pay_step=data.get('pay_step'),
            start_date=data.get('start_date'),
            end_date=data.get('end_date')
        )
        db.session.add(career)
        db.session.commit()
        return career.to_dict()

    def delete_career(self, career_id: int, profile_id: int) -> bool:
        """경력 삭제 (소유권 확인)"""
        career = Career.query.filter_by(
            id=career_id, profile_id=profile_id
        ).first()
        if not career:
            return False
        db.session.delete(career)
        db.session.commit()
        return True

    def delete_all_careers(self, profile_id: int) -> int:
        """프로필의 모든 경력 삭제"""
        count = Career.query.filter_by(profile_id=profile_id).delete()
        db.session.commit()
        return count

    # ========================================
    # 자격증 (Certificate) CRUD
    # ========================================

    def get_certificates(self, profile_id: int) -> List[Dict]:
        """자격증 목록 조회"""
        profile = Profile.query.get(profile_id)
        if not profile:
            return []
        return [c.to_dict() for c in profile.certificates.all()]

    def add_certificate(self, profile_id: int, data: Dict) -> Dict:
        """자격증 추가"""
        certificate = Certificate(
            profile_id=profile_id,
            certificate_name=data.get('name') or data.get('certificate_name'),
            issuing_organization=data.get('issuing_organization'),
            acquisition_date=data.get('issue_date') or data.get('acquisition_date'),
            expiry_date=data.get('expiry_date'),
            certificate_number=data.get('certificate_number'),
            grade=data.get('grade')
        )
        db.session.add(certificate)
        db.session.commit()
        return certificate.to_dict()

    def delete_certificate(self, certificate_id: int, profile_id: int) -> bool:
        """자격증 삭제 (소유권 확인)"""
        certificate = Certificate.query.filter_by(
            id=certificate_id, profile_id=profile_id
        ).first()
        if not certificate:
            return False
        db.session.delete(certificate)
        db.session.commit()
        return True

    def delete_all_certificates(self, profile_id: int) -> int:
        """프로필의 모든 자격증 삭제"""
        count = Certificate.query.filter_by(profile_id=profile_id).delete()
        db.session.commit()
        return count

    # ========================================
    # 어학 (Language) CRUD
    # ========================================

    def get_languages(self, profile_id: int) -> List[Dict]:
        """어학 목록 조회"""
        profile = Profile.query.get(profile_id)
        if not profile:
            return []
        return [lang.to_dict() for lang in profile.languages.all()]

    def add_language(self, profile_id: int, data: Dict) -> Dict:
        """어학 추가"""
        language = Language(
            profile_id=profile_id,
            language_name=data.get('language') or data.get('language_name'),
            level=data.get('proficiency') or data.get('level'),
            test_name=data.get('test_name'),
            score=data.get('score'),
            test_date=data.get('test_date')
        )
        db.session.add(language)
        db.session.commit()
        return language.to_dict()

    def delete_language(self, language_id: int, profile_id: int) -> bool:
        """어학 삭제 (소유권 확인)"""
        language = Language.query.filter_by(
            id=language_id, profile_id=profile_id
        ).first()
        if not language:
            return False
        db.session.delete(language)
        db.session.commit()
        return True

    def delete_all_languages(self, profile_id: int) -> int:
        """프로필의 모든 어학 삭제"""
        count = Language.query.filter_by(profile_id=profile_id).delete()
        db.session.commit()
        return count

    # ========================================
    # 병역 (MilitaryService) CRUD - 1:1 관계
    # ========================================

    def get_military(self, profile_id: int) -> Optional[Dict]:
        """병역 정보 조회"""
        profile = Profile.query.get(profile_id)
        if not profile:
            return None
        military = profile.military_services.first()
        return military.to_dict() if military else None

    def save_military(self, profile_id: int, data: Dict) -> Dict:
        """병역 정보 저장/수정 (1:1)"""
        # 기존 데이터 조회
        military = MilitaryService.query.filter_by(profile_id=profile_id).first()

        if military:
            # 수정
            military.military_status = data.get('service_type') or data.get('military_status')
            military.branch = data.get('branch')
            military.rank = data.get('rank')
            military.start_date = data.get('start_date')
            military.end_date = data.get('end_date')
            military.service_type = data.get('specialty') or data.get('service_type')
            military.duty = data.get('duty')
            military.exemption_reason = data.get('notes') or data.get('exemption_reason')
        else:
            # 신규 생성
            military = MilitaryService(
                profile_id=profile_id,
                military_status=data.get('service_type') or data.get('military_status'),
                branch=data.get('branch'),
                rank=data.get('rank'),
                start_date=data.get('start_date'),
                end_date=data.get('end_date'),
                service_type=data.get('specialty') or data.get('service_type'),
                duty=data.get('duty'),
                exemption_reason=data.get('notes') or data.get('exemption_reason')
            )
            db.session.add(military)

        db.session.commit()
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

        # 통합 Profile 모델 조회
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
                'english_name': profile.english_name,
                'chinese_name': profile.chinese_name,
                'photo': profile.photo or '/static/images/face/face_01_m.png',
                'email': profile.email,
                'phone': profile.mobile_phone,
                'home_phone': profile.home_phone,
                'address': profile.address,
                'detailed_address': profile.detailed_address,
                'postal_code': profile.postal_code,
                'actual_address': profile.actual_address,
                'actual_detailed_address': profile.actual_detailed_address,
                'birth_date': profile.birth_date,
                'lunar_birth': profile.lunar_birth,
                'gender': profile.gender,
                'marital_status': profile.marital_status,
                'resident_number': profile.resident_number,
                'nationality': profile.nationality,
                'emergency_contact': profile.emergency_contact,
                'emergency_relation': profile.emergency_relation,
                'blood_type': profile.blood_type,
                'religion': profile.religion,
                'hobby': profile.hobby,
                'specialty': profile.specialty,
                'disability_info': profile.disability_info,
                # 소속정보 (계약 기반)
                'department': contract.department,
                'team': contract.department,
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

        # 이력 정보 조회 (통합 Profile 모델 사용)
        education_list = []
        career_list = []
        certificate_list = []
        language_list = []
        military = None
        award_list = []
        family_list = []

        if profile:
            education_list = [e.to_dict() for e in profile.educations.all()]
            career_list = [c.to_dict() for c in profile.careers.all()]
            certificate_list = [c.to_dict() for c in profile.certificates.all()]
            language_list = [lang.to_dict() for lang in profile.languages.all()]
            military_records = profile.military_services.first()
            military = military_records.to_dict() if military_records else None
            award_list = [a.to_dict() for a in profile.awards.all()]
            family_list = [f.to_dict() for f in profile.family_members.all()]

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
