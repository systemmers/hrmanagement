"""
Salary Repository

급여 데이터의 CRUD 기능을 제공합니다. (1:1 관계)
"""
from app.models import Salary
from .base_repository import BaseOneToOneRepository


class SalaryRepository(BaseOneToOneRepository[Salary]):
    """급여 저장소 (1:1)"""

    def __init__(self):
        super().__init__(Salary)
