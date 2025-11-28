"""
Contract Repository

계약 데이터의 CRUD 기능을 제공합니다. (1:1 관계)
"""
from app.models import Contract
from .base_repository import BaseOneToOneRepository


class ContractRepository(BaseOneToOneRepository):
    """계약 저장소 (1:1)"""

    def __init__(self):
        super().__init__(Contract)
