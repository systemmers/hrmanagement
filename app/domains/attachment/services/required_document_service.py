"""
필수 서류 서비스

필수 서류 관리 비즈니스 로직을 제공합니다.
Phase 4.1: 필수 서류 설정 기능 추가
"""
from typing import List, Dict, Optional

from app.database import db


class RequiredDocumentService:
    """
    필수 서류 서비스

    법인별 필수 서류 관리 CRUD 기능을 제공합니다.
    """

    @property
    def repo(self):
        """지연 초기화된 RequiredDocument Repository"""
        from app.domains.attachment.repositories import required_document_repository
        return required_document_repository

    # ===== 조회 =====

    def get_by_company(
        self, company_id: int, active_only: bool = True
    ) -> List[Dict]:
        """
        법인별 필수 서류 목록 조회

        Args:
            company_id: 법인 ID
            active_only: 활성화된 항목만 조회

        Returns:
            필수 서류 목록
        """
        models = self.repo.get_by_company(company_id, active_only)
        return [m.to_dict() for m in models]

    def get_required_by_company(self, company_id: int) -> List[Dict]:
        """
        법인별 필수 제출 서류만 조회

        Args:
            company_id: 법인 ID

        Returns:
            필수 제출 서류 목록
        """
        models = self.repo.get_required_by_company(company_id)
        return [m.to_dict() for m in models]

    def get_by_category(self, company_id: int, category: str) -> List[Dict]:
        """
        카테고리별 필수 서류 조회

        Args:
            company_id: 법인 ID
            category: 서류 분류

        Returns:
            해당 카테고리의 필수 서류 목록
        """
        models = self.repo.get_by_category(company_id, category)
        return [m.to_dict() for m in models]

    def get_by_linked_entity(
        self, company_id: int, entity_type: str
    ) -> List[Dict]:
        """
        연결 엔티티별 필수 서류 조회

        Args:
            company_id: 법인 ID
            entity_type: 연결 엔티티 타입 (education, career, certificate 등)

        Returns:
            해당 엔티티에 연결된 필수 서류 목록
        """
        models = self.repo.get_by_linked_entity(company_id, entity_type)
        return [m.to_dict() for m in models]

    def get_by_id(self, doc_id: int) -> Optional[Dict]:
        """
        필수 서류 단일 조회

        Args:
            doc_id: 필수 서류 ID

        Returns:
            필수 서류 또는 None
        """
        model = self.repo.get_by_id(doc_id)
        return model.to_dict() if model else None

    # ===== 생성 =====

    def create(self, data: Dict, commit: bool = True) -> Dict:
        """
        필수 서류 생성

        Args:
            data: 서류 데이터
            commit: 커밋 여부

        Returns:
            생성된 필수 서류
        """
        from app.domains.attachment.models import RequiredDocument

        # display_order 자동 설정
        if 'display_order' not in data or data.get('display_order') is None:
            max_order = self.repo.get_max_order(data['company_id'])
            data['display_order'] = max_order + 1

        model = RequiredDocument(**data)
        db.session.add(model)
        if commit:
            db.session.commit()
        return model.to_dict()

    # ===== 수정 =====

    def update(self, doc_id: int, data: Dict, commit: bool = True) -> Optional[Dict]:
        """
        필수 서류 수정

        Args:
            doc_id: 필수 서류 ID
            data: 수정할 데이터
            commit: 커밋 여부

        Returns:
            수정된 필수 서류 또는 None
        """
        model = self.repo.get_by_id(doc_id)
        if not model:
            return None

        # 수정 가능 필드
        updatable_fields = [
            'name', 'category', 'description', 'is_required',
            'display_order', 'linked_entity_type', 'is_active'
        ]
        for field in updatable_fields:
            if field in data:
                setattr(model, field, data[field])

        if commit:
            db.session.commit()
        return model.to_dict()

    def reorder(
        self, company_id: int, doc_ids: List[int], commit: bool = True
    ) -> bool:
        """
        필수 서류 순서 재정렬

        Args:
            company_id: 법인 ID
            doc_ids: 순서대로 정렬된 서류 ID 목록
            commit: 커밋 여부

        Returns:
            성공 여부
        """
        return self.repo.reorder_documents(company_id, doc_ids, commit)

    def reorder_by_items(
        self, orders: List[Dict], commit: bool = True
    ) -> bool:
        """
        필수 서류 순서 재정렬 (개별 항목 방식)

        Args:
            orders: [{"id": 1, "order": 1}, {"id": 2, "order": 2}, ...]
            commit: 커밋 여부

        Returns:
            성공 여부
        """
        for item in orders:
            doc_id = item.get('id')
            new_order = item.get('order')
            if doc_id and new_order is not None:
                model = self.repo.get_by_id(doc_id)
                if model:
                    model.display_order = new_order

        if commit:
            db.session.commit()
        return True

    # ===== 삭제/비활성화 =====

    def delete(self, doc_id: int, commit: bool = True) -> bool:
        """
        필수 서류 삭제

        Args:
            doc_id: 필수 서류 ID
            commit: 커밋 여부

        Returns:
            삭제 성공 여부
        """
        model = self.repo.get_by_id(doc_id)
        if not model:
            return False

        db.session.delete(model)
        if commit:
            db.session.commit()
        return True

    def deactivate(self, doc_id: int, commit: bool = True) -> bool:
        """
        필수 서류 비활성화 (소프트 삭제)

        Args:
            doc_id: 필수 서류 ID
            commit: 커밋 여부

        Returns:
            성공 여부
        """
        return self.repo.deactivate(doc_id, commit)

    def activate(self, doc_id: int, commit: bool = True) -> bool:
        """
        필수 서류 활성화

        Args:
            doc_id: 필수 서류 ID
            commit: 커밋 여부

        Returns:
            성공 여부
        """
        return self.repo.activate(doc_id, commit)

    # ===== 검증 =====

    def check_completion(
        self, company_id: int, owner_type: str, owner_id: int
    ) -> Dict:
        """
        필수 서류 제출 현황 확인

        Args:
            company_id: 법인 ID
            owner_type: 소유자 타입
            owner_id: 소유자 ID

        Returns:
            {
                'total': 전체 필수 서류 수,
                'submitted': 제출된 서류 수,
                'missing': 미제출 서류 목록,
                'completed': 제출 완료 여부
            }
        """
        from app.domains.attachment.services import attachment_service

        # 필수 서류 목록 조회
        required_docs = self.get_required_by_company(company_id)
        total = len(required_docs)

        if total == 0:
            return {
                'total': 0,
                'submitted': 0,
                'missing': [],
                'completed': True
            }

        # 제출된 첨부파일 조회
        attachments = attachment_service.get_by_owner(owner_type, owner_id)
        submitted_categories = {att.get('category') for att in attachments}

        # 미제출 서류 확인
        missing = []
        for doc in required_docs:
            # 서류명 또는 카테고리로 매칭
            doc_name = doc.get('name', '')
            doc_category = doc.get('category', '')

            if doc_name not in submitted_categories and doc_category not in submitted_categories:
                missing.append(doc)

        submitted = total - len(missing)

        return {
            'total': total,
            'submitted': submitted,
            'missing': missing,
            'completed': len(missing) == 0
        }


# 싱글톤 인스턴스
required_document_service = RequiredDocumentService()
