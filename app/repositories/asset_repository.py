"""
Asset Repository

자산 배정 데이터의 CRUD 기능을 제공합니다.
"""
from typing import List, Dict
from app.models import Asset
from .base_repository import BaseRelationRepository


class AssetRepository(BaseRelationRepository[Asset]):
    """자산 배정 저장소"""

    def __init__(self):
        super().__init__(Asset)

    def get_by_status(self, status: str) -> List[Dict]:
        """상태별 자산 조회"""
        records = Asset.query.filter_by(status=status).all()
        return [record.to_dict() for record in records]

    def get_active_assets(self, employee_id: str) -> List[Dict]:
        """특정 직원의 현재 배정된 자산 조회"""
        records = Asset.query.filter(
            Asset.employee_id == employee_id,
            Asset.return_date.is_(None)
        ).all()
        return [record.to_dict() for record in records]
