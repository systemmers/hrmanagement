"""
스냅샷 동기화 서비스

1회성 데이터 제공을 위한 스냅샷 생성 및 적용을 담당합니다.
"""
from typing import Dict, Any, Optional
from datetime import datetime
import json

from app.database import db
from app.models.employee import Employee
from app.models.personal_profile import PersonalProfile
from app.models.person_contract import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog
)


class SyncSnapshotService:
    """스냅샷 기반 동기화 처리"""

    def __init__(self, current_user_id: int = None):
        self._current_user_id = current_user_id

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정"""
        self._current_user_id = user_id

    def get_snapshot(
        self,
        contract_id: int,
        syncable: Dict,
        include_relations: bool = True
    ) -> Dict[str, Any]:
        """
        계약 기준 개인 프로필 스냅샷 생성 (1회성 제공용)

        데이터 공유 설정에 따라 허용된 데이터만 포함합니다.

        Args:
            contract_id: 계약 ID
            syncable: get_syncable_fields() 결과
            include_relations: 관계 데이터 포함 여부

        Returns:
            스냅샷 데이터
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 조회할 수 있습니다.'}

        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

        if not profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        # 기본 데이터 수집
        snapshot = {
            'snapshot_at': datetime.utcnow().isoformat(),
            'contract_id': contract_id,
            'data': {}
        }

        # 기본 정보
        if syncable['basic']:
            snapshot['data']['basic'] = {}
            for field in syncable['basic']:
                snapshot['data']['basic'][field] = getattr(profile, field, None)

        # 연락처 정보
        if syncable['contact']:
            snapshot['data']['contact'] = {}
            for field in syncable['contact']:
                snapshot['data']['contact'][field] = getattr(profile, field, None)

        # 관계 데이터
        if include_relations:
            if syncable.get('education'):
                snapshot['data']['educations'] = [
                    e.to_dict() for e in profile.educations.all()
                ]

            if syncable.get('career'):
                snapshot['data']['careers'] = [
                    c.to_dict() for c in profile.careers.all()
                ]

            if syncable.get('certificates'):
                snapshot['data']['certificates'] = [
                    c.to_dict() for c in profile.certificates.all()
                ]

            if syncable.get('languages'):
                snapshot['data']['languages'] = [
                    l.to_dict() for l in profile.languages.all()
                ]

            if syncable.get('military') and profile.military_service:
                snapshot['data']['military_service'] = profile.military_service.to_dict()

        # 스냅샷 생성 로그
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=SyncLog.SYNC_TYPE_MANUAL,
            entity_type='snapshot',
            field_name=None,
            old_value=None,
            new_value=json.dumps(list(snapshot['data'].keys())),
            direction='personal_to_company',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        snapshot['success'] = True
        return snapshot

    def apply_snapshot_to_employee(
        self,
        contract_id: int,
        snapshot_data: Dict[str, Any],
        employee: Employee,
        field_mapper: callable
    ) -> Dict[str, Any]:
        """
        스냅샷 데이터를 직원 정보에 적용 (1회성 제공)

        Args:
            contract_id: 계약 ID
            snapshot_data: get_snapshot()으로 생성된 스냅샷
            employee: 대상 직원 객체
            field_mapper: 필드 매핑 함수

        Returns:
            적용 결과
        """
        data = snapshot_data.get('data', {})
        changes = []

        # 기본 정보 적용
        basic_data = data.get('basic', {})
        for field, value in basic_data.items():
            emp_field = field_mapper(field)
            if emp_field:
                old_value = getattr(employee, emp_field, None)
                if old_value != value:
                    setattr(employee, emp_field, value)
                    changes.append({
                        'field': field,
                        'old_value': self._serialize_value(old_value),
                        'new_value': self._serialize_value(value)
                    })

        # 연락처 정보 적용
        contact_data = data.get('contact', {})
        for field, value in contact_data.items():
            emp_field = field_mapper(field)
            if emp_field:
                old_value = getattr(employee, emp_field, None)
                if old_value != value:
                    setattr(employee, emp_field, value)
                    changes.append({
                        'field': field,
                        'old_value': self._serialize_value(old_value),
                        'new_value': self._serialize_value(value)
                    })

        # 적용 로그
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=SyncLog.SYNC_TYPE_MANUAL,
            entity_type='snapshot_apply',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'changed_fields': len(changes)}),
            direction='snapshot_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        return {
            'success': True,
            'changes': changes,
            'employee_id': employee.id
        }

    def _serialize_value(self, value: Any) -> Optional[str]:
        """값을 문자열로 직렬화 (로그용)"""
        if value is None:
            return None
        if isinstance(value, datetime):
            return value.isoformat()
        return str(value)
