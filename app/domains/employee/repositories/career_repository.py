"""
Career Repository

경력 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Career
from app.repositories.base_repository import BaseRelationRepository


class CareerRepository(BaseRelationRepository[Career]):
    """경력 저장소"""

    def __init__(self):
        super().__init__(Career)
