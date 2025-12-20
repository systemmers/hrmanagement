"""
감사 로그 API Blueprint

감사 로그 조회 및 통계 API를 제공합니다.
Phase 4: 데이터 동기화 및 퇴사 처리
Phase 7: 데코레이터 통합 리팩토링
Phase 8: 상수 모듈 적용
"""
from datetime import datetime, timedelta
from flask import Blueprint, request, jsonify, session

from app.constants.session_keys import SessionKeys, AccountType
from app.services.audit_service import audit_service, AuditLog
from app.utils.decorators import (
    api_login_required as login_required,
    api_admin_or_manager_required as admin_required,
    api_corporate_account_required as corporate_account_required
)

audit_bp = Blueprint('audit', __name__, url_prefix='/api/audit')


# ===== 감사 로그 조회 API =====

@audit_bp.route('/logs', methods=['GET'])
@login_required
@admin_required
def get_logs():
    """
    감사 로그 조회 (관리자용)

    Query Params:
    - user_id: 사용자 ID 필터 (선택)
    - action: 액션 유형 필터 (선택)
    - resource_type: 리소스 유형 필터 (선택)
    - resource_id: 리소스 ID 필터 (선택)
    - status: 상태 필터 (선택)
    - start_date: 시작 날짜 (ISO format, 선택)
    - end_date: 종료 날짜 (ISO format, 선택)
    - limit: 조회 제한 (기본 100)
    - offset: 오프셋 (기본 0)

    Response:
    {
        "success": true,
        "logs": [...],
        "total": 150,
        "limit": 100,
        "offset": 0
    }
    """
    # 법인 계정인 경우 자사 로그만 조회
    company_id = session.get(SessionKeys.COMPANY_ID) if session.get(SessionKeys.ACCOUNT_TYPE) == AccountType.CORPORATE else None

    # 필터 파라미터
    user_id = request.args.get('user_id', type=int)
    action = request.args.get('action')
    resource_type = request.args.get('resource_type')
    resource_id = request.args.get('resource_id', type=int)
    status = request.args.get('status')
    limit = request.args.get('limit', 100, type=int)
    offset = request.args.get('offset', 0, type=int)

    # 날짜 파싱
    start_date = None
    end_date = None
    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        except ValueError:
            pass
    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        except ValueError:
            pass

    logs = audit_service.get_logs(
        user_id=user_id,
        company_id=company_id,
        action=action,
        resource_type=resource_type,
        resource_id=resource_id,
        status=status,
        start_date=start_date,
        end_date=end_date,
        limit=limit,
        offset=offset
    )

    # 전체 개수 (페이지네이션용)
    total_query = AuditLog.query
    if company_id:
        total_query = total_query.filter_by(company_id=company_id)
    if user_id:
        total_query = total_query.filter_by(user_id=user_id)
    if action:
        total_query = total_query.filter_by(action=action)
    if resource_type:
        total_query = total_query.filter_by(resource_type=resource_type)
    total = total_query.count()

    return jsonify({
        'success': True,
        'logs': logs,
        'total': total,
        'limit': limit,
        'offset': offset
    })


@audit_bp.route('/logs/resource/<resource_type>/<int:resource_id>', methods=['GET'])
@login_required
@admin_required
def get_resource_logs(resource_type, resource_id):
    """
    특정 리소스의 감사 로그 조회

    Response:
    {
        "success": true,
        "logs": [...],
        "access_summary": {...}
    }
    """
    limit = request.args.get('limit', 50, type=int)

    logs = audit_service.get_logs_for_resource(
        resource_type=resource_type,
        resource_id=resource_id,
        limit=limit
    )

    # 접근 요약
    summary = audit_service.get_access_summary(
        resource_type=resource_type,
        resource_id=resource_id
    )

    return jsonify({
        'success': True,
        'logs': logs,
        'access_summary': summary
    })


@audit_bp.route('/logs/user/<int:user_id>', methods=['GET'])
@login_required
@admin_required
def get_user_logs(user_id):
    """
    특정 사용자의 활동 로그 조회

    Query Params:
    - days: 조회 기간 (기본 30일)

    Response:
    {
        "success": true,
        "logs": [...],
        "user_id": 123,
        "period_days": 30
    }
    """
    days = request.args.get('days', 30, type=int)

    logs = audit_service.get_user_activity(user_id=user_id, days=days)

    return jsonify({
        'success': True,
        'logs': logs,
        'user_id': user_id,
        'period_days': days
    })


@audit_bp.route('/logs/my', methods=['GET'])
@login_required
def get_my_logs():
    """
    내 활동 로그 조회 (일반 사용자용)

    Query Params:
    - days: 조회 기간 (기본 30일)
    - limit: 조회 제한 (기본 50)

    Response:
    {
        "success": true,
        "logs": [...],
        "period_days": 30
    }
    """
    user_id = session.get(SessionKeys.USER_ID)
    days = request.args.get('days', 30, type=int)
    limit = request.args.get('limit', 50, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)
    logs = audit_service.get_logs(
        user_id=user_id,
        start_date=start_date,
        limit=limit
    )

    return jsonify({
        'success': True,
        'logs': logs,
        'period_days': days
    })


# ===== 통계 API =====

