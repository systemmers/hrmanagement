"""
Profile Repository

통합 프로필 데이터 접근 레이어
Phase 5: Repository/Service 계층 리팩토링
"""
from typing import List, Optional, Dict, Any
from app.database import db
from app.models import Profile
from .base_repository import BaseRepository


class ProfileRepository(BaseRepository):
    """통합 프로필 Repository"""

    def __init__(self):
        super().__init__(Profile)

    def get_by_user_id(self, user_id: int) -> Optional[Profile]:
        """User ID로 프로필 조회 (개인 계정용)"""
        return Profile.query.filter_by(user_id=user_id).first()

    def get_by_user_id_dict(self, user_id: int) -> Optional[Dict]:
        """User ID로 프로필 조회 (딕셔너리 반환)"""
        profile = self.get_by_user_id(user_id)
        return profile.to_dict() if profile else None

    def get_by_id_model(self, profile_id: int) -> Optional[Profile]:
        """ID로 프로필 모델 조회"""
        return Profile.query.get(profile_id)

    def get_or_create_for_user(self, user_id: int, name: str, email: str = None) -> Profile:
        """
        User에 대한 프로필 조회 또는 생성

        Args:
            user_id: 사용자 ID
            name: 이름 (생성 시 필수)
            email: 이메일 (선택)

        Returns:
            Profile 모델 인스턴스
        """
        profile = self.get_by_user_id(user_id)
        if profile:
            return profile

        # 새 프로필 생성
        profile = Profile(
            user_id=user_id,
            name=name,
            email=email
        )
        db.session.add(profile)
        db.session.commit()
        return profile

    def create_for_employee(self, data: Dict) -> Profile:
        """
        직원용 프로필 생성 (user_id 없음)

        Args:
            data: 프로필 데이터

        Returns:
            Profile 모델 인스턴스
        """
        profile = Profile.from_dict(data)
        db.session.add(profile)
        db.session.commit()
        return profile

    def update_profile(self, profile_id: int, data: Dict) -> Optional[Profile]:
        """
        프로필 업데이트

        Args:
            profile_id: 프로필 ID
            data: 업데이트할 데이터

        Returns:
            업데이트된 Profile 모델 또는 None
        """
        profile = Profile.query.get(profile_id)
        if not profile:
            return None

        self._update_record_fields(profile, data)
        db.session.commit()
        return profile

    def update_by_user_id(self, user_id: int, data: Dict) -> Optional[Profile]:
        """
        User ID로 프로필 업데이트

        Args:
            user_id: 사용자 ID
            data: 업데이트할 데이터

        Returns:
            업데이트된 Profile 모델 또는 None
        """
        profile = self.get_by_user_id(user_id)
        if not profile:
            return None

        self._update_record_fields(profile, data)
        db.session.commit()
        return profile

    def get_public_profiles(self, limit: int = 50) -> List[Dict]:
        """공개된 프로필 목록 조회 (구직 활동용)"""
        profiles = Profile.query.filter_by(is_public=True).limit(limit).all()
        return [p.to_dict() for p in profiles]

    def search_by_name(self, name: str, limit: int = 20) -> List[Dict]:
        """이름으로 프로필 검색"""
        profiles = Profile.query.filter(
            Profile.name.ilike(f'%{name}%')
        ).limit(limit).all()
        return [p.to_dict() for p in profiles]

    def get_profiles_without_user(self) -> List[Profile]:
        """User 연결 없는 프로필 조회 (법인 생성 직원용)"""
        return Profile.query.filter_by(user_id=None).all()

    def link_to_user(self, profile_id: int, user_id: int) -> Optional[Profile]:
        """
        프로필을 User에 연결 (개인 계정 연결)

        Args:
            profile_id: 프로필 ID
            user_id: 연결할 사용자 ID

        Returns:
            업데이트된 Profile 모델 또는 None
        """
        profile = Profile.query.get(profile_id)
        if not profile:
            return None

        profile.user_id = user_id
        db.session.commit()
        return profile

    def to_snapshot_data(self, profile: Profile) -> Dict:
        """
        스냅샷용 데이터 생성 (이력 정보 포함)

        Args:
            profile: Profile 모델

        Returns:
            스냅샷 딕셔너리
        """
        return profile.to_snapshot()
