"""
Insurance Repository

보험 데이터의 CRUD 기능을 제공합니다. (1:1 관계)
"""
from app.models import Insurance
from .base_repository import BaseOneToOneRepository


class InsuranceRepository(BaseOneToOneRepository[Insurance]):
    """보험 저장소 (1:1)"""

    def __init__(self):
        super().__init__(Insurance)
