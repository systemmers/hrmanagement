"""
DataSharingSettings Repository

데이터 공유 설정의 CRUD 및 조회를 처리합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Phase 30: 레이어 분리 - Service의 Model.query 직접 사용 제거
"""
from typing import Optional, Dict, Any
from app.database import db
from app.domains.contract.models import DataSharingSettings
from app.shared.repositories.base_repository import BaseRepository


class DataSharingSettingsRepository(BaseRepository[DataSharingSettings]):
    """데이터 공유 설정 Repository"""

    def __init__(self):
        super().__init__(DataSharingSettings)

    def find_by_contract_id(self, contract_id: int) -> Optional[DataSharingSettings]:
        """계약 ID로 데이터 공유 설정 조회

        Args:
            contract_id: 계약 ID

        Returns:
            DataSharingSettings 또는 None
        """
        return DataSharingSettings.query.filter_by(contract_id=contract_id).first()

    def create_for_contract(
        self,
        contract_id: int,
        settings: Dict[str, Any] = None,
        commit: bool = True
    ) -> DataSharingSettings:
        """계약에 대한 데이터 공유 설정 생성

        Args:
            contract_id: 계약 ID
            settings: 초기 설정 값 (선택)
            commit: True면 즉시 커밋

        Returns:
            생성된 DataSharingSettings 모델
        """
        data = {'contract_id': contract_id}
        if settings:
            data.update(settings)

        sharing = DataSharingSettings(**data)
        db.session.add(sharing)
        if commit:
            db.session.commit()
        return sharing

    def update_settings(
        self,
        contract_id: int,
        settings: Dict[str, Any],
        commit: bool = True
    ) -> Optional[DataSharingSettings]:
        """데이터 공유 설정 업데이트 (upsert)

        Args:
            contract_id: 계약 ID
            settings: 업데이트할 설정 값
            commit: True면 즉시 커밋

        Returns:
            업데이트된 DataSharingSettings 또는 None
        """
        sharing = self.find_by_contract_id(contract_id)

        if not sharing:
            # 새로 생성
            return self.create_for_contract(contract_id, settings, commit)

        # 기존 레코드 업데이트
        for key, value in settings.items():
            if hasattr(sharing, key):
                setattr(sharing, key, value)

        if commit:
            db.session.commit()
        return sharing

    def is_realtime_sync_enabled(self, contract_id: int) -> bool:
        """실시간 동기화 활성화 여부 확인

        Args:
            contract_id: 계약 ID

        Returns:
            실시간 동기화 활성화 여부
        """
        settings = self.find_by_contract_id(contract_id)
        return settings.is_realtime_sync if settings else False

    def delete_by_contract_id(self, contract_id: int, commit: bool = True) -> bool:
        """계약 ID로 설정 삭제

        Args:
            contract_id: 계약 ID
            commit: True면 즉시 커밋

        Returns:
            삭제 성공 여부
        """
        settings = self.find_by_contract_id(contract_id)
        if settings:
            db.session.delete(settings)
            if commit:
                db.session.commit()
            return True
        return False


# 싱글톤 인스턴스
data_sharing_settings_repository = DataSharingSettingsRepository()
