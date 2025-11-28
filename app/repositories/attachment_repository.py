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
