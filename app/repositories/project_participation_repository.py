"""
ProjectParticipation Repository

프로젝트 참여이력 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.models import ProjectParticipation
from .base_repository import BaseRelationRepository


class ProjectParticipationRepository(BaseRelationRepository[ProjectParticipation]):
    """프로젝트 참여이력 저장소"""

    def __init__(self):
        super().__init__(ProjectParticipation)
