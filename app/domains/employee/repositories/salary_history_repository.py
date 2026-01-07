"""
SalaryHistory Repository

급여 이력 데이터의 CRUD 기능을 제공합니다.
"""
from app.domains.employee.models import SalaryHistory
from app.shared.repositories.base_repository import BaseRelationRepository


class SalaryHistoryRepository(BaseRelationRepository[SalaryHistory]):
    """급여 이력 저장소"""

    def __init__(self):
        super().__init__(SalaryHistory)
