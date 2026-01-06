"""
MilitaryService Repository

병역 데이터의 CRUD 기능을 제공합니다. (1:1 관계)
"""
from app.domains.employee.models import MilitaryService
from app.repositories.base_repository import BaseOneToOneRepository


class MilitaryServiceRepository(BaseOneToOneRepository[MilitaryService]):
    """병역 저장소 (1:1)"""

    def __init__(self):
        super().__init__(MilitaryService)
