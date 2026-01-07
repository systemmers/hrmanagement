"""
번호 카테고리 API

사번, 자산번호 등 번호 분류코드 CRUD API를 제공합니다.
Phase 2.4: API 응답 표준화 (2025-12-29)
Phase 2 Migration: 도메인으로 이동
"""
from flask import request

from app.domains.company.blueprints.settings import corporate_settings_api_bp
from app.domains.company.blueprints.settings.helpers import get_company_id
from app.domains.company.services.corporate_settings_service import corporate_settings_service
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden, api_not_found
from app.shared.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/number-categories', methods=['GET'])
@corporate_admin_required
def get_number_categories():
    """번호 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    type_filter = request.args.get('type')
    categories = corporate_settings_service.get_number_categories(company_id, type_filter)
    return api_success(categories)


@corporate_settings_api_bp.route('/number-categories/employee', methods=['GET'])
@corporate_admin_required
def get_employee_number_categories():
    """사번 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    categories = corporate_settings_service.get_employee_categories(company_id)
    return api_success(categories)


@corporate_settings_api_bp.route('/number-categories/asset', methods=['GET'])
@corporate_admin_required
def get_asset_number_categories():
    """자산번호 분류코드 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    categories = corporate_settings_service.get_asset_categories(company_id)
    return api_success(categories)


@corporate_settings_api_bp.route('/number-categories', methods=['POST'])
@corporate_admin_required
def create_number_category():
    """번호 분류코드 생성"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    type_code = data.get('type')
    code = data.get('code', '').strip()
    name = data.get('name', '').strip()
    description = data.get('description', '').strip()

    if not type_code or not code or not name:
        return api_error('타입, 코드, 이름은 필수입니다.')

    result = corporate_settings_service.create_number_category(
        company_id=company_id,
        type_code=type_code,
        code=code,
        name=name,
        description=description
    )

    return api_success(result, status_code=201)


@corporate_settings_api_bp.route('/number-categories/<int:category_id>', methods=['PUT'])
@corporate_admin_required
def update_number_category(category_id):
    """번호 분류코드 수정"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    result = corporate_settings_service.update_number_category(category_id, company_id, data)

    if not result:
        return api_not_found('분류코드')

    return api_success(result)


@corporate_settings_api_bp.route('/number-categories/<int:category_id>', methods=['DELETE'])
@corporate_admin_required
def delete_number_category(category_id):
    """번호 분류코드 삭제"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    success = corporate_settings_service.delete_number_category(category_id, company_id)

    if not success:
        return api_error('분류코드를 찾을 수 없거나 사용중인 번호가 있습니다.')

    return api_success(message='분류코드가 삭제되었습니다.')


@corporate_settings_api_bp.route('/number-categories/<int:category_id>/preview', methods=['GET'])
@corporate_admin_required
def preview_next_number(category_id):
    """다음 번호 미리보기"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    company_code = corporate_settings_service.get_setting(company_id, 'company_code') or ''
    separator = corporate_settings_service.get_setting(company_id, 'employee_number.separator') or '-'
    digits = corporate_settings_service.get_setting(company_id, 'employee_number.digits') or 6

    preview = corporate_settings_service.preview_next_number(
        category_id, company_code, separator, int(digits)
    )

    return api_success({'preview': preview})


@corporate_settings_api_bp.route('/number-categories/initialize-assets', methods=['POST'])
@corporate_admin_required
def initialize_asset_categories():
    """기본 자산 분류코드 초기화"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    results = corporate_settings_service.initialize_asset_categories(company_id)
    return api_success({'initialized': len(results)})
