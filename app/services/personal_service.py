"""
Personal Service

개인 계정 관련 비즈니스 로직을 처리합니다.
- 회원가입
- 프로필 관리
- 이력 데이터 CRUD

Phase 4.1: PersonalProfile → Profile 마이그레이션 완료
- ProfileRepository 사용
- 통합 이력 테이블 직접 접근

Phase 30: 전화번호 중복 체크 및 형식 검증 추가
Phase 30: 레이어 분리 - Model.query 제거, Repository 패턴 적용
"""
import re
from typing import Dict, Optional, List, Tuple
from datetime import datetime, timedelta
from app.models.user import User
from app.models.profile import Profile
from app.utils.transaction import atomic_transaction
from app.repositories.user_repository import UserRepository
from app.repositories.profile_repository import ProfileRepository
from app.services.profile_relation_service import profile_relation_service
from app.services.base import ServiceResult
from app.constants.status import ContractStatus


class PersonalService:
    """개인 계정 서비스 (통합 Profile 모델 사용)

    Phase 30: 레이어 분리 - Repository DI 패턴 적용
    """

    def __init__(self):
        self.user_repo = UserRepository()
        self.profile_repo = ProfileRepository()
        self._contract_repo = None
        self._company_repo = None
        self._employee_repo = None

    # ========================================
    # Repository Properties (지연 초기화)
    # ========================================

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        if self._contract_repo is None:
            from app.repositories.contract.person_contract_repository import person_contract_repository
            self._contract_repo = person_contract_repository
        return self._contract_repo

    @property
    def company_repo(self):
        """지연 초기화된 법인 Repository"""
        if self._company_repo is None:
            from app.repositories.company_repository import company_repository
            self._company_repo = company_repository
        return self._company_repo

    @property
    def employee_repo(self):
        """지연 초기화된 직원 Repository"""
        if self._employee_repo is None:
            from app.repositories.employee_repository import employee_repository
            self._employee_repo = employee_repository
        return self._employee_repo

    # ========================================
    # 회원가입
    # ========================================

    # 전화번호 형식 정규식 (010-XXXX-XXXX 또는 01X-XXX-XXXX)
    PHONE_PATTERN = re.compile(r'^01[0-9]-\d{3,4}-\d{4}$')

    def validate_registration(self, username: str, email: str,
                              password: str, password_confirm: str,
                              name: str, mobile_phone: str = None) -> List[str]:
        """회원가입 유효성 검사

        Args:
            username: 아이디
            email: 이메일
            password: 비밀번호
            password_confirm: 비밀번호 확인
            name: 이름
            mobile_phone: 휴대폰 번호 (선택)

        Returns:
            에러 메시지 리스트
        """
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

        # 전화번호 검증 (입력된 경우에만)
        if mobile_phone:
            # 형식 검증
            if not self.PHONE_PATTERN.match(mobile_phone):
                errors.append('전화번호 형식이 올바르지 않습니다. (예: 010-1234-5678)')
            # 중복 확인
            elif self.profile_repo.mobile_phone_exists(mobile_phone):
                errors.append('이미 등록된 전화번호입니다.')

        return errors

    def register(self, username: str, email: str, password: str,
                 name: str, mobile_phone: str = None) -> ServiceResult[User]:
        """개인 회원가입 처리 (통합 Profile 모델 사용)

        Phase 30: Repository 패턴 적용

        Returns:
            ServiceResult[User]
        """
        try:
            with atomic_transaction():
                # 사용자 계정 생성 (Repository 사용)
                user = self.user_repo.create_personal_user(
                    username=username,
                    email=email,
                    password=password,
                    commit=False
                )

                # 통합 Profile 생성 (Repository 사용)
                self.profile_repo.create_for_user(
                    user_id=user.id,
                    name=name,
                    email=email,
                    mobile_phone=mobile_phone,
                    commit=False
                )

            return ServiceResult.ok(data=user)

        except Exception as e:
            return ServiceResult.fail(str(e))

    # ========================================
    # 프로필 조회/수정
    # ========================================

    def get_user_with_profile(self, user_id: int) -> Tuple[Optional[User], Optional[Profile]]:
        """사용자와 프로필 동시 조회

        Phase 30: Repository 패턴 적용
        """
        user = self.user_repo.find_by_id(user_id)
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

    def update_profile(self, user_id: int, data: Dict) -> ServiceResult[Dict]:
        """프로필 정보 수정"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return ServiceResult.not_found('프로필')

        try:
            with atomic_transaction():
                self.profile_repo.update_by_user_id(user_id, data, commit=False)
            return ServiceResult.ok(data=profile.to_dict())
        except Exception as e:
            return ServiceResult.fail(str(e))

    # ========================================
    # 학력 (Education) CRUD - profile_relation_service 위임
    # ========================================

    def get_educations(self, profile_id: int) -> List[Dict]:
        """학력 목록 조회"""
        return profile_relation_service.get_educations(profile_id, 'profile')

    def add_education(self, profile_id: int, data: Dict) -> Dict:
        """학력 추가"""
        return profile_relation_service.add_education(profile_id, data, 'profile')

    def delete_education(self, education_id: int, profile_id: int) -> bool:
        """학력 삭제 (소유권 확인)"""
        return profile_relation_service.delete_education(education_id, profile_id, 'profile')

    def delete_all_educations(self, profile_id: int) -> int:
        """프로필의 모든 학력 삭제"""
        return profile_relation_service.delete_all_educations(profile_id, 'profile')

    # ========================================
    # 경력 (Career) CRUD - profile_relation_service 위임
    # ========================================

    def get_careers(self, profile_id: int) -> List[Dict]:
        """경력 목록 조회"""
        return profile_relation_service.get_careers(profile_id, 'profile')

    def add_career(self, profile_id: int, data: Dict) -> Dict:
        """경력 추가"""
        return profile_relation_service.add_career(profile_id, data, 'profile')

    def delete_career(self, career_id: int, profile_id: int) -> bool:
        """경력 삭제 (소유권 확인)"""
        return profile_relation_service.delete_career(career_id, profile_id, 'profile')

    def delete_all_careers(self, profile_id: int) -> int:
        """프로필의 모든 경력 삭제"""
        return profile_relation_service.delete_all_careers(profile_id, 'profile')

    # ========================================
    # 자격증 (Certificate) CRUD - profile_relation_service 위임
    # ========================================

    def get_certificates(self, profile_id: int) -> List[Dict]:
        """자격증 목록 조회"""
        return profile_relation_service.get_certificates(profile_id, 'profile')

    def add_certificate(self, profile_id: int, data: Dict) -> Dict:
        """자격증 추가"""
        return profile_relation_service.add_certificate(profile_id, data, 'profile')

    def delete_certificate(self, certificate_id: int, profile_id: int) -> bool:
        """자격증 삭제 (소유권 확인)"""
        return profile_relation_service.delete_certificate(certificate_id, profile_id, 'profile')

    def delete_all_certificates(self, profile_id: int) -> int:
        """프로필의 모든 자격증 삭제"""
        return profile_relation_service.delete_all_certificates(profile_id, 'profile')

    # ========================================
    # 어학 (Language) CRUD - profile_relation_service 위임
    # ========================================

    def get_languages(self, profile_id: int) -> List[Dict]:
        """어학 목록 조회"""
        return profile_relation_service.get_languages(profile_id, 'profile')

    def add_language(self, profile_id: int, data: Dict) -> Dict:
        """어학 추가"""
        return profile_relation_service.add_language(profile_id, data, 'profile')

    def delete_language(self, language_id: int, profile_id: int) -> bool:
        """어학 삭제 (소유권 확인)"""
        return profile_relation_service.delete_language(language_id, profile_id, 'profile')

    def delete_all_languages(self, profile_id: int) -> int:
        """프로필의 모든 어학 삭제"""
        return profile_relation_service.delete_all_languages(profile_id, 'profile')

    # ========================================
    # 병역 (MilitaryService) CRUD - 1:1 관계
    # Phase 9: ProfileRelationService 위임
    # ========================================

    def get_military(self, profile_id: int) -> Optional[Dict]:
        """병역 정보 조회"""
        return profile_relation_service.get_military(profile_id, 'profile')

    def get_military_list(self, profile_id: int) -> List[Dict]:
        """병역 목록 조회 (1:N 지원)"""
        return profile_relation_service.get_military_list(profile_id, 'profile')

    def save_military(self, profile_id: int, data: Dict) -> Dict:
        """병역 정보 저장/수정 (1:1)"""
        return profile_relation_service.update_or_create_military(profile_id, data, 'profile')

    def add_military(self, profile_id: int, data: Dict) -> Dict:
        """병역 추가"""
        return profile_relation_service.add_military(profile_id, data, 'profile')

    def delete_military(self, military_id: int, profile_id: int) -> bool:
        """병역 삭제 (소유권 확인)"""
        return profile_relation_service.delete_military(military_id, profile_id, 'profile')

    def delete_all_military(self, profile_id: int) -> int:
        """프로필의 모든 병역 정보 삭제"""
        return profile_relation_service.delete_all_military(profile_id, 'profile')

    # ========================================
    # 회사 인사카드 (Phase 2)
    # ========================================

    def get_viewable_contracts(self, user_id: int, include_terminated: bool = True) -> List[Dict]:
        """열람 가능한 계약 목록 조회

        승인된 계약과 종료된 계약(3년 보관 기간 내)을 모두 반환합니다.

        Phase 30: Repository 패턴 적용

        Args:
            user_id: 사용자 ID
            include_terminated: 종료된 계약 포함 여부 (기본 True)

        Returns:
            계약 목록 (활성/종료 구분 포함)
        """
        # Repository를 통해 계약 조회
        contracts = self.contract_repo.find_viewable_by_person_user_id(
            user_id, include_terminated
        )

        result = []
        retention_days = 365 * 3  # 3년 보관

        for contract in contracts:
            company = self.company_repo.find_by_id(contract.company_id)
            if not company:
                continue

            # 종료된 계약의 보관 기간 확인
            is_within_retention = True
            if contract.status == ContractStatus.TERMINATED and contract.terminated_at:
                retention_end = contract.terminated_at + timedelta(days=retention_days)
                is_within_retention = datetime.utcnow() < retention_end

            if not is_within_retention:
                continue

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
                # 종료 상태 정보
                'status': contract.status,
                'is_active': contract.status == ContractStatus.APPROVED,
                'terminated_at': contract.terminated_at,
                'termination_reason': contract.termination_reason,
            })

        # 활성 계약 우선, 그 다음 종료일 역순 정렬
        result.sort(key=lambda x: (
            0 if x['is_active'] else 1,
            x.get('terminated_at') or datetime.min
        ), reverse=False)

        return result

    def get_approved_contracts(self, user_id: int) -> List[Dict]:
        """승인된 계약 목록 조회 (하위 호환용)

        활성 계약만 반환합니다. 종료된 계약도 필요하면 get_viewable_contracts() 사용.
        """
        contracts = self.get_viewable_contracts(user_id, include_terminated=False)
        return [c for c in contracts if c['is_active']]

    def get_company_card_data(self, user_id: int, contract_id: int) -> Optional[Dict]:
        """회사 인사카드 데이터 조회

        특정 계약에 대한 회사 인사카드 정보를 반환합니다.
        법인의 Employee 데이터를 조회하여 법인과 동일한 정보를 제공합니다.
        종료된 계약도 3년 보관 기간 내에는 열람 가능합니다.

        Phase 30: Repository 패턴 적용
        """
        # 계약 정보 조회 및 권한 확인 (approved + terminated)
        contract = self.contract_repo.find_viewable_by_id_and_person_user(
            contract_id, user_id
        )

        if not contract:
            return None

        # 종료된 계약의 보관 기간 확인 (3년)
        is_terminated = contract.status == ContractStatus.TERMINATED
        if is_terminated and contract.terminated_at:
            retention_end = contract.terminated_at + timedelta(days=365 * 3)
            if datetime.utcnow() >= retention_end:
                return None  # 보관 기간 만료

        # 회사 정보 조회 (Repository 사용)
        company = self.company_repo.find_by_id(contract.company_id)
        if not company:
            return None

        # Employee 조회 (법인 DB, Repository 사용)
        employee = None
        if contract.employee_number:
            employee = self.employee_repo.find_by_employee_number(
                contract.employee_number
            )

        # Employee가 없으면 User.employee_id로 시도
        if not employee:
            user = self.user_repo.find_by_id(user_id)
            if user and user.employee_id:
                employee = self.employee_repo.find_by_id(user.employee_id)

        # Employee 데이터 구성 (법인 DB 기반)
        employee_data = None
        if employee:
            employee_data = {
                'id': employee.id,
                'name': employee.name,
                'english_name': employee.english_name,
                'chinese_name': employee.chinese_name,
                'photo': employee.photo or '/static/images/face/face_01_m.png',
                'email': employee.email,
                'phone': employee.mobile_phone or employee.phone,
                'home_phone': employee.home_phone,
                'address': employee.address,
                'detailed_address': employee.detailed_address,
                'postal_code': employee.postal_code,
                'actual_address': employee.actual_address,
                'actual_detailed_address': employee.actual_detailed_address,
                'birth_date': employee.birth_date,
                'lunar_birth': employee.lunar_birth,
                'gender': employee.gender,
                'marital_status': employee.marital_status,
                'resident_number': employee.resident_number,
                'nationality': employee.nationality,
                'emergency_contact': employee.emergency_contact,
                'emergency_relation': employee.emergency_relation,
                'blood_type': employee.blood_type,
                'religion': employee.religion,
                'hobby': employee.hobby,
                'specialty': employee.specialty,
                'disability_info': employee.disability_info,
                # 소속정보 (Employee 기반)
                'department': employee.department or contract.department,
                'team': employee.team or contract.department,
                'position': employee.position or contract.position,
                'job_title': employee.job_title,
                'job_grade': employee.job_grade,
                'job_role': employee.job_role,
                'employee_number': employee.employee_number,
                'employment_type': employee.employment_type,
                'work_location': employee.work_location,
                'internal_phone': employee.internal_phone,
                'company_email': employee.company_email,
                'hire_date': employee.hire_date,
                'status': employee.status,
                'probation_end': employee.probation_end,
                'resignation_date': employee.resignation_date,
            }

        # 이력 정보 조회 (Employee 기반 - 법인 DB)
        education_list = []
        career_list = []
        certificate_list = []
        language_list = []
        military = None
        award_list = []
        family_list = []
        salary_history_list = []
        salary_payment_list = []
        promotion_list = []
        evaluation_list = []
        training_list = []
        attendance_summary = None
        asset_list = []

        if employee:
            education_list = [e.to_dict() for e in employee.educations.all()]
            career_list = [c.to_dict() for c in employee.careers.all()]
            certificate_list = [c.to_dict() for c in employee.certificates.all()]
            language_list = [lang.to_dict() for lang in employee.languages.all()]
            military = employee.military_service.to_dict() if employee.military_service else None
            award_list = [a.to_dict() for a in employee.awards.all()]
            family_list = [f.to_dict() for f in employee.family_members.all()]
            # 법인 전용 정보 (인사기록)
            salary_history_list = [s.to_dict() for s in employee.salary_histories.all()]
            salary_payment_list = [s.to_dict() for s in employee.salary_payments.all()]
            promotion_list = [p.to_dict() for p in employee.promotions.all()]
            evaluation_list = [e.to_dict() for e in employee.evaluations.all()]
            training_list = [t.to_dict() for t in employee.trainings.all()]
            asset_list = [a.to_dict() for a in employee.assets.all()]

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
            # 종료 상태 정보
            'is_terminated': is_terminated,
            'terminated_at': contract.terminated_at.isoformat() if contract.terminated_at else None,
            'termination_reason': contract.termination_reason,
            # 이력 정보 (법인 DB 기반)
            'education_list': education_list,
            'career_list': career_list,
            'certificate_list': certificate_list,
            'language_list': language_list,
            'military': military,
            'award_list': award_list,
            'family_list': family_list,
            # 인사기록 정보 (법인 DB 기반)
            'salary_history_list': salary_history_list,
            'salary_payment_list': salary_payment_list,
            'promotion_list': promotion_list,
            'evaluation_list': evaluation_list,
            'training_list': training_list,
            'attendance_summary': attendance_summary,
            'asset_list': asset_list,
        }


# 싱글톤 인스턴스
personal_service = PersonalService()
