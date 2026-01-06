"""
Education Repository

학력 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Education
from app.repositories.base_repository import BaseRelationRepository


class EducationRepository(BaseRelationRepository[Education]):
    """학력 저장소"""

    def __init__(self):
        super().__init__(Education)
