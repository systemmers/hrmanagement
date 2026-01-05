"""
기본 필드 동기화 서비스

개인 프로필 <-> 직원 간 기본 필드 동기화를 담당합니다.

Phase 30: 레이어 분리 - db.session 제거, Repository 패턴 적용
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.models.employee import Employee
from app.models.personal_profile import PersonalProfile
from app.models.person_contract import (
    PersonCorporateContract,
    SyncLog
)


class SyncBasicService:
    """기본 필드 동기화 처리

    Phase 30: Repository DI 패턴 적용
    """

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id
        self._sync_log_repo = None

    # ========================================
    # Repository Properties (지연 초기화)
    # ========================================

    @property
    def sync_log_repo(self):
        """지연 초기화된 SyncLog Repository"""
        if self._sync_log_repo is None:
            from app.repositories.sync_log_repository import sync_log_repository
            self._sync_log_repo = sync_log_repository
        return self._sync_log_repo

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정"""
        self._current_user_id = user_id

    def sync_personal_to_employee(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        target_fields: List[str],
        field_mapper: callable,
        sync_type: str = SyncLog.SYNC_TYPE_AUTO
    ) -> Dict[str, Any]:
        """
        개인 프로필 -> 법인 직원 기본 필드 동기화

        Args:
            contract_id: 계약 ID
            profile: 개인 프로필
            employee: 직원 객체
            target_fields: 동기화할 필드 목록
            field_mapper: 필드 매핑 함수
            sync_type: 동기화 유형

        Returns:
            동기화 결과 {'synced_fields': [], 'changes': [], 'log_ids': []}
        """
        changes = []
        synced_fields = []
        log_ids = []

        for field in target_fields:
            employee_field = field_mapper(field)
            if not employee_field:
                continue

            old_value = getattr(employee, employee_field, None)
            new_value = getattr(profile, field, None)

            if old_value != new_value:
                setattr(employee, employee_field, new_value)

                change = {
                    'field': field,
                    'old_value': self._serialize_value(old_value),
                    'new_value': self._serialize_value(new_value),
                }
                changes.append(change)
                synced_fields.append(field)

                # Phase 30: Repository 패턴 적용
                log = self.sync_log_repo.create_log(
                    contract_id=contract_id,
                    sync_type=sync_type,
                    entity_type='personal_profile',
                    field_name=field,
                    old_value=change['old_value'],
                    new_value=change['new_value'],
                    direction='personal_to_employee',
                    user_id=self._current_user_id,
                    commit=False
                )
                log_ids.append(log.id)

        return {
            'synced_fields': synced_fields,
            'changes': changes,
            'log_ids': log_ids
        }

    def sync_employee_to_personal(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        target_fields: List[str],
        field_mapper: callable,
        sync_type: str = SyncLog.SYNC_TYPE_MANUAL
    ) -> Dict[str, Any]:
        """
        법인 직원 -> 개인 프로필 기본 필드 동기화 (역방향)

        Args:
            contract_id: 계약 ID
            profile: 개인 프로필
            employee: 직원 객체
            target_fields: 동기화할 필드 목록
            field_mapper: 필드 매핑 함수
            sync_type: 동기화 유형

        Returns:
            동기화 결과
        """
        changes = []
        synced_fields = []
        log_ids = []

        for field in target_fields:
            employee_field = field_mapper(field)
            if not employee_field:
                continue

            old_value = getattr(profile, field, None)
            new_value = getattr(employee, employee_field, None)

            if old_value != new_value:
                setattr(profile, field, new_value)

                change = {
                    'field': field,
                    'old_value': self._serialize_value(old_value),
                    'new_value': self._serialize_value(new_value),
                }
                changes.append(change)
                synced_fields.append(field)

                # Phase 30: Repository 패턴 적용
                log = self.sync_log_repo.create_log(
                    contract_id=contract_id,
                    sync_type=sync_type,
                    entity_type='employee',
                    field_name=field,
                    old_value=change['old_value'],
                    new_value=change['new_value'],
                    direction='employee_to_personal',
                    user_id=self._current_user_id,
                    commit=False
                )
                log_ids.append(log.id)

        return {
            'synced_fields': synced_fields,
            'changes': changes,
            'log_ids': log_ids
        }

    def _serialize_value(self, value: Any) -> Optional[str]:
        """값을 JSON 직렬화 가능한 문자열로 변환"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return json.dumps(value)
