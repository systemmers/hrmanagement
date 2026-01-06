"""
Evaluation Repository

인사평가 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Evaluation
from app.repositories.base_repository import BaseRelationRepository


class EvaluationRepository(BaseRelationRepository[Evaluation]):
    """인사평가 저장소"""

    def __init__(self):
        super().__init__(Evaluation)
