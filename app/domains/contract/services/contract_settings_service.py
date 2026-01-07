"""
Contract Settings Service

계약 데이터 공유 설정 및 동기화 로그 관련 비즈니스 로직을 처리합니다.
- 데이터 공유 설정 조회/수정
- 동기화 로그 조회

Phase 30: 레이어 분리 - db.session 제거, Repository 패턴 적용
"""
from typing import Dict, Optional, List, Any

from app.shared.base import ServiceResult


class ContractSettingsService:
    """계약 설정 서비스

    Phase 30: Repository DI 패턴 적용
    """

    def __init__(self):
        self._contract_repo = None
        self._data_sharing_repo = None
        self._sync_log_repo = None

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        if self._contract_repo is None:
            from app.extensions import person_contract_repo
            self._contract_repo = person_contract_repo
        return self._contract_repo

    @property
    def data_sharing_repo(self):
        """지연 초기화된 DataSharingSettings Repository"""
        if self._data_sharing_repo is None:
            from app.domains.company.repositories.data_sharing_settings_repository import data_sharing_settings_repository
            self._data_sharing_repo = data_sharing_settings_repository
        return self._data_sharing_repo

    @property
    def sync_log_repo(self):
        """지연 초기화된 SyncLog Repository"""
        if self._sync_log_repo is None:
            from app.domains.sync.repositories.sync_log_repository import sync_log_repository
            self._sync_log_repo = sync_log_repository
        return self._sync_log_repo

    # ========================================
    # 데이터 공유 설정
    # ========================================

    def get_sharing_settings(self, contract_id: int) -> Dict:
        """데이터 공유 설정 조회"""
        return self.contract_repo.get_sharing_settings(contract_id)

    def get_sharing_settings_model(self, contract_id: int) -> Optional[Any]:
        """데이터 공유 설정 모델 조회

        Phase 30: Repository 패턴 적용

        Args:
            contract_id: 계약 ID

        Returns:
            DataSharingSettings 모델 또는 None
        """
        return self.data_sharing_repo.find_by_contract_id(contract_id)

    def update_or_create_sharing_settings(
        self, contract_id: int, commit: bool = True, **kwargs
    ) -> Any:
        """데이터 공유 설정 생성 또는 업데이트

        Phase 30: Repository 패턴 적용

        Args:
            contract_id: 계약 ID
            commit: 트랜잭션 커밋 여부 (atomic_transaction 내에서는 False)
            **kwargs: 업데이트할 필드 (share_basic_info, is_realtime_sync 등)

        Returns:
            DataSharingSettings 모델
        """
        return self.data_sharing_repo.update_settings(contract_id, kwargs, commit=commit)

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

        Phase 30: Repository 패턴 적용

        Args:
            contract_id: 계약 ID
            sync_type: 동기화 유형 필터 (선택)
            limit: 최대 조회 수

        Returns:
            로그 목록 (Dict)
        """
        if sync_type:
            logs = self.sync_log_repo.find_by_sync_type(contract_id, sync_type, limit)
        else:
            logs = self.sync_log_repo.find_by_contract_id(contract_id, limit)
        return [log.to_dict() for log in logs]

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        """동기화 로그 조회"""
        return self.contract_repo.get_sync_logs(contract_id, limit)


# 싱글톤 인스턴스
contract_settings_service = ContractSettingsService()
