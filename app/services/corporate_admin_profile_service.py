"""
Corporate Admin Profile Service

법인 관리자 프로필 관련 비즈니스 로직을 처리합니다.
- 프로필 생성/수정/조회
- 어댑터 통합
"""
from typing import Dict, Optional, Tuple
from app.database import db
from app.utils.transaction import atomic_transaction
from app.models.user import User
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.repositories.corporate_admin_profile_repository import CorporateAdminProfileRepository
from app.repositories.user_repository import UserRepository
from app.adapters.profile_adapter import CorporateAdminProfileAdapter


class CorporateAdminProfileService:
    """법인 관리자 프로필 서비스"""

    def __init__(self):
        self.profile_repo = CorporateAdminProfileRepository()
        self.user_repo = UserRepository()

    # ========================================
    # 프로필 조회
    # ========================================

    def get_profile_by_user_id(self, user_id: int) -> Optional[CorporateAdminProfile]:
        """사용자 ID로 프로필 조회"""
        return self.profile_repo.get_by_user_id(user_id)

    def get_user_with_profile(self, user_id: int) -> Tuple[Optional[User], Optional[CorporateAdminProfile]]:
        """사용자와 프로필 동시 조회"""
        user = User.query.get(user_id)
        if not user:
            return None, None

        profile = self.profile_repo.get_by_user_id(user_id)
        return user, profile

    def get_adapter(self, user_id: int) -> Optional[CorporateAdminProfileAdapter]:
        """사용자 ID로 프로필 어댑터 반환"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return None
        return CorporateAdminProfileAdapter(profile)

    def get_dashboard_data(self, user_id: int) -> Optional[Dict]:
        """대시보드용 데이터 조회"""
        user, profile = self.get_user_with_profile(user_id)
        if not user or not profile:
            return None

        return {
            'user': user,
            'profile': profile,
            'company': profile.company,
            'adapter': CorporateAdminProfileAdapter(profile)
        }

    # ========================================
    # 프로필 생성/수정
    # ========================================

    def ensure_profile_exists(self, user_id: int, company_id: int, default_name: str) -> CorporateAdminProfile:
        """프로필이 없으면 생성, 있으면 반환"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            profile = self.profile_repo.create_profile(
                user_id=user_id,
                company_id=company_id,
                name=default_name
            )
        return profile

    def create_profile(self, user_id: int, company_id: int, data: Dict) -> Tuple[bool, Optional[CorporateAdminProfile], Optional[str]]:
        """새 프로필 생성

        Returns:
            Tuple[성공여부, Profile객체, 에러메시지]
        """
        # 이미 프로필이 있는지 확인
        if self.profile_repo.exists_for_user(user_id):
            return False, None, '이미 프로필이 존재합니다.'

        try:
            with atomic_transaction():
                profile = self.profile_repo.create_profile(
                    user_id=user_id,
                    company_id=company_id,
                    name=data.get('name', ''),
                    english_name=data.get('english_name'),
                    position=data.get('position'),
                    mobile_phone=data.get('mobile_phone'),
                    office_phone=data.get('office_phone'),
                    email=data.get('email'),
                    photo=data.get('photo'),
                    department=data.get('department'),
                    bio=data.get('bio'),
                    commit=False
                )
            return True, profile, None
        except Exception as e:
            return False, None, str(e)

    def update_profile(self, user_id: int, data: Dict) -> Tuple[bool, Optional[str]]:
        """프로필 정보 수정"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False, '프로필을 찾을 수 없습니다.'

        try:
            with atomic_transaction():
                self.profile_repo.update_profile(profile, data, commit=False)
            return True, None
        except Exception as e:
            return False, str(e)

    # ========================================
    # 프로필 상태 관리
    # ========================================

    def deactivate_profile(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """프로필 비활성화"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False, '프로필을 찾을 수 없습니다.'

        try:
            with atomic_transaction():
                self.profile_repo.deactivate(profile, commit=False)
            return True, None
        except Exception as e:
            return False, str(e)

    def activate_profile(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """프로필 활성화"""
        profile = self.profile_repo.get_by_user_id(user_id)
        if not profile:
            return False, '프로필을 찾을 수 없습니다.'

        try:
            with atomic_transaction():
                self.profile_repo.activate(profile, commit=False)
            return True, None
        except Exception as e:
            return False, str(e)

    # ========================================
    # 유틸리티
    # ========================================

    def is_corporate_admin(self, user: User) -> bool:
        """법인 관리자 여부 확인"""
        return (
            user.account_type == User.ACCOUNT_CORPORATE and
            user.employee_id is None
        )

    def has_profile(self, user_id: int) -> bool:
        """프로필 존재 여부 확인"""
        return self.profile_repo.exists_for_user(user_id)


# 싱글톤 인스턴스
corporate_admin_profile_service = CorporateAdminProfileService()
