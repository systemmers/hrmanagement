"""
Promotion Repository

승진 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Promotion
from app.shared.repositories.base_repository import BaseRelationRepository


class PromotionRepository(BaseRelationRepository[Promotion]):
    """승진 저장소"""

    def __init__(self):
        super().__init__(Promotion)
