"""
Language Repository

어학 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Language
from app.shared.repositories.base_repository import BaseRelationRepository


class LanguageRepository(BaseRelationRepository[Language]):
    """어학 저장소"""

    def __init__(self):
        super().__init__(Language)
