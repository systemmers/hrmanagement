"""
Platform Companies Management

법인 관리 라우트
"""
from flask import render_template, request, jsonify

from . import platform_bp
from ...utils.decorators import superadmin_required, api_superadmin_required
from ...models import Company, User
from ...database import db


@platform_bp.route('/companies')
@superadmin_required
def companies_list():
    """법인 목록"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip()
    status = request.args.get('status', '')

    query = Company.query

    if search:
        query = query.filter(Company.name.ilike(f'%{search}%'))

    if status == 'active':
        query = query.filter_by(is_active=True)
    elif status == 'inactive':
        query = query.filter_by(is_active=False)

    pagination = query.order_by(Company.created_at.desc()).paginate(
        page=page, per_page=per_page, error_out=False
    )

    return render_template(
        'platform/companies/list.html',
        companies=pagination.items,
        pagination=pagination,
        search=search,
        status=status
    )


@platform_bp.route('/companies/<int:company_id>')
@superadmin_required
def company_detail(company_id):
    """법인 상세"""
    company = Company.query.get_or_404(company_id)

    # 법인 소속 사용자
    users = User.query.filter_by(company_id=company_id).all()

    return render_template(
        'platform/companies/detail.html',
        company=company,
        users=users
    )


@platform_bp.route('/api/companies/<int:company_id>/toggle-active', methods=['POST'])
@api_superadmin_required
def toggle_company_active(company_id):
    """법인 활성화/비활성화 토글"""
    company = Company.query.get_or_404(company_id)

    company.is_active = not company.is_active
    db.session.commit()

    return jsonify({
        'success': True,
        'is_active': company.is_active,
        'message': f'법인이 {"활성화" if company.is_active else "비활성화"}되었습니다.'
    })
