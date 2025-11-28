"""
Career Repository

경력 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import Career
from .base_repository import BaseRelationRepository


class CareerRepository(BaseRelationRepository):
    """경력 저장소"""

    def __init__(self):
        super().__init__(Career)
