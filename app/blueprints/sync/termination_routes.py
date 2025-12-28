"""
퇴사/종료 처리 라우트

계약 종료 및 데이터 보관 관련 API 라우트를 정의합니다.
"""
from flask import request, session

from app.blueprints.sync import sync_bp
from app.constants.session_keys import SessionKeys, AccountType
from app.services.termination_service import termination_service
from app.utils.decorators import (
    api_login_required as login_required,
    contract_access_required
)
from app.utils.api_helpers import api_success, api_error


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
