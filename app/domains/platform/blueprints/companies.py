"""
Platform Companies Management

법인 관리 라우트

Phase 7: 도메인 중심 마이그레이션 (app/domains/platform/blueprints/)
Phase 24: PlatformService 경유로 레이어 분리 준수
"""
from flask import render_template, request, abort

from . import platform_bp
from app.shared.utils.decorators import superadmin_required, api_superadmin_required
from app.domains.platform.services.platform_service import platform_service
from app.shared.utils.api_helpers import api_success, api_error
from app.shared.constants.field_options import FieldOptions


@platform_bp.route('/companies')
@superadmin_required
def companies_list():
    """법인 목록"""
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)
    search = request.args.get('search', '').strip() or None

    companies, pagination = platform_service.get_companies_paginated(
        page=page,
        per_page=per_page,
        search=search
    )

    return render_template(
        'platform/companies/list.html',
        companies=companies,
        pagination=pagination,
        search=search or '',
        status=request.args.get('status', ''),
        field_options=FieldOptions
    )


@platform_bp.route('/companies/<int:company_id>')
@superadmin_required
def company_detail(company_id):
    """법인 상세"""
    company = platform_service.get_company_by_id(company_id)
    if not company:
        abort(404)

    # 법인 소속 사용자
    users = platform_service.get_users_by_company(company_id)

    return render_template(
        'platform/companies/detail.html',
        company=company,
        users=users
    )


@platform_bp.route('/api/companies/<int:company_id>/toggle-active', methods=['POST'])
@api_superadmin_required
def toggle_company_active(company_id):
    """법인 활성화/비활성화 토글"""
    success, error, is_active = platform_service.toggle_company_active(company_id)

    if not success:
        return api_error(error)

    return api_success({
        'is_active': is_active,
        'message': f'법인이 {"활성화" if is_active else "비활성화"}되었습니다.'
    })
