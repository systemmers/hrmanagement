"""
분류 옵션 서비스

분류 옵션 관리 비즈니스 로직을 제공합니다.
Phase 2: Service 계층 표준화
"""
from typing import List, Optional, Dict, Any

from ..extensions import classification_repo
from ..models.classification_option import ClassificationOption


class ClassificationService:
    """
    분류 옵션 서비스

    분류 옵션 CRUD 및 조회 기능을 제공합니다.
    """

    def get_all(self) -> List[Dict[str, Any]]:
        """
        모든 분류 옵션 조회

        Returns:
            분류 옵션 목록
        """
        return classification_repo.get_all()

    def get_by_category(self, category: str) -> List[Dict[str, Any]]:
        """
        카테고리별 분류 옵션 조회

        Args:
            category: 카테고리명

        Returns:
            해당 카테고리의 분류 옵션 목록
        """
        return classification_repo.get_by_category(category)

    def get_by_id(self, option_id: int) -> Optional[ClassificationOption]:
        """
        ID로 분류 옵션 조회

        Args:
            option_id: 분류 옵션 ID

        Returns:
            분류 옵션 또는 None
        """
        return classification_repo.get_by_id(option_id)

    # ========================================
    # 부서 관리
    # ========================================

    def add_department(self, department: str) -> bool:
        """부서 추가"""
        return classification_repo.add_department(department)

    def update_department(self, old_department: str, new_department: str) -> bool:
        """부서 수정"""
        return classification_repo.update_department(old_department, new_department)

    def delete_department(self, department: str) -> bool:
        """부서 삭제"""
        return classification_repo.delete_department(department)

    # ========================================
    # 직급 관리
    # ========================================

    def add_position(self, position: str) -> bool:
        """직급 추가"""
        return classification_repo.add_position(position)

    def update_position(self, old_position: str, new_position: str) -> bool:
        """직급 수정"""
        return classification_repo.update_position(old_position, new_position)

    def delete_position(self, position: str) -> bool:
        """직급 삭제"""
        return classification_repo.delete_position(position)

    # ========================================
    # 상태 관리
    # ========================================

    def add_status(self, value: str, label: str) -> bool:
        """상태 추가"""
        return classification_repo.add_status(value, label)

    def update_status(self, old_value: str, new_value: str, new_label: str) -> bool:
        """상태 수정"""
        return classification_repo.update_status(old_value, new_value, new_label)

    def delete_status(self, value: str) -> bool:
        """상태 삭제"""
        return classification_repo.delete_status(value)


# 싱글톤 인스턴스
classification_service = ClassificationService()
