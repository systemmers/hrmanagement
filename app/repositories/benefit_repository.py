"""
Benefit Repository

복리후생 데이터의 CRUD 기능을 제공합니다. (1:1 관계)
"""
from app.models import Benefit
from .base_repository import BaseOneToOneRepository


class BenefitRepository(BaseOneToOneRepository[Benefit]):
    """복리후생 저장소 (1:1)"""

    def __init__(self):
        super().__init__(Benefit)
