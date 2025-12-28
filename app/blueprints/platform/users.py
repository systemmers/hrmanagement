"""
Platform Users Management

사용자 관리 라우트
Phase 24: PlatformService 경유로 레이어 분리 준수
"""
from flask import render_template, request, jsonify, session, abort

from . import platform_bp
from ...utils.decorators import superadmin_required, api_superadmin_required
from ...services.platform_service import platform_service
from ...constants import SessionKeys


@platform_bp.route('/users')
@superadmin_required
def users_list():
    """사용자 목록"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip() or None
    account_type = request.args.get('account_type', '') or None

    users, pagination = platform_service.get_users_paginated(
        page=page,
        per_page=per_page,
        search=search,
        account_type=account_type
    )

    return render_template(
        'platform/users/list.html',
        users=users,
        pagination=pagination,
        search=search or '',
        account_type=account_type or ''
    )


@platform_bp.route('/users/<int:user_id>')
@superadmin_required
def user_detail(user_id):
    """사용자 상세"""
    user = platform_service.get_user_by_id(user_id)
    if not user:
        abort(404)

    return render_template(
        'platform/users/detail.html',
        user=user
    )


@platform_bp.route('/api/users/<int:user_id>/toggle-active', methods=['POST'])
@api_superadmin_required
def toggle_user_active(user_id):
    """사용자 활성화/비활성화 토글"""
    current_user_id = session.get(SessionKeys.USER_ID)

    success, error, is_active = platform_service.toggle_user_active(
        user_id, current_user_id
    )

    if not success:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({
        'success': True,
        'is_active': is_active,
        'message': f'사용자가 {"활성화" if is_active else "비활성화"}되었습니다.'
    })


@platform_bp.route('/api/users/<int:user_id>/grant-superadmin', methods=['POST'])
@api_superadmin_required
def grant_superadmin(user_id):
    """Superadmin 권한 부여"""
    success, error = platform_service.grant_superadmin(user_id)

    if not success:
        return jsonify({'success': False, 'error': error}), 400

    # 성공 메시지를 위해 사용자 정보 조회
    user = platform_service.get_user_by_id(user_id)
    username = user.username if user else f'ID:{user_id}'

    return jsonify({
        'success': True,
        'message': f'{username}에게 슈퍼관리자 권한이 부여되었습니다.'
    })


@platform_bp.route('/api/users/<int:user_id>/revoke-superadmin', methods=['POST'])
@api_superadmin_required
def revoke_superadmin(user_id):
    """Superadmin 권한 해제"""
    current_user_id = session.get(SessionKeys.USER_ID)

    # 성공 메시지를 위해 먼저 사용자 정보 조회
    user = platform_service.get_user_by_id(user_id)
    username = user.username if user else f'ID:{user_id}'

    success, error = platform_service.revoke_superadmin(user_id, current_user_id)

    if not success:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({
        'success': True,
        'message': f'{username}의 슈퍼관리자 권한이 해제되었습니다.'
    })
