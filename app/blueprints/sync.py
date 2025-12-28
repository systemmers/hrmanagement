"""
동기화 API Blueprint

개인-법인 데이터 동기화 API를 제공합니다.
Phase 4: 데이터 동기화 및 퇴사 처리
Phase 8: 상수 모듈 적용
Phase 24: 트랜잭션 SSOT 적용
"""
from flask import Blueprint, request, session

from app.constants.session_keys import SessionKeys, AccountType
from app.services.sync_service import sync_service
from app.services.contract_service import contract_service
from app.utils.transaction import atomic_transaction
from app.services.termination_service import termination_service
from app.models.person_contract import DataSharingSettings
from app.utils.decorators import (
    api_login_required as login_required,
    api_personal_account_required as personal_account_required,
    api_corporate_account_required as corporate_account_required,
    contract_access_required
)
from app.utils.api_helpers import api_success, api_error, api_not_found

sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')


# ===== 동기화 API =====

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
    from app.database import db
    from app.models.person_contract import PersonCorporateContract

    user_id = session.get(SessionKeys.USER_ID)
    sync_service.set_current_user(user_id)

    # 계약 확인
    contract = contract_service.get_contract_model_by_id(contract_id)
    if not contract:
        return api_not_found('계약')

    if contract.status != PersonCorporateContract.STATUS_APPROVED:
        return api_error('승인된 계약만 동기화할 수 있습니다.')

    try:
        with atomic_transaction():
            # DataSharingSettings 생성 또는 업데이트 (전체 공유)
            settings = contract_service.get_sharing_settings_model(contract_id)
            if not settings:
                settings = DataSharingSettings(contract_id=contract_id)
                db.session.add(settings)

            # 모든 공유 설정을 True로
            settings.share_basic_info = True
            settings.share_contact = True
            settings.share_education = True
            settings.share_career = True
            settings.share_certificates = True
            settings.share_languages = True
            settings.share_military = True
            db.session.flush()

            # 전체 동기화 실행
            result = sync_service.sync_personal_to_employee(
                contract_id=contract_id,
                sync_type=SyncLog.SYNC_TYPE_MANUAL
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


# ===== 계약 목록 API =====

@sync_bp.route('/contracts', methods=['GET'])
@login_required
@personal_account_required
def get_my_contracts():
    """
    내 활성 계약 목록 조회 (동기화 대상)

    Response:
    {
        "success": true,
        "contracts": [...]
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    contracts = sync_service.get_contracts_for_user(user_id)
    return api_success({'contracts': contracts})


# ===== 동기화 설정 API =====

@sync_bp.route('/settings/<int:contract_id>/realtime', methods=['PUT'])
@login_required
@personal_account_required
@contract_access_required
def toggle_realtime_sync(contract_id):
    """
    실시간 동기화 설정 변경 (개인만 가능)

    Request Body:
    {
        "enabled": true/false
    }

    Response:
    {
        "success": true,
        "realtime_sync": true/false
    }
    """
    from app.database import db

    data = request.get_json() or {}
    enabled = data.get('enabled', False)

    with atomic_transaction():
        settings = contract_service.get_sharing_settings_model(contract_id)
        if not settings:
            settings = DataSharingSettings(contract_id=contract_id)
            db.session.add(settings)

        settings.is_realtime_sync = enabled

    return api_success({'realtime_sync': settings.is_realtime_sync})


# ===== 퇴사/종료 처리 API =====

@sync_bp.route('/terminate/<int:contract_id>', methods=['POST'])
@login_required
@contract_access_required
def terminate_contract(contract_id):
    """
    계약 종료 처리

    Request Body:
    {
        "reason": "퇴사 사유 (선택)"
    }

    Response:
    {
        "success": true,
        "contract_id": 1,
        "terminated_at": "...",
        "revoked_permissions": {...},
        "archive_scheduled": {...}
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    termination_service.set_current_user(user_id)

    data = request.get_json() or {}
    reason = data.get('reason')

    result = termination_service.terminate_contract(
        contract_id=contract_id,
        reason=reason,
        terminate_by_user_id=user_id
    )

    if result.get('success'):
        return api_success(result)
    else:
        return api_error(result.get('error', '계약 종료 실패'))


@sync_bp.route('/retention/<int:contract_id>', methods=['GET'])
@login_required
@contract_access_required
def get_retention_status(contract_id):
    """
    데이터 보관 상태 조회

    Response:
    {
        "success": true,
        "status": "pending/archived/deleted",
        "terminated_at": "...",
        "retention_end": "...",
        "days_remaining": 1095
    }
    """
    result = termination_service.get_retention_status(contract_id)

    if result.get('success'):
        return api_success(result)
    else:
        return api_error(result.get('error', '보관 상태 조회 실패'))


@sync_bp.route('/termination-history', methods=['GET'])
@login_required
def get_termination_history():
    """
    종료된 계약 이력 조회

    Query Params:
    - limit: 조회 제한 (기본 50)

    Response:
    {
        "success": true,
        "contracts": [...]
    }
    """
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)
    user_id = session.get(SessionKeys.USER_ID)
    company_id = session.get(SessionKeys.COMPANY_ID)

    limit = request.args.get('limit', 50, type=int)

    if account_type == AccountType.PERSONAL:
        history = termination_service.get_termination_history(
            person_user_id=user_id,
            limit=limit
        )
    elif account_type == AccountType.CORPORATE:
        history = termination_service.get_termination_history(
            company_id=company_id,
            limit=limit
        )
    else:
        return api_error('잘못된 계정 유형입니다.')

    return api_success({'contracts': history})


# ===== 동기화 로그 API =====

@sync_bp.route('/logs/<int:contract_id>', methods=['GET'])
@login_required
@contract_access_required
def get_sync_logs(contract_id):
    """
    동기화 로그 조회

    Query Params:
    - limit: 조회 제한 (기본 50)
    - sync_type: 동기화 유형 필터 (auto, manual, initial)

    Response:
    {
        "success": true,
        "logs": [...]
    }
    """
    limit = request.args.get('limit', 50, type=int)
    sync_type = request.args.get('sync_type')

    logs = contract_service.get_sync_logs_filtered(
        contract_id, sync_type=sync_type, limit=limit
    )

    return api_success({'logs': logs})


# ===== 필드 매핑 정보 API =====

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
