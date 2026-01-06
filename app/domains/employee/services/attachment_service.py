"""
첨부파일 서비스

첨부파일 관리 비즈니스 로직을 제공합니다.
Phase 2: Service 계층 표준화
"""
from typing import List, Dict, Optional


class AttachmentService:
    """
    첨부파일 서비스

    첨부파일 CRUD 및 조회 기능을 제공합니다.
    """

    @property
    def attachment_repo(self):
        """지연 초기화된 첨부파일 Repository"""
        from .. import get_attachment_repo
        return get_attachment_repo()

    def get_by_employee_id(self, employee_id: int) -> List[Dict]:
        """
        직원 ID로 첨부파일 목록 조회

        Args:
            employee_id: 직원 ID

        Returns:
            첨부파일 목록
        """
        models = self.attachment_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_by_category(self, employee_id: int, category: str) -> List[Dict]:
        """
        카테고리별 첨부파일 조회

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            해당 카테고리의 첨부파일 목록
        """
        return self.attachment_repo.get_by_category(employee_id, category)

    def get_one_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """
        카테고리별 첨부파일 1개 조회

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            첨부파일 또는 None
        """
        return self.attachment_repo.get_one_by_category(employee_id, category)

    def get_by_file_type(self, employee_id: int, file_type: str) -> List[Dict]:
        """
        파일 타입별 첨부파일 조회

        Args:
            employee_id: 직원 ID
            file_type: 파일 타입

        Returns:
            해당 타입의 첨부파일 목록
        """
        return self.attachment_repo.get_by_file_type(employee_id, file_type)

    def delete_by_category(self, employee_id: int, category: str) -> bool:
        """
        카테고리별 첨부파일 삭제

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            삭제 성공 여부
        """
        return self.attachment_repo.delete_by_category(employee_id, category)


# 싱글톤 인스턴스
attachment_service = AttachmentService()
