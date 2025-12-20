"""
Company Document Repository

법인 서류를 관리합니다.
"""
from typing import Dict, List, Optional
from datetime import datetime
from app.database import db
from app.models import CompanyDocument
from .base_repository import BaseRepository


class CompanyDocumentRepository(BaseRepository[CompanyDocument]):
    """법인 서류 저장소"""

    def __init__(self):
        super().__init__(CompanyDocument)

    def get_by_company(self, company_id: int, include_inactive: bool = False) -> List[Dict]:
        """법인별 모든 서류 조회"""
        query = CompanyDocument.query.filter_by(company_id=company_id)
        if not include_inactive:
            query = query.filter_by(is_active=True)
        documents = query.order_by(CompanyDocument.category, CompanyDocument.uploaded_at.desc()).all()
        return [doc.to_dict() for doc in documents]

    def get_by_category(self, company_id: int, category: str,
                        include_inactive: bool = False) -> List[Dict]:
        """카테고리별 서류 조회"""
        query = CompanyDocument.query.filter_by(
            company_id=company_id,
            category=category
        )
        if not include_inactive:
            query = query.filter_by(is_active=True)
        documents = query.order_by(CompanyDocument.uploaded_at.desc()).all()
        return [doc.to_dict() for doc in documents]

    def get_by_document_type(self, company_id: int, document_type: str) -> Optional[Dict]:
        """서류 유형별 최신 서류 조회"""
        document = CompanyDocument.query.filter_by(
            company_id=company_id,
            document_type=document_type,
            is_active=True
        ).order_by(CompanyDocument.uploaded_at.desc()).first()
        return document.to_dict() if document else None

    def create(self, data: Dict) -> Dict:
        """서류 등록"""
        document = CompanyDocument.from_dict(data)
        db.session.add(document)
        db.session.commit()
        return document.to_dict()

    def update(self, document_id: int, data: Dict) -> Optional[Dict]:
        """서류 수정"""
        document = CompanyDocument.query.get(document_id)
        if not document:
            return None

        updatable_fields = [
            'title', 'description', 'category', 'document_type',
            'version', 'is_required', 'visibility', 'expires_at'
        ]

        for field in updatable_fields:
            camel_key = ''.join(
                word.capitalize() if i > 0 else word
                for i, word in enumerate(field.split('_'))
            )
            if camel_key in data:
                setattr(document, field, data[camel_key])

        db.session.commit()
        return document.to_dict()

    def delete(self, document_id: int, soft_delete: bool = True) -> bool:
        """서류 삭제"""
        document = CompanyDocument.query.get(document_id)
        if not document:
            return False

        if soft_delete:
            document.is_active = False
        else:
            db.session.delete(document)

        db.session.commit()
        return True

    def get_required_documents(self, company_id: int) -> List[Dict]:
        """필수 서류 목록 조회"""
        documents = CompanyDocument.query.filter_by(
            company_id=company_id,
            is_required=True,
            is_active=True
        ).order_by(CompanyDocument.uploaded_at.desc()).all()
        return [doc.to_dict() for doc in documents]

    def get_expiring_documents(self, company_id: int, days: int = 30) -> List[Dict]:
        """만료 예정 서류 조회"""
        from datetime import timedelta
        cutoff = datetime.utcnow() + timedelta(days=days)

        documents = CompanyDocument.query.filter(
            CompanyDocument.company_id == company_id,
            CompanyDocument.is_active == True,
            CompanyDocument.expires_at != None,
            CompanyDocument.expires_at <= cutoff
        ).order_by(CompanyDocument.expires_at).all()
        return [doc.to_dict() for doc in documents]

    def get_by_visibility(self, company_id: int, visibility: str) -> List[Dict]:
        """가시성별 서류 조회"""
        documents = CompanyDocument.query.filter_by(
            company_id=company_id,
            visibility=visibility,
            is_active=True
        ).order_by(CompanyDocument.uploaded_at.desc()).all()
        return [doc.to_dict() for doc in documents]

    def update_file_info(self, document_id: int, file_path: str,
                         file_name: str, file_size: int, file_type: str) -> Optional[Dict]:
        """파일 정보 업데이트"""
        document = CompanyDocument.query.get(document_id)
        if not document:
            return None

        document.file_path = file_path
        document.file_name = file_name
        document.file_size = file_size
        document.file_type = file_type
        document.uploaded_at = datetime.utcnow()

        db.session.commit()
        return document.to_dict()

    def update_ai_info(self, document_id: int, ai_data: Dict) -> Optional[Dict]:
        """AI 처리 정보 업데이트"""
        document = CompanyDocument.query.get(document_id)
        if not document:
            return None

        document.ai_processed = True
        document.ai_detected_type = ai_data.get('detectedType')
        document.ai_extracted_data = ai_data.get('extractedData')
        document.ai_confidence = ai_data.get('confidence')

        db.session.commit()
        return document.to_dict(include_ai=True)

    def get_statistics(self, company_id: int) -> Dict:
        """서류 통계 조회"""
        total = CompanyDocument.query.filter_by(
            company_id=company_id,
            is_active=True
        ).count()

        by_category = {}
        for category in CompanyDocument.VALID_CATEGORIES:
            count = CompanyDocument.query.filter_by(
                company_id=company_id,
                category=category,
                is_active=True
            ).count()
            by_category[category] = count

        required_count = CompanyDocument.query.filter_by(
            company_id=company_id,
            is_required=True,
            is_active=True
        ).count()

        from datetime import timedelta
        expiring_count = CompanyDocument.query.filter(
            CompanyDocument.company_id == company_id,
            CompanyDocument.is_active == True,
            CompanyDocument.expires_at != None,
            CompanyDocument.expires_at <= datetime.utcnow() + timedelta(days=30)
        ).count()

        return {
            'total': total,
            'byCategory': by_category,
            'required': required_count,
            'expiringSoon': expiring_count
        }
