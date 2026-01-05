"""
PersonalProfile Repository

개인 프로필의 CRUD 및 조회를 처리합니다.

Phase 30: 레이어 분리 - Service의 Model.query 직접 사용 제거
"""
from typing import Optional, List, Dict, Any
from app.database import db
from app.models.personal_profile import PersonalProfile
from .base_repository import BaseRepository


class PersonalProfileRepository(BaseRepository[PersonalProfile]):
    """개인 프로필 Repository"""

    def __init__(self):
        super().__init__(PersonalProfile)

    def find_by_user_id(self, user_id: int) -> Optional[PersonalProfile]:
        """사용자 ID로 프로필 조회

        Args:
            user_id: User ID

        Returns:
            PersonalProfile 또는 None
        """
        return PersonalProfile.query.filter_by(user_id=user_id).first()

    def create_for_user(
        self,
        user_id: int,
        data: Dict[str, Any] = None,
        commit: bool = True
    ) -> PersonalProfile:
        """사용자에 대한 프로필 생성

        Args:
            user_id: User ID
            data: 프로필 데이터 (선택)
            commit: True면 즉시 커밋

        Returns:
            생성된 PersonalProfile 모델
        """
        profile_data = {'user_id': user_id}
        if data:
            profile_data.update(data)

        # name 필드가 필수이므로 없으면 기본값 설정
        if 'name' not in profile_data:
            profile_data['name'] = ''

        profile = PersonalProfile(**profile_data)
        db.session.add(profile)
        if commit:
            db.session.commit()
        return profile

    def find_or_create_for_user(
        self,
        user_id: int,
        data: Dict[str, Any] = None,
        commit: bool = True
    ) -> PersonalProfile:
        """사용자의 프로필 조회 또는 생성 (upsert)

        Args:
            user_id: User ID
            data: 프로필 데이터 (선택)
            commit: True면 즉시 커밋

        Returns:
            PersonalProfile 모델
        """
        profile = self.find_by_user_id(user_id)
        if profile:
            return profile
        return self.create_for_user(user_id, data, commit)

    def update_profile(
        self,
        user_id: int,
        data: Dict[str, Any],
        commit: bool = True
    ) -> Optional[PersonalProfile]:
        """프로필 업데이트

        Args:
            user_id: User ID
            data: 업데이트할 데이터
            commit: True면 즉시 커밋

        Returns:
            업데이트된 PersonalProfile 또는 None
        """
        profile = self.find_by_user_id(user_id)
        if not profile:
            return None

        for key, value in data.items():
            if hasattr(profile, key):
                setattr(profile, key, value)

        if commit:
            db.session.commit()
        return profile

    def find_public_profiles(self) -> List[PersonalProfile]:
        """공개된 프로필 목록 조회

        Returns:
            공개 프로필 목록
        """
        return PersonalProfile.query.filter_by(is_public=True).all()

    def find_by_email(self, email: str) -> Optional[PersonalProfile]:
        """이메일로 프로필 조회

        Args:
            email: 이메일 주소

        Returns:
            PersonalProfile 또는 None
        """
        return PersonalProfile.query.filter_by(email=email).first()

    def delete_by_user_id(self, user_id: int, commit: bool = True) -> bool:
        """사용자 ID로 프로필 삭제

        Args:
            user_id: User ID
            commit: True면 즉시 커밋

        Returns:
            삭제 성공 여부
        """
        profile = self.find_by_user_id(user_id)
        if profile:
            db.session.delete(profile)
            if commit:
                db.session.commit()
            return True
        return False


# 싱글톤 인스턴스
personal_profile_repository = PersonalProfileRepository()
