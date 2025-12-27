"""
사용자 서비스

사용자 인증 및 계정 관리 비즈니스 로직을 제공합니다.
Phase 2: Service 계층 표준화
Phase 24: Option A 레이어 분리 - Service는 Dict 반환 표준화
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

        Phase 24: find_by_id() + to_dict() 패턴 적용

        Args:
            user_id: 사용자 ID

        Returns:
            User Dict 또는 None
        """
        model = self.user_repo.find_by_id(user_id)
        return model.to_dict() if model else None

    def get_model_by_id(self, user_id: int) -> Optional[Any]:
        """사용자 ID로 모델 객체 조회

        Args:
            user_id: 사용자 ID

        Returns:
            User 모델 객체 또는 None
        """
        return self.user_repo.find_by_id(user_id)

    def get_by_company_and_account_type(
        self,
        company_id: int,
        account_type: str
    ) -> list:
        """회사 ID와 계정 유형으로 사용자 목록 조회

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            company_id: 회사 ID
            account_type: 계정 유형 (employee_sub, corporate 등)

        Returns:
            User 모델 객체 리스트
        """
        return self.user_repo.get_by_company_and_account_type(company_id, account_type)

    def get_employee_sub_users_with_employee(self, company_id: int) -> list:
        """회사 소속 employee_sub 계정 목록 조회 (Employee 정보 포함)

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            company_id: 회사 ID

        Returns:
            User 모델 객체 리스트 (employee 관계 로드됨)
        """
        return self.user_repo.get_employee_sub_users_with_employee(company_id)

    def find_by_employee_id(self, employee_id: int) -> Optional[Any]:
        """Employee ID로 연결된 User 조회

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            employee_id: Employee.id

        Returns:
            User 모델 객체 또는 None
        """
        return self.user_repo.find_by_employee_id(employee_id)


# 싱글톤 인스턴스
user_service = UserService()
