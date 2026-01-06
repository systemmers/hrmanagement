"""
Training Repository

교육 훈련 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import Training
from app.repositories.base_repository import BaseRelationRepository


class TrainingRepository(BaseRelationRepository[Training]):
    """교육 훈련 저장소"""

    def __init__(self):
        super().__init__(Training)
