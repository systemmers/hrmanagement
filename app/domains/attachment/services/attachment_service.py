"""
첨부파일 서비스

첨부파일 관리 비즈니스 로직을 제공합니다.
Phase 31: 독립 도메인으로 분리 + owner_type/owner_id 범용화
"""
from typing import List, Dict, Optional


class AttachmentService:
    """
    첨부파일 서비스 (범용)

    첨부파일 CRUD 및 조회 기능을 제공합니다.
    """

    @property
    def attachment_repo(self):
        """지연 초기화된 첨부파일 Repository"""
        from app.domains.attachment import get_attachment_repo
        return get_attachment_repo()

    # ===== 범용 메서드 (owner_type + owner_id) =====

    def get_by_owner(self, owner_type: str, owner_id: int) -> List[Dict]:
        """
        소유자별 첨부파일 목록 조회

        Args:
            owner_type: 소유자 타입 (employee, profile, company)
            owner_id: 소유자 ID

        Returns:
            첨부파일 목록
        """
        models = self.attachment_repo.get_by_owner(owner_type, owner_id)
        return [m.to_dict() for m in models]

    def get_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> List[Dict]:
        """
        소유자 및 카테고리별 첨부파일 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명

        Returns:
            해당 카테고리의 첨부파일 목록
        """
        models = self.attachment_repo.get_by_owner_and_category(
            owner_type, owner_id, category
        )
        return [m.to_dict() for m in models]

    def get_one_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> Optional[Dict]:
        """
        소유자 및 카테고리별 첨부파일 1개 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명

        Returns:
            첨부파일 또는 None
        """
        model = self.attachment_repo.get_one_by_owner_and_category(
            owner_type, owner_id, category
        )
        return model.to_dict() if model else None

    def delete_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str, commit: bool = True
    ) -> int:
        """
        소유자 및 카테고리별 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 카테고리명
            commit: DB 커밋 여부

        Returns:
            삭제된 첨부파일 개수
        """
        return self.attachment_repo.delete_by_owner_and_category(
            owner_type, owner_id, category, commit
        )

    def delete_by_owner(self, owner_type: str, owner_id: int, commit: bool = True) -> int:
        """
        소유자의 모든 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            commit: DB 커밋 여부

        Returns:
            삭제된 첨부파일 개수
        """
        return self.attachment_repo.delete_by_owner(owner_type, owner_id, commit)

    # ===== 레거시 호환 메서드 (employee_id) =====

    def get_by_employee_id(self, employee_id: int) -> List[Dict]:
        """
        직원 ID로 첨부파일 목록 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID

        Returns:
            첨부파일 목록
        """
        return self.get_by_owner('employee', employee_id)

    def get_by_category(self, employee_id: int, category: str) -> List[Dict]:
        """
        카테고리별 첨부파일 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            해당 카테고리의 첨부파일 목록
        """
        return self.attachment_repo.get_by_category(employee_id, category)

    def get_one_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """
        카테고리별 첨부파일 1개 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명

        Returns:
            첨부파일 또는 None
        """
        return self.attachment_repo.get_one_by_category(employee_id, category)

    def get_by_file_type(self, employee_id: int, file_type: str) -> List[Dict]:
        """
        파일 타입별 첨부파일 조회 (레거시 호환)

        Args:
            employee_id: 직원 ID
            file_type: 파일 타입

        Returns:
            해당 타입의 첨부파일 목록
        """
        return self.attachment_repo.get_by_file_type(employee_id, file_type)

    def delete_by_category(self, employee_id: int, category: str, commit: bool = True) -> bool:
        """
        카테고리별 첨부파일 삭제 (레거시 호환)

        Args:
            employee_id: 직원 ID
            category: 카테고리명
            commit: DB 커밋 여부

        Returns:
            삭제 성공 여부
        """
        return self.attachment_repo.delete_by_category(employee_id, category, commit)


# 싱글톤 인스턴스
attachment_service = AttachmentService()
