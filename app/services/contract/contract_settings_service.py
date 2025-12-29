"""
Contract Settings Service

계약 데이터 공유 설정 및 동기화 로그 관련 비즈니스 로직을 처리합니다.
- 데이터 공유 설정 조회/수정
- 동기화 로그 조회
"""
from typing import Dict, Optional, List, Any

from ...database import db
from ...models.person_contract import DataSharingSettings, SyncLog
from ..base import ServiceResult


class ContractSettingsService:
    """계약 설정 서비스"""

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        from ...extensions import person_contract_repo
        return person_contract_repo

    # ========================================
    # 데이터 공유 설정
    # ========================================

    def get_sharing_settings(self, contract_id: int) -> Dict:
        """데이터 공유 설정 조회"""
        return self.contract_repo.get_sharing_settings(contract_id)

    def get_sharing_settings_model(self, contract_id: int) -> Optional[Any]:
        """데이터 공유 설정 모델 조회

        Args:
            contract_id: 계약 ID

        Returns:
            DataSharingSettings 모델 또는 None
        """
        return DataSharingSettings.query.filter_by(contract_id=contract_id).first()

    def update_or_create_sharing_settings(
        self, contract_id: int, commit: bool = True, **kwargs
    ) -> Any:
        """데이터 공유 설정 생성 또는 업데이트

        Args:
            contract_id: 계약 ID
            commit: 트랜잭션 커밋 여부 (atomic_transaction 내에서는 False)
            **kwargs: 업데이트할 필드 (share_basic_info, is_realtime_sync 등)

        Returns:
            DataSharingSettings 모델
        """
        settings = self.get_sharing_settings_model(contract_id)
        if not settings:
            settings = DataSharingSettings(contract_id=contract_id)
            db.session.add(settings)

        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        if commit:
            db.session.commit()
        else:
            db.session.flush()

        return settings

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> ServiceResult[Dict]:
        """데이터 공유 설정 업데이트

        Returns:
            ServiceResult[Dict]
        """
        try:
            result = self.contract_repo.update_sharing_settings(contract_id, settings)
            return ServiceResult.ok(data=result)
        except ValueError as e:
            return ServiceResult.fail(str(e))

    # ========================================
    # 동기화 로그
    # ========================================

    def get_sync_logs_filtered(
        self, contract_id: int, sync_type: str = None, limit: int = 50
    ) -> List[Dict]:
        """동기화 로그 조회 (필터링 지원)

        Args:
            contract_id: 계약 ID
            sync_type: 동기화 유형 필터 (선택)
            limit: 최대 조회 수

        Returns:
            로그 목록 (Dict)
        """
        query = SyncLog.query.filter_by(contract_id=contract_id)
        if sync_type:
            query = query.filter_by(sync_type=sync_type)
        logs = query.order_by(SyncLog.executed_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        """동기화 로그 조회"""
        return self.contract_repo.get_sync_logs(contract_id, limit)


# 싱글톤 인스턴스
contract_settings_service = ContractSettingsService()
