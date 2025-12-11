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


# 싱글톤 인스턴스
personal_service = PersonalService()
