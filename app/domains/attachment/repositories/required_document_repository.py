"""
RequiredDocument Repository

필수 서류 데이터의 CRUD 기능을 제공합니다.
Phase 4.1: 필수 서류 설정 기능 추가
"""
from typing import List, Optional
from app.domains.attachment.models import RequiredDocument
from app.shared.repositories.base_repository import BaseRepository


class RequiredDocumentRepository(BaseRepository[RequiredDocument]):
    """필수 서류 저장소"""

    def __init__(self):
        super().__init__(RequiredDocument)

    def get_by_company(
        self, company_id: int, active_only: bool = True
    ) -> List[RequiredDocument]:
        """법인별 필수 서류 목록 조회 (display_order 순 정렬)"""
        query = RequiredDocument.query.filter_by(company_id=company_id)
        if active_only:
            query = query.filter_by(is_active=True)
        return query.order_by(RequiredDocument.display_order.asc()).all()

    def get_required_by_company(self, company_id: int) -> List[RequiredDocument]:
        """법인별 필수 서류만 조회"""
        return RequiredDocument.query.filter_by(
            company_id=company_id,
            is_required=True,
            is_active=True
        ).order_by(RequiredDocument.display_order.asc()).all()

    def get_by_category(
        self, company_id: int, category: str
    ) -> List[RequiredDocument]:
        """카테고리별 필수 서류 조회"""
        return RequiredDocument.query.filter_by(
            company_id=company_id,
            category=category,
            is_active=True
        ).order_by(RequiredDocument.display_order.asc()).all()

    def get_by_linked_entity(
        self, company_id: int, entity_type: str
    ) -> List[RequiredDocument]:
        """연결 엔티티별 필수 서류 조회"""
        return RequiredDocument.query.filter_by(
            company_id=company_id,
            linked_entity_type=entity_type,
            is_active=True
        ).order_by(RequiredDocument.display_order.asc()).all()

    def find_by_name(
        self, company_id: int, name: str
    ) -> Optional[RequiredDocument]:
        """서류명으로 필수 서류 조회"""
        return RequiredDocument.query.filter_by(
            company_id=company_id,
            name=name
        ).first()

    def get_max_order(self, company_id: int) -> int:
        """법인의 최대 display_order 조회"""
        from sqlalchemy import func
        result = RequiredDocument.query.with_entities(
            func.max(RequiredDocument.display_order)
        ).filter_by(company_id=company_id).scalar()
        return result or 0

    def update_order(
        self, doc_id: int, new_order: int, commit: bool = True
    ) -> bool:
        """필수 서류 순서 변경"""
        from app.database import db
        doc = self.get_by_id(doc_id)
        if not doc:
            return False
        doc.display_order = new_order
        if commit:
            db.session.commit()
        return True

    def reorder_documents(
        self, company_id: int, doc_ids: List[int], commit: bool = True
    ) -> bool:
        """필수 서류 일괄 순서 재정렬

        Args:
            company_id: 법인 ID
            doc_ids: 순서대로 정렬된 서류 ID 목록
            commit: 커밋 여부

        Returns:
            성공 여부
        """
        from app.database import db
        for order, doc_id in enumerate(doc_ids):
            doc = self.get_by_id(doc_id)
            if doc and doc.company_id == company_id:
                doc.display_order = order
        if commit:
            db.session.commit()
        return True

    def deactivate(self, doc_id: int, commit: bool = True) -> bool:
        """필수 서류 비활성화"""
        from app.database import db
        doc = self.get_by_id(doc_id)
        if not doc:
            return False
        doc.is_active = False
        if commit:
            db.session.commit()
        return True

    def activate(self, doc_id: int, commit: bool = True) -> bool:
        """필수 서류 활성화"""
        from app.database import db
        doc = self.get_by_id(doc_id)
        if not doc:
            return False
        doc.is_active = True
        if commit:
            db.session.commit()
        return True


# 싱글톤 인스턴스
required_document_repository = RequiredDocumentRepository()
