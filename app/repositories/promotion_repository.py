"""
Promotion Repository

승진 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import Promotion
from .base_repository import BaseRelationRepository


class PromotionRepository(BaseRelationRepository):
    """승진 저장소"""

    def __init__(self):
        super().__init__(Promotion)
