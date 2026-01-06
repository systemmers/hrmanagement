"""
퇴사/종료 처리 라우트

계약 종료 및 데이터 보관 관련 API 라우트를 정의합니다.

Phase 5.3: 양측 동의 계약 종료 API 추가
Phase 7: 도메인 중심 마이그레이션 (app/domains/sync/blueprints/)
"""
from flask import request, session

from app.domains.sync.blueprints import sync_bp
from app.shared.constants.session_keys import SessionKeys, AccountType
from app.services.termination_service import termination_service
from app.services.contract_service import contract_service
from app.shared.utils.decorators import (
    api_login_required as login_required,
    contract_access_required
)
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden


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


# ========================================
# 양측 동의 계약 종료 API (Phase 5.3)
# ========================================

@sync_bp.route('/contracts/<int:contract_id>/request-termination', methods=['POST'])
@login_required
@contract_access_required
def request_termination(contract_id):
    """
    계약 종료 요청 (양측 동의 프로세스 시작)

    개인 또는 법인 어느 쪽이든 종료 요청 가능.
    상대방이 승인해야 최종 종료됨.

    Request Body:
    {
        "reason": "종료 요청 사유 (선택)"
    }

    Response:
    {
        "success": true,
        "data": {...}  // 계약 정보
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json() or {}
    reason = data.get('reason')

    result = contract_service.request_termination(
        contract_id=contract_id,
        requester_user_id=user_id,
        reason=reason
    )

    if result:
        return api_success(result.data)
    return api_error(result.message)


@sync_bp.route('/contracts/<int:contract_id>/approve-termination', methods=['POST'])
@login_required
@contract_access_required
def approve_termination(contract_id):
    """
    계약 종료 승인 (상대방이 승인)

    종료 요청의 상대방만 승인 가능.
    승인 시 최종 계약 종료 처리.

    Response:
    {
        "success": true,
        "data": {...}  // 계약 정보
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    result = contract_service.approve_termination(
        contract_id=contract_id,
        approver_user_id=user_id
    )

    if result:
        return api_success(result.data)
    return api_error(result.message)


@sync_bp.route('/contracts/<int:contract_id>/reject-termination', methods=['POST'])
@login_required
@contract_access_required
def reject_termination(contract_id):
    """
    계약 종료 거절 (상대방이 거절)

    종료 요청의 상대방만 거절 가능.
    거절 시 계약 상태가 approved로 원복됨.

    Request Body:
    {
        "reason": "거절 사유 (선택)"
    }

    Response:
    {
        "success": true,
        "data": {...}  // 계약 정보
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json() or {}
    reason = data.get('reason')

    result = contract_service.reject_termination(
        contract_id=contract_id,
        rejector_user_id=user_id,
        reason=reason
    )

    if result:
        return api_success(result.data)
    return api_error(result.message)


@sync_bp.route('/termination-pending', methods=['GET'])
@login_required
def get_termination_pending():
    """
    종료 요청 대기 중인 계약 목록 조회

    현재 사용자가 승인/거절해야 하는 종료 요청 목록

    Response:
    {
        "success": true,
        "data": {
            "contracts": [...]
        }
    }
    """
    user_id = session.get(SessionKeys.USER_ID)

    contracts = contract_service.get_termination_pending_contracts(user_id)

    return api_success({'contracts': contracts})
