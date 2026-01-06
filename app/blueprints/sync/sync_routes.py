"""
동기화 실행 라우트

개인-법인 데이터 동기화 API 라우트를 정의합니다.
"""
from flask import request, session

from app.blueprints.sync import sync_bp
from app.shared.constants.session_keys import SessionKeys
from app.services.sync_service import sync_service
from app.services.contract_service import contract_service
from app.shared.utils.transaction import atomic_transaction
from app.models.person_contract import SyncLog, PersonCorporateContract
from app.shared.constants.status import ContractStatus
from app.shared.utils.decorators import (
    api_login_required as login_required,
    api_personal_account_required as personal_account_required,
    api_corporate_account_required as corporate_account_required,
    contract_access_required
)
from app.shared.utils.api_helpers import api_success, api_error, api_not_found


@sync_bp.route('/fields/<int:contract_id>', methods=['GET'])
@login_required
@contract_access_required
def get_syncable_fields(contract_id):
    """
    동기화 가능 필드 목록 조회

    Response:
    {
        "success": true,
        "fields": {
            "basic": ["name", "photo", ...],
            "contact": ["email", "phone", ...],
            "education": true/false,
            ...
        }
    }
    """
    fields = sync_service.get_syncable_fields(contract_id)
    return api_success({'fields': fields})


@sync_bp.route('/personal-to-employee/<int:contract_id>', methods=['POST'])
@login_required
@personal_account_required
@contract_access_required
def sync_personal_to_employee(contract_id):
    """
    개인 -> 법인 동기화 실행 (수동)

    Request Body:
    {
        "fields": ["name", "email", ...] // 선택, 미지정 시 설정에 따라 전체
    }

    Response:
    {
        "success": true,
        "synced_fields": [...],
        "changes": [{"field": "name", "old_value": "...", "new_value": "..."}, ...],
        "logs": [1, 2, 3]
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    sync_service.set_current_user(user_id)

    data = request.get_json() or {}
    fields = data.get('fields')

    result = sync_service.sync_personal_to_employee(
        contract_id=contract_id,
        fields=fields,
        sync_type=SyncLog.SYNC_TYPE_MANUAL
    )

    if result.get('success'):
        return api_success(result)
    else:
        return api_error(result.get('error', '동기화 실패'))


@sync_bp.route('/employee-to-personal/<int:contract_id>', methods=['POST'])
@login_required
@corporate_account_required
@contract_access_required
def sync_employee_to_personal(contract_id):
    """
    법인 -> 개인 동기화 실행 (역방향, 선택적)

    Request Body:
    {
        "fields": ["name", "email", ...] // 필수
    }

    Response:
    동기화 결과
    """
    user_id = session.get(SessionKeys.USER_ID)
    sync_service.set_current_user(user_id)

    data = request.get_json() or {}
    fields = data.get('fields')

    if not fields:
        return api_error('동기화할 필드를 지정해야 합니다.')

    result = sync_service.sync_employee_to_personal(
        contract_id=contract_id,
        fields=fields,
        sync_type=SyncLog.SYNC_TYPE_MANUAL
    )

    if result.get('success'):
        return api_success(result)
    else:
        return api_error(result.get('error', '동기화 실패'))


@sync_bp.route('/full-sync/<int:contract_id>', methods=['POST'])
@login_required
@corporate_account_required
@contract_access_required
def full_sync_from_corporate(contract_id):
    """
    법인 관리자용 전체 동기화

    기존 계약에 대해 DataSharingSettings를 전체 True로 설정하고
    모든 데이터를 동기화합니다.

    Response:
    {
        "success": true,
        "synced_fields": [...],
        "changes": [...],
        "relations": [...]
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    sync_service.set_current_user(user_id)

    # 계약 확인
    contract = contract_service.get_contract_model_by_id(contract_id)
    if not contract:
        return api_not_found('계약')

    if contract.status != ContractStatus.APPROVED:
        return api_error('승인된 계약만 동기화할 수 있습니다.')

    try:
        with atomic_transaction():
            # DataSharingSettings 생성 또는 업데이트 (전체 공유)
            # Phase 2: db.session 직접 사용 제거 - Service 메서드 사용
            contract_service.update_or_create_sharing_settings(
                contract_id,
                commit=False,
                share_basic_info=True,
                share_contact=True,
                share_education=True,
                share_career=True,
                share_certificates=True,
                share_languages=True,
                share_military=True
            )

            # 전체 동기화 실행
            result = sync_service.sync_personal_to_employee(
                contract_id=contract_id,
                sync_type=SyncLog.SYNC_TYPE_MANUAL,
                commit=False  # Phase 30: 외부 트랜잭션에 위임
            )

            if not result.get('success'):
                raise Exception(result.get('error', '동기화 실패'))

        return api_success(result)

    except Exception as e:
        return api_error(str(e))


@sync_bp.route('/all-contracts', methods=['POST'])
@login_required
@personal_account_required
def sync_all_contracts():
    """
    내 모든 활성 계약 동기화 (개인용)

    실시간 동기화가 활성화된 계약만 처리됩니다.

    Response:
    {
        "success": true,
        "total_contracts": 3,
        "synced_contracts": 2,
        "results": [...]
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    sync_service.set_current_user(user_id)

    result = sync_service.sync_all_contracts_for_user(
        user_id=user_id,
        sync_type=SyncLog.SYNC_TYPE_MANUAL
    )

    return api_success(result)


@sync_bp.route('/field-mappings', methods=['GET'])
@login_required
def get_field_mappings():
    """
    필드 매핑 정보 조회 (개발/디버깅용)

    Response:
    {
        "success": true,
        "mappings": {
            "basic": {...},
            "contact": {...},
            "extra": {...}
        }
    }
    """
    mappings = sync_service.get_all_field_mappings()
    return api_success({'mappings': mappings})
