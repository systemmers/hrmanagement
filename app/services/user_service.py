"""
사용자 서비스

사용자 인증 및 계정 관리 비즈니스 로직을 제공합니다.
Phase 2: Service 계층 표준화
"""
from typing import Dict, Optional, Any

from ..extensions import user_repo


class UserService:
    """
    사용자 서비스

    인증, 비밀번호 관리, 계정 설정 기능을 제공합니다.
    """

    def __init__(self):
        self.user_repo = user_repo

    # ========================================
    # 인증
    # ========================================

    def authenticate(self, username: str, password: str) -> Optional[Any]:
        """사용자 인증

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            User 객체 또는 None
        """
        return self.user_repo.authenticate(username, password)

    # ========================================
    # 비밀번호 관리
    # ========================================

    def update_password(self, user_id: int, new_password: str) -> bool:
        """비밀번호 변경

        Args:
            user_id: 사용자 ID
            new_password: 새 비밀번호

        Returns:
            성공 여부
        """
        return self.user_repo.update_password(user_id, new_password)

    # ========================================
    # 개인정보 공개 설정
    # ========================================

    def get_privacy_settings(self, user_id: int) -> Optional[Dict]:
        """개인정보 공개 설정 조회

        Args:
            user_id: 사용자 ID

        Returns:
            공개 설정 Dict 또는 None
        """
        return self.user_repo.get_privacy_settings(user_id)

    def update_privacy_settings(self, user_id: int, settings: Dict) -> bool:
        """개인정보 공개 설정 저장

        Args:
            user_id: 사용자 ID
            settings: 공개 설정 Dict

        Returns:
            성공 여부
        """
        return self.user_repo.update_privacy_settings(user_id, settings)

    # ========================================
    # 계정 관리
    # ========================================

    def deactivate(self, user_id: int) -> bool:
        """계정 비활성화 (soft delete)

        Args:
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        return self.user_repo.deactivate(user_id)

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """사용자 ID로 조회 (Dict 반환)

        Args:
            user_id: 사용자 ID

        Returns:
            User Dict 또는 None
        """
        return self.user_repo.get_by_id(user_id)

    def get_model_by_id(self, user_id: int) -> Optional[Any]:
        """사용자 ID로 모델 객체 조회

        Args:
            user_id: 사용자 ID

        Returns:
            User 모델 객체 또는 None
        """
        return self.user_repo.get_model_by_id(user_id)


# 싱글톤 인스턴스
user_service = UserService()
