"""
CorporateAdminProfile Repository

법인 관리자 프로필의 CRUD 기능을 제공합니다.
"""
from typing import Optional, Dict, List
from app.database import db
from app.models.corporate_admin_profile import CorporateAdminProfile
from .base_repository import BaseRepository


class CorporateAdminProfileRepository(BaseRepository[CorporateAdminProfile]):
    """법인 관리자 프로필 저장소"""

    def __init__(self):
        super().__init__(CorporateAdminProfile)

    def get_by_user_id(self, user_id: int) -> Optional[CorporateAdminProfile]:
        """사용자 ID로 프로필 조회 (모델 객체 반환)"""
        return CorporateAdminProfile.query.filter_by(user_id=user_id).first()

    def get_dict_by_user_id(self, user_id: int) -> Optional[Dict]:
        """사용자 ID로 프로필 조회 (딕셔너리 반환)"""
        profile = self.get_by_user_id(user_id)
        return profile.to_dict() if profile else None

    def get_by_company_id(self, company_id: int) -> List[CorporateAdminProfile]:
        """회사 ID로 관리자 프로필 목록 조회"""
        return CorporateAdminProfile.query.filter_by(company_id=company_id).all()

    def get_active_by_company_id(self, company_id: int) -> List[CorporateAdminProfile]:
        """회사 ID로 활성 관리자 프로필 목록 조회"""
        return CorporateAdminProfile.query.filter_by(
            company_id=company_id,
            is_active=True
        ).all()

    def create_profile(self, user_id: int, company_id: int, name: str, **kwargs) -> CorporateAdminProfile:
        """새 프로필 생성"""
        profile = CorporateAdminProfile(
            user_id=user_id,
            company_id=company_id,
            name=name,
            english_name=kwargs.get('english_name'),
            position=kwargs.get('position'),
            mobile_phone=kwargs.get('mobile_phone'),
            office_phone=kwargs.get('office_phone'),
            email=kwargs.get('email'),
            photo=kwargs.get('photo'),
            department=kwargs.get('department'),
            bio=kwargs.get('bio'),
            is_active=kwargs.get('is_active', True)
        )
        db.session.add(profile)
        db.session.commit()
        return profile

    def update_profile(self, profile: CorporateAdminProfile, data: Dict) -> CorporateAdminProfile:
        """프로필 정보 수정"""
        allowed_fields = [
            'name', 'english_name', 'position', 'mobile_phone',
            'office_phone', 'email', 'photo', 'department', 'bio', 'is_active'
        ]
        for field in allowed_fields:
            if field in data:
                setattr(profile, field, data[field])
        db.session.commit()
        return profile

    def exists_for_user(self, user_id: int) -> bool:
        """사용자에 대한 프로필 존재 여부 확인"""
        return CorporateAdminProfile.query.filter_by(user_id=user_id).first() is not None

    def deactivate(self, profile: CorporateAdminProfile) -> CorporateAdminProfile:
        """프로필 비활성화"""
        profile.is_active = False
        db.session.commit()
        return profile

    def activate(self, profile: CorporateAdminProfile) -> CorporateAdminProfile:
        """프로필 활성화"""
        profile.is_active = True
        db.session.commit()
        return profile
