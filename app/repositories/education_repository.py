"""
Education Repository

학력 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import Education
from .base_repository import BaseRelationRepository


class EducationRepository(BaseRelationRepository[Education]):
    """학력 저장소"""

    def __init__(self):
        super().__init__(Education)
