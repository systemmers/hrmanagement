"""
Attachment Repository

첨부파일 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.models import Attachment
from .base_repository import BaseRelationRepository


class AttachmentRepository(BaseRelationRepository):
    """첨부파일 저장소"""

    def __init__(self):
        super().__init__(Attachment)

    def get_by_category(self, employee_id: str, category: str) -> List[Dict]:
        """특정 직원의 카테고리별 첨부파일 조회"""
        records = Attachment.query.filter_by(
            employee_id=employee_id,
            category=category
        ).all()
        return [record.to_dict() for record in records]

    def get_by_file_type(self, employee_id: str, file_type: str) -> List[Dict]:
        """특정 직원의 파일 유형별 첨부파일 조회"""
        records = Attachment.query.filter_by(
            employee_id=employee_id,
            file_type=file_type
        ).all()
        return [record.to_dict() for record in records]

    def get_one_by_category(self, employee_id: int, category: str) -> Dict:
        """특정 직원의 카테고리별 단일 첨부파일 조회 (최신 1개)"""
        record = Attachment.query.filter_by(
            employee_id=employee_id,
            category=category
        ).order_by(Attachment.upload_date.desc()).first()
        return record.to_dict() if record else None

    def delete_by_category(self, employee_id: int, category: str) -> bool:
        """특정 직원의 카테고리별 첨부파일 삭제"""
        from app.database import db
        records = Attachment.query.filter_by(
            employee_id=employee_id,
            category=category
        ).all()
        for record in records:
            db.session.delete(record)
        db.session.commit()
        return len(records) > 0
