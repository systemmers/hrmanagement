"""
Attachment Repository

첨부파일 데이터의 CRUD 기능을 제공합니다.
Phase 31: 독립 도메인으로 분리 + owner_type/owner_id 범용화
"""
from typing import List, Dict, Optional
from app.domains.attachment.models import Attachment
from app.shared.repositories.base_repository import BaseRelationRepository


class AttachmentRepository(BaseRelationRepository[Attachment]):
    """첨부파일 저장소 (범용)"""

    def __init__(self):
        super().__init__(Attachment)

    # ===== 범용 메서드 (owner_type + owner_id) =====

    def get_by_owner(self, owner_type: str, owner_id: int) -> List[Attachment]:
        """소유자별 첨부파일 조회 (display_order 순 정렬)"""
        return Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id
        ).order_by(Attachment.display_order.asc()).all()

    def get_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> List[Attachment]:
        """소유자 및 카테고리별 첨부파일 조회 (display_order 순 정렬)"""
        return Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            category=category
        ).order_by(Attachment.display_order.asc()).all()

    def get_one_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str
    ) -> Optional[Attachment]:
        """소유자 및 카테고리별 단일 첨부파일 조회 (최신 1개)"""
        return Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            category=category
        ).order_by(Attachment.upload_date.desc()).first()

    def delete_by_owner_and_category(
        self, owner_type: str, owner_id: int, category: str, commit: bool = True
    ) -> int:
        """소유자 및 카테고리별 첨부파일 삭제"""
        from app.database import db
        records = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            category=category
        ).all()
        count = len(records)
        for record in records:
            db.session.delete(record)
        if commit:
            db.session.commit()
        return count

    def delete_by_owner(self, owner_type: str, owner_id: int, commit: bool = True) -> int:
        """소유자의 모든 첨부파일 삭제"""
        from app.database import db
        records = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id
        ).all()
        count = len(records)
        for record in records:
            db.session.delete(record)
        if commit:
            db.session.commit()
        return count

    # ===== 레거시 호환 메서드 (employee_id) =====

    def get_by_employee_id(self, employee_id: int) -> List[Attachment]:
        """직원 ID로 첨부파일 조회 (레거시 호환)"""
        return self.get_by_owner('employee', employee_id)

    def get_by_category(self, employee_id: int, category: str) -> List[Dict]:
        """특정 직원의 카테고리별 첨부파일 조회 (레거시 호환)"""
        records = self.get_by_owner_and_category('employee', employee_id, category)
        return [record.to_dict() for record in records]

    def get_one_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """특정 직원의 카테고리별 단일 첨부파일 조회 (레거시 호환)"""
        record = self.get_one_by_owner_and_category('employee', employee_id, category)
        return record.to_dict() if record else None

    def delete_by_category(self, employee_id: int, category: str, commit: bool = True) -> bool:
        """특정 직원의 카테고리별 첨부파일 삭제 (레거시 호환)"""
        count = self.delete_by_owner_and_category('employee', employee_id, category, commit)
        return count > 0

    def get_by_file_type(self, employee_id: int, file_type: str) -> List[Dict]:
        """특정 직원의 파일 유형별 첨부파일 조회"""
        records = Attachment.query.filter_by(
            owner_type='employee',
            owner_id=employee_id,
            file_type=file_type
        ).all()
        return [record.to_dict() for record in records]

    # ===== Phase 33: 계약 기반 동기화/분리 =====

    def find_synced_by_contract(
        self, owner_type: str, owner_id: int, contract_id: int
    ) -> List[Attachment]:
        """특정 계약에서 동기화된 첨부파일 조회

        Args:
            owner_type: 소유자 타입 (employee, profile 등)
            owner_id: 소유자 ID
            contract_id: 동기화 출처 계약 ID

        Returns:
            동기화된 첨부파일 목록
        """
        from app.domains.attachment.models.attachment import SourceType
        return Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            source_type=SourceType.SYNCED,
            source_contract_id=contract_id
        ).all()

    def find_all_synced_by_owner(self, owner_type: str, owner_id: int) -> List[Attachment]:
        """소유자의 모든 동기화된 첨부파일 조회

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID

        Returns:
            동기화된 첨부파일 목록
        """
        from app.domains.attachment.models.attachment import SourceType
        return Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            source_type=SourceType.SYNCED
        ).all()

    def delete_synced_by_category(
        self, owner_type: str, owner_id: int, category: str, contract_id: int, commit: bool = True
    ) -> int:
        """특정 계약에서 동기화된 특정 카테고리 첨부파일 삭제

        Args:
            owner_type: 소유자 타입
            owner_id: 소유자 ID
            category: 첨부파일 카테고리
            contract_id: 동기화 출처 계약 ID
            commit: 커밋 여부

        Returns:
            삭제된 레코드 수
        """
        from app.database import db
        from app.domains.attachment.models.attachment import SourceType

        records = Attachment.query.filter_by(
            owner_type=owner_type,
            owner_id=owner_id,
            category=category,
            source_type=SourceType.SYNCED,
            source_contract_id=contract_id
        ).all()
        count = len(records)
        for record in records:
            db.session.delete(record)
        if commit:
            db.session.commit()
        return count
