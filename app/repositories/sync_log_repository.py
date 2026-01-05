"""
SyncLog Repository

동기화 로그의 CRUD 및 조회를 처리합니다.

Phase 30: 레이어 분리 - Service의 Model.query 직접 사용 제거
"""
from typing import Optional, List, Any
from app.database import db
from app.models.person_contract import SyncLog
from .base_repository import BaseRepository


class SyncLogRepository(BaseRepository[SyncLog]):
    """동기화 로그 Repository"""

    def __init__(self):
        super().__init__(SyncLog)

    def find_by_contract_id(
        self,
        contract_id: int,
        limit: int = 50
    ) -> List[SyncLog]:
        """계약 ID로 동기화 로그 조회 (최신순)

        Args:
            contract_id: 계약 ID
            limit: 최대 조회 건수

        Returns:
            SyncLog 목록
        """
        return SyncLog.query.filter_by(
            contract_id=contract_id
        ).order_by(SyncLog.executed_at.desc()).limit(limit).all()

    def create_log(
        self,
        contract_id: int,
        sync_type: str,
        entity_type: str,
        field_name: str = None,
        old_value: Any = None,
        new_value: Any = None,
        direction: str = None,
        user_id: int = None,
        commit: bool = True,
        flush: bool = True
    ) -> SyncLog:
        """동기화 로그 생성

        Phase 30: flush 옵션 추가 (ID 할당 필요 시)

        Args:
            contract_id: 계약 ID
            sync_type: 동기화 유형 (auto, manual, initial)
            entity_type: 엔티티 유형
            field_name: 필드명 (선택)
            old_value: 이전 값 (선택)
            new_value: 새 값 (선택)
            direction: 동기화 방향 (선택)
            user_id: 실행자 ID (선택)
            commit: True면 즉시 커밋
            flush: True면 flush 실행 (ID 할당)

        Returns:
            생성된 SyncLog 모델
        """
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type=entity_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            direction=direction,
            user_id=user_id
        )
        db.session.add(log)
        if commit:
            db.session.commit()
        elif flush:
            db.session.flush()
        return log

    def find_by_entity_type(
        self,
        contract_id: int,
        entity_type: str,
        limit: int = 50
    ) -> List[SyncLog]:
        """계약 ID와 엔티티 유형으로 로그 조회

        Args:
            contract_id: 계약 ID
            entity_type: 엔티티 유형
            limit: 최대 조회 건수

        Returns:
            SyncLog 목록
        """
        return SyncLog.query.filter_by(
            contract_id=contract_id,
            entity_type=entity_type
        ).order_by(SyncLog.executed_at.desc()).limit(limit).all()

    def find_by_sync_type(
        self,
        contract_id: int,
        sync_type: str,
        limit: int = 50
    ) -> List[SyncLog]:
        """계약 ID와 동기화 유형으로 로그 조회

        Args:
            contract_id: 계약 ID
            sync_type: 동기화 유형
            limit: 최대 조회 건수

        Returns:
            SyncLog 목록
        """
        return SyncLog.query.filter_by(
            contract_id=contract_id,
            sync_type=sync_type
        ).order_by(SyncLog.executed_at.desc()).limit(limit).all()

    def count_by_contract_id(self, contract_id: int) -> int:
        """계약별 로그 건수 조회

        Args:
            contract_id: 계약 ID

        Returns:
            로그 건수
        """
        return SyncLog.query.filter_by(contract_id=contract_id).count()

    def delete_by_contract_id(self, contract_id: int, commit: bool = True) -> int:
        """계약 ID로 모든 로그 삭제

        Args:
            contract_id: 계약 ID
            commit: True면 즉시 커밋

        Returns:
            삭제된 로그 건수
        """
        count = SyncLog.query.filter_by(contract_id=contract_id).delete()
        if commit:
            db.session.commit()
        return count


# 싱글톤 인스턴스
sync_log_repository = SyncLogRepository()
