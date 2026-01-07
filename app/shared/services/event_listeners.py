"""
SQLAlchemy 이벤트 리스너

데이터 변경 시 자동 동기화를 트리거합니다.
Phase 4: 데이터 동기화 및 퇴사 처리
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from typing import Any, Set
from sqlalchemy import event
from sqlalchemy.orm import Session
from flask import current_app, has_app_context

from app.database import db
from app.domains.contract.models import DataSharingSettings, PersonCorporateContract, SyncLog
from app.domains.user.models import PersonalProfile
from app.shared.constants.status import ContractStatus


class SyncEventManager:
    """
    동기화 이벤트 관리자

    PersonalProfile 모델의 변경사항을 감지하고
    실시간 동기화가 활성화된 계약에 대해 자동 동기화를 수행합니다.
    """

    _enabled = False
    _pending_syncs: Set[int] = set()
    _contract_repo = None
    _data_sharing_repo = None

    @classmethod
    def _get_contract_repo(cls):
        """지연 초기화된 계약 Repository"""
        if cls._contract_repo is None:
            from app.domains.contract.repositories.person_contract_repository import person_contract_repository
            cls._contract_repo = person_contract_repository
        return cls._contract_repo

    @classmethod
    def _get_data_sharing_repo(cls):
        """지연 초기화된 데이터 공유 설정 Repository"""
        if cls._data_sharing_repo is None:
            from app.domains.company.repositories.data_sharing_settings_repository import data_sharing_settings_repository
            cls._data_sharing_repo = data_sharing_settings_repository
        return cls._data_sharing_repo

    @classmethod
    def enable(cls):
        """이벤트 리스너 활성화"""
        if not cls._enabled:
            cls._register_listeners()
            cls._enabled = True

    @classmethod
    def disable(cls):
        """이벤트 리스너 비활성화"""
        if cls._enabled:
            cls._unregister_listeners()
            cls._enabled = False

    @classmethod
    def is_enabled(cls) -> bool:
        """활성화 상태 확인"""
        return cls._enabled

    @classmethod
    def _register_listeners(cls):
        """이벤트 리스너 등록"""
        # PersonalProfile 변경 감지
        event.listen(PersonalProfile, 'after_update', cls._on_profile_update)
        event.listen(PersonalProfile, 'after_insert', cls._on_profile_insert)

        # 세션 커밋 후 처리
        event.listen(db.session, 'after_commit', cls._after_commit)

    @classmethod
    def _unregister_listeners(cls):
        """이벤트 리스너 해제"""
        try:
            event.remove(PersonalProfile, 'after_update', cls._on_profile_update)
            event.remove(PersonalProfile, 'after_insert', cls._on_profile_insert)
            event.remove(db.session, 'after_commit', cls._after_commit)
        except Exception:
            pass

    @classmethod
    def _on_profile_update(cls, mapper, connection, target: PersonalProfile):
        """
        PersonalProfile 업데이트 이벤트 핸들러

        Args:
            mapper: SQLAlchemy mapper
            connection: DB connection
            target: 업데이트된 PersonalProfile 인스턴스
        """
        if not cls._enabled:
            return

        # 동기화 대상으로 마킹
        cls._pending_syncs.add(target.user_id)

    @classmethod
    def _on_profile_insert(cls, mapper, connection, target: PersonalProfile):
        """
        PersonalProfile 생성 이벤트 핸들러

        새 프로필이 생성되면 기존 계약이 있는지 확인하고 초기 동기화 수행
        """
        if not cls._enabled:
            return

        cls._pending_syncs.add(target.user_id)

    @classmethod
    def _after_commit(cls, session: Session):
        """
        세션 커밋 후 동기화 실행

        트랜잭션이 성공적으로 커밋된 후에만 동기화를 수행합니다.
        """
        if not cls._pending_syncs:
            return

        user_ids = cls._pending_syncs.copy()
        cls._pending_syncs.clear()

        # 앱 컨텍스트 확인
        if not has_app_context():
            return

        for user_id in user_ids:
            try:
                cls._sync_user_contracts(user_id)
            except Exception as e:
                if current_app:
                    current_app.logger.error(
                        f"Auto sync failed for user {user_id}: {str(e)}"
                    )

    @classmethod
    def _sync_user_contracts(cls, user_id: int):
        """
        사용자의 모든 활성 계약 동기화

        Args:
            user_id: 개인 사용자 ID
        """
        # Phase 31: Repository 패턴 적용
        contracts = cls._get_contract_repo().find_by_person_user_id_and_status(
            user_id, ContractStatus.APPROVED
        )

        for contract in contracts:
            # 실시간 동기화 설정 확인
            settings = cls._get_data_sharing_repo().find_by_contract_id(contract.id)

            if settings and settings.is_realtime_sync:
                cls._execute_sync(contract.id, user_id)

    @classmethod
    def _execute_sync(cls, contract_id: int, user_id: int):
        """
        실제 동기화 실행

        Args:
            contract_id: 계약 ID
            user_id: 사용자 ID
        """
        # 순환 import 방지
        from app.domains.sync.services.sync_service import sync_service

        try:
            sync_service.set_current_user(user_id)
            result = sync_service.sync_personal_to_employee(
                contract_id=contract_id,
                sync_type=SyncLog.SYNC_TYPE_AUTO
            )

            if current_app:
                if result.get('success'):
                    current_app.logger.info(
                        f"Auto sync completed for contract {contract_id}: "
                        f"{len(result.get('changes', []))} changes"
                    )
                else:
                    current_app.logger.warning(
                        f"Auto sync failed for contract {contract_id}: "
                        f"{result.get('error')}"
                    )

        except Exception as e:
            if current_app:
                current_app.logger.error(
                    f"Auto sync error for contract {contract_id}: {str(e)}"
                )


class ContractEventManager:
    """
    계약 이벤트 관리자

    계약 상태 변경 시 관련 처리를 수행합니다.
    """

    _enabled = False
    _data_sharing_repo = None

    @classmethod
    def _get_data_sharing_repo(cls):
        """지연 초기화된 데이터 공유 설정 Repository"""
        if cls._data_sharing_repo is None:
            from app.domains.company.repositories.data_sharing_settings_repository import data_sharing_settings_repository
            cls._data_sharing_repo = data_sharing_settings_repository
        return cls._data_sharing_repo

    @classmethod
    def enable(cls):
        """이벤트 리스너 활성화"""
        if not cls._enabled:
            cls._register_listeners()
            cls._enabled = True

    @classmethod
    def disable(cls):
        """이벤트 리스너 비활성화"""
        if cls._enabled:
            cls._unregister_listeners()
            cls._enabled = False

    @classmethod
    def _register_listeners(cls):
        """이벤트 리스너 등록"""
        event.listen(PersonCorporateContract, 'after_update', cls._on_contract_update)

    @classmethod
    def _unregister_listeners(cls):
        """이벤트 리스너 해제"""
        try:
            event.remove(PersonCorporateContract, 'after_update', cls._on_contract_update)
        except Exception:
            pass

    @classmethod
    def _on_contract_update(cls, mapper, connection, target: PersonCorporateContract):
        """
        계약 업데이트 이벤트 핸들러

        - 계약 승인 시: 초기 동기화 수행
        - 계약 종료 시: 권한 해제 및 정리
        """
        if not cls._enabled:
            return

        # 상태 변경 감지
        history = db.inspect(target).attrs.status.history

        if history.has_changes():
            old_status = history.deleted[0] if history.deleted else None
            new_status = history.added[0] if history.added else None

            if old_status != new_status:
                cls._handle_status_change(target, old_status, new_status)

    @classmethod
    def _handle_status_change(
        cls,
        contract: PersonCorporateContract,
        old_status: str,
        new_status: str
    ):
        """상태 변경 처리"""
        if not has_app_context():
            return

        # 승인됨으로 변경 시
        if new_status == ContractStatus.APPROVED:
            cls._on_contract_approved(contract)

        # 종료됨으로 변경 시
        elif new_status == ContractStatus.TERMINATED:
            cls._on_contract_terminated(contract)

    @classmethod
    def _on_contract_approved(cls, contract: PersonCorporateContract):
        """
        계약 승인 시 처리

        - 기본 데이터 공유 설정 생성
        - 초기 동기화 수행
        """
        # Phase 31: Repository 패턴 적용
        repo = cls._get_data_sharing_repo()
        settings = repo.find_by_contract_id(contract.id)

        if not settings:
            # 기본값으로 생성 (commit=False로 현재 트랜잭션 유지)
            settings = repo.create_for_contract(
                contract_id=contract.id,
                settings={
                    'share_basic_info': True,
                    'share_contact': True,
                    'share_education': False,
                    'share_career': False,
                    'share_certificates': False,
                    'share_languages': False,
                    'share_military': False,
                    'is_realtime_sync': False,  # 기본값은 수동 동기화
                },
                commit=False  # 이벤트 리스너 내에서는 commit 하지 않음
            )

        if current_app:
            current_app.logger.info(
                f"Contract {contract.id} approved, sharing settings created"
            )

    @classmethod
    def _on_contract_terminated(cls, contract: PersonCorporateContract):
        """
        계약 종료 시 처리

        - 실시간 동기화 비활성화
        - 로그 기록
        """
        # Phase 31: Repository 패턴 적용
        repo = cls._get_data_sharing_repo()
        settings = repo.find_by_contract_id(contract.id)

        if settings:
            settings.is_realtime_sync = False
            # 이벤트 리스너 내에서는 commit 하지 않음 (외부 트랜잭션에서 처리)

        if current_app:
            current_app.logger.info(
                f"Contract {contract.id} terminated, realtime sync disabled"
            )


def init_event_listeners(app):
    """
    Flask 앱에 이벤트 리스너 초기화

    Args:
        app: Flask 애플리케이션
    """
    with app.app_context():
        # 환경 설정에 따라 활성화 결정
        if app.config.get('ENABLE_AUTO_SYNC', True):
            SyncEventManager.enable()
            app.logger.info("SyncEventManager enabled")

        if app.config.get('ENABLE_CONTRACT_EVENTS', True):
            ContractEventManager.enable()
            app.logger.info("ContractEventManager enabled")


def cleanup_event_listeners():
    """이벤트 리스너 정리"""
    SyncEventManager.disable()
    ContractEventManager.disable()


# 변경 감지 유틸리티
def get_model_changes(model) -> dict:
    """
    모델의 변경된 필드 목록 반환

    Args:
        model: SQLAlchemy 모델 인스턴스

    Returns:
        {field: {'old': value, 'new': value}, ...}
    """
    changes = {}
    state = db.inspect(model)

    for attr in state.attrs:
        history = attr.history
        if history.has_changes():
            changes[attr.key] = {
                'old': history.deleted[0] if history.deleted else None,
                'new': history.added[0] if history.added else None,
            }

    return changes


def track_field_changes(model, fields: list) -> dict:
    """
    특정 필드의 변경사항만 추적

    Args:
        model: SQLAlchemy 모델 인스턴스
        fields: 추적할 필드 목록

    Returns:
        변경된 필드만 포함하는 딕셔너리
    """
    all_changes = get_model_changes(model)
    return {k: v for k, v in all_changes.items() if k in fields}
