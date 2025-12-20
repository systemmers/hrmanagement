"""
HrProject Repository

인사이력 프로젝트 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.database import db
from app.models import HrProject
from .base_repository import BaseRelationRepository


class HrProjectRepository(BaseRelationRepository[HrProject]):
    """인사이력 프로젝트 저장소"""

    def __init__(self):
        super().__init__(HrProject)

    def get_active_projects(self, employee_id: int) -> List[Dict]:
        """특정 직원의 진행 중인 프로젝트 조회"""
        records = HrProject.query.filter(
            HrProject.employee_id == employee_id,
            HrProject.end_date.is_(None)
        ).all()
        return [record.to_dict() for record in records]