@audit_bp.route('/stats', methods=['GET'])
@login_required
@admin_required
def get_statistics():
    """
    감사 로그 통계 (관리자용)

    Query Params:
    - start_date: 시작 날짜 (ISO format, 선택)
    - end_date: 종료 날짜 (ISO format, 선택)
    - days: start_date 미지정 시 최근 일수 (기본 30)

    Response:
    {
        "success": true,
        "stats": {
            "total": 1000,
            "by_action": {...},
            "by_resource": {...},
            "by_status": {...}
        },
        "period": {...}
    }
    """
    company_id = session.get(SessionKeys.COMPANY_ID) if session.get(SessionKeys.ACCOUNT_TYPE) == AccountType.CORPORATE else None

    days = request.args.get('days', 30, type=int)
    start_date = None
    end_date = None

    if request.args.get('start_date'):
        try:
            start_date = datetime.fromisoformat(request.args.get('start_date'))
        except ValueError:
            pass
    else:
        start_date = datetime.utcnow() - timedelta(days=days)

    if request.args.get('end_date'):
        try:
            end_date = datetime.fromisoformat(request.args.get('end_date'))
        except ValueError:
            pass

    stats = audit_service.get_statistics(
        company_id=company_id,
        start_date=start_date,
        end_date=end_date
    )

    return jsonify({
        'success': True,
        'stats': stats,
        'period': {
            'start_date': start_date.isoformat() if start_date else None,
            'end_date': end_date.isoformat() if end_date else None,
        }
    })


@audit_bp.route('/stats/company', methods=['GET'])
@login_required
@corporate_account_required
@admin_required
def get_company_statistics():
    """
    법인 감사 통계

    Response:
    {
        "success": true,
        "stats": {...},
        "audit_trail": [...],
        "period_days": 30
    }
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    days = request.args.get('days', 30, type=int)

    start_date = datetime.utcnow() - timedelta(days=days)

    stats = audit_service.get_statistics(
        company_id=company_id,
        start_date=start_date
    )

    audit_trail = audit_service.get_company_audit_trail(
        company_id=company_id,
        days=days
    )

    return jsonify({
        'success': True,
        'stats': stats,
        'audit_trail': audit_trail[:100],  # 최근 100개만
        'period_days': days
    })


# ===== 액션 유형 정보 =====

@audit_bp.route('/actions', methods=['GET'])
@login_required
def get_action_types():
    """
    사용 가능한 액션 유형 목록

    Response:
    {
        "success": true,
        "actions": [...]
    }
    """
    actions = [
        {'value': AuditLog.ACTION_VIEW, 'label': '조회'},
        {'value': AuditLog.ACTION_CREATE, 'label': '생성'},
        {'value': AuditLog.ACTION_UPDATE, 'label': '수정'},
        {'value': AuditLog.ACTION_DELETE, 'label': '삭제'},
        {'value': AuditLog.ACTION_EXPORT, 'label': '내보내기'},
        {'value': AuditLog.ACTION_SYNC, 'label': '동기화'},
        {'value': AuditLog.ACTION_LOGIN, 'label': '로그인'},
        {'value': AuditLog.ACTION_LOGOUT, 'label': '로그아웃'},
        {'value': AuditLog.ACTION_ACCESS_DENIED, 'label': '접근 거부'},
    ]

    return jsonify({'success': True, 'actions': actions})


@audit_bp.route('/resource-types', methods=['GET'])
@login_required
def get_resource_types():
    """
    추적 대상 리소스 유형 목록

    Response:
    {
        "success": true,
        "resource_types": [...]
    }
    """
    resource_types = [
        {'value': 'employee', 'label': '직원'},
        {'value': 'contract', 'label': '계약'},
        {'value': 'personal_profile', 'label': '개인 프로필'},
        {'value': 'sync', 'label': '동기화'},
        {'value': 'snapshot', 'label': '스냅샷'},
        {'value': 'termination', 'label': '퇴사 처리'},
        {'value': 'user', 'label': '사용자'},
        {'value': 'company', 'label': '법인'},
        {'value': 'organization', 'label': '조직'},
    ]

    return jsonify({'success': True, 'resource_types': resource_types})


# ===== 접근 요약 =====

@audit_bp.route('/access-summary/employee/<int:employee_id>', methods=['GET'])
@login_required
@admin_required
def get_employee_access_summary(employee_id):
    """
    직원 정보 접근 요약

    Response:
    {
        "success": true,
        "employee_id": 123,
        "summary": {...}
    }
    """
    days = request.args.get('days', 30, type=int)

    summary = audit_service.get_access_summary(
        resource_type='employee',
        resource_id=employee_id,
        days=days
    )

    return jsonify({
        'success': True,
        'employee_id': employee_id,
        'summary': summary
    })


@audit_bp.route('/access-summary/contract/<int:contract_id>', methods=['GET'])
@login_required
@admin_required
def get_contract_access_summary(contract_id):
    """
    계약 정보 접근 요약

    Response:
    {
        "success": true,
        "contract_id": 123,
        "summary": {...}
    }
    """
    days = request.args.get('days', 30, type=int)

    summary = audit_service.get_access_summary(
        resource_type='contract',
        resource_id=contract_id,
        days=days
    )

    return jsonify({
        'success': True,
        'contract_id': contract_id,
        'summary': summary
    })
