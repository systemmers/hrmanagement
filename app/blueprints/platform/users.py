"""
Platform Users Management

사용자 관리 라우트
"""
from flask import render_template, request, jsonify

from . import platform_bp
from ...utils.decorators import superadmin_required, api_superadmin_required
from ...models import User
from ...database import db


@platform_bp.route('/users')
@superadmin_required
def users_list():
    """사용자 목록"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    account_type = request.args.get('account_type', '')

    query = User.query

    if search:
        query = query.filter(
            (User.username.ilike(f'%{search}%')) |
            (User.email.ilike(f'%{search}%'))
        )

    if account_type:
        query = query.filter_by(account_type=account_type)

    pagination = query.order_by(User.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'platform/users/list.html',
        users=pagination.items,
        pagination=pagination,
        search=search,
        account_type=account_type
    )


@platform_bp.route('/users/<int:user_id>')
@superadmin_required
def user_detail(user_id):
    """사용자 상세"""
    user = User.query.get_or_404(user_id)

    return render_template(
        'platform/users/detail.html',
        user=user
    )


@platform_bp.route('/api/users/<int:user_id>/toggle-active', methods=['POST'])
@api_superadmin_required
def toggle_user_active(user_id):
    """사용자 활성화/비활성화 토글"""
    user = User.query.get_or_404(user_id)

    # 자기 자신은 비활성화 불가
    from flask import session
    from ...constants import SessionKeys
    if user.id == session.get(SessionKeys.USER_ID):
        return jsonify({
            'success': False,
            'error': '자기 자신은 비활성화할 수 없습니다.'
        }), 400

    user.is_active = not user.is_active
    db.session.commit()

    return jsonify({
        'success': True,
        'is_active': user.is_active,
        'message': f'사용자가 {"활성화" if user.is_active else "비활성화"}되었습니다.'
    })


@platform_bp.route('/api/users/<int:user_id>/grant-superadmin', methods=['POST'])
@api_superadmin_required
def grant_superadmin(user_id):
    """Superadmin 권한 부여"""
    user = User.query.get_or_404(user_id)

    if user.is_superadmin:
        return jsonify({
            'success': False,
            'error': '이미 슈퍼관리자입니다.'
        }), 400

    user.is_superadmin = True
    user.account_type = User.ACCOUNT_PLATFORM
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'{user.username}에게 슈퍼관리자 권한이 부여되었습니다.'
    })


@platform_bp.route('/api/users/<int:user_id>/revoke-superadmin', methods=['POST'])
@api_superadmin_required
def revoke_superadmin(user_id):
    """Superadmin 권한 해제"""
    user = User.query.get_or_404(user_id)

    # 자기 자신의 권한은 해제 불가
    from flask import session
    from ...constants import SessionKeys
    if user.id == session.get(SessionKeys.USER_ID):
        return jsonify({
            'success': False,
            'error': '자기 자신의 권한은 해제할 수 없습니다.'
        }), 400

    if not user.is_superadmin:
        return jsonify({
            'success': False,
            'error': '슈퍼관리자가 아닙니다.'
        }), 400

    # 마지막 superadmin 확인
    superadmin_count = User.query.filter_by(is_superadmin=True).count()
    if superadmin_count <= 1:
        return jsonify({
            'success': False,
            'error': '최소 1명의 슈퍼관리자가 필요합니다.'
        }), 400

    user.is_superadmin = False
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'{user.username}의 슈퍼관리자 권한이 해제되었습니다.'
    })
