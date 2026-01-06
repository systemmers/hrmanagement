"""
Award Repository

수상/징계 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.domains.employee.models import Award
from app.repositories.base_repository import BaseRelationRepository


class AwardRepository(BaseRelationRepository[Award]):
    """수상/징계 저장소"""

    def __init__(self):
        super().__init__(Award)

    def get_by_type(self, employee_id: str, award_type: str) -> List[Dict]:
        """특정 직원의 유형별 수상/징계 조회"""
        records = Award.query.filter_by(
            employee_id=employee_id,
            award_type=award_type
        ).all()
        return [record.to_dict() for record in records]
