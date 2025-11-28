"""
Training Repository

교육 훈련 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import Training
from .base_repository import BaseRelationRepository


class TrainingRepository(BaseRelationRepository):
    """교육 훈련 저장소"""

    def __init__(self):
        super().__init__(Training)
