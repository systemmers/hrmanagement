"""
FamilyMember Repository

가족 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import FamilyMember
from .base_repository import BaseRelationRepository


class FamilyMemberRepository(BaseRelationRepository):
    """가족 저장소"""

    def __init__(self):
        super().__init__(FamilyMember)
