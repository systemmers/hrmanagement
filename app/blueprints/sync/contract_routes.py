"""
계약 및 설정 라우트

계약 목록 조회 및 동기화 설정 관련 API 라우트를 정의합니다.
"""
from flask import request, session

from app.blueprints.sync import sync_bp
from app.constants.session_keys import SessionKeys
from app.services.sync_service import sync_service
from app.services.contract_service import contract_service
from app.utils.transaction import atomic_transaction
from app.utils.decorators import (
    api_login_required as login_required,
    api_personal_account_required as personal_account_required,
    contract_access_required
)
from app.utils.api_helpers import api_success


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
    data = request.get_json() or {}
    enabled = data.get('enabled', False)

    with atomic_transaction():
        settings = contract_service.update_or_create_sharing_settings(
            contract_id, commit=False, is_realtime_sync=enabled
        )

    return api_success({'realtime_sync': settings.is_realtime_sync})


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
