"""
Project Repository

프로젝트 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.models import Project
from .base_repository import BaseRelationRepository


class ProjectRepository(BaseRelationRepository[Project]):
    """프로젝트 저장소"""

    def __init__(self):
        super().__init__(Project)

    def get_by_status(self, status: str) -> List[Dict]:
        """상태별 프로젝트 조회"""
        records = Project.query.filter_by(status=status).all()
        return [record.to_dict() for record in records]

    def get_active_projects(self, employee_id: str) -> List[Dict]:
        """특정 직원의 진행 중인 프로젝트 조회"""
        records = Project.query.filter(
            Project.employee_id == employee_id,
            Project.status.in_(['진행중', '계획중'])
        ).all()
        return [record.to_dict() for record in records]
