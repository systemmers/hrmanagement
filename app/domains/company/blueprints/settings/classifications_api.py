"""
분류 API

조직/직급/직위/직종 CRUD API를 제공합니다.
Phase 2.4: API 응답 표준화 (2025-12-29)
Phase 2 Migration: 도메인으로 이동
"""
from flask import request

from app.domains.company.blueprints.settings import corporate_settings_api_bp
from app.domains.company.blueprints.settings.helpers import get_company_id
from app.domains.company.services.corporate_settings_service import corporate_settings_service
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden, api_not_found
from app.shared.utils.decorators import corporate_admin_required
from app.shared.utils.exceptions import ConflictError


@corporate_settings_api_bp.route('/classifications', methods=['GET'])
@corporate_admin_required
def get_classifications():
    """전체 분류 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 분류 타입 필터 (선택적)
    classification_type = request.args.get('type')

    classifications = corporate_settings_service.get_classifications(company_id, classification_type)
    return api_success(classifications)


@corporate_settings_api_bp.route('/classifications/organizations', methods=['GET'])
@corporate_admin_required
def get_organizations():
    """조직 분류 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    classifications = corporate_settings_service.get_organization_classifications(company_id)
    return api_success(classifications)


@corporate_settings_api_bp.route('/classifications/<type_code>', methods=['GET', 'POST'])
@corporate_admin_required
def get_or_create_classification_by_type(type_code):
    """분류 타입별 조회 또는 생성"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    if request.method == 'GET':
        classifications = corporate_settings_service.get_classifications(company_id, type_code)
        return api_success(classifications)

    # POST: 분류 생성
    data = request.get_json()
    value = data.get('value', '').strip() or data.get('name', '').strip()

    if not value:
        return api_error('값(value)은 필수입니다.')

    try:
        result = corporate_settings_service.add_classification(
            company_id=company_id,
            category=type_code,
            value=value,
            label=value
        )
        return api_success(result, status_code=201)
    except ConflictError as e:
        return api_error(e.message, status_code=409)


@corporate_settings_api_bp.route('/classifications', methods=['POST'])
@corporate_admin_required
def create_classification():
    """분류 생성"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    type_code = data.get('type')
    code = data.get('code', '').strip()
    name = data.get('name', '').strip()

    if not type_code or not code or not name:
        return api_error('타입, 코드, 이름은 필수입니다.')

    result = corporate_settings_service.create_classification(
        company_id=company_id,
        type_code=type_code,
        code=code,
        name=name,
        parent_id=data.get('parentId'),
        display_order=data.get('displayOrder', 0)
    )

    return api_success(result, status_code=201)


@corporate_settings_api_bp.route('/classifications/<int:classification_id>', methods=['PUT'])
@corporate_admin_required
def update_classification(classification_id):
    """분류 수정"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    result = corporate_settings_service.update_classification(classification_id, company_id, data)

    if not result:
        return api_not_found('분류')

    return api_success(result)


@corporate_settings_api_bp.route('/classifications/<type_code>/<int:option_id>', methods=['PUT'])
@corporate_admin_required
def update_classification_by_category(type_code, option_id):
    """카테고리별 분류 수정 (프론트엔드 호환)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    try:
        result = corporate_settings_service.update_classification(option_id, company_id, data)
        if not result:
            return api_not_found('분류')
        return api_success(result)
    except ConflictError as e:
        return api_error(e.message, status_code=409)


@corporate_settings_api_bp.route('/classifications/<int:classification_id>', methods=['DELETE'])
@corporate_admin_required
def delete_classification(classification_id):
    """분류 삭제"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    success = corporate_settings_service.delete_classification(classification_id, company_id)

    if not success:
        return api_error('분류를 찾을 수 없거나 하위 항목이 존재합니다.')

    return api_success(message='분류가 삭제되었습니다.')


@corporate_settings_api_bp.route('/classifications/<type_code>/<int:option_id>', methods=['DELETE'])
@corporate_admin_required
def delete_classification_by_category(type_code, option_id):
    """카테고리별 분류 삭제 (프론트엔드 호환)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    success = corporate_settings_service.delete_classification(option_id, company_id)

    if not success:
        return api_error('분류를 찾을 수 없거나 하위 항목이 존재합니다.')

    return api_success(message='분류가 삭제되었습니다.')


@corporate_settings_api_bp.route('/classifications/reorder', methods=['POST'])
@corporate_admin_required
def reorder_classifications():
    """분류 순서 변경"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    items = data.get('items', [])

    if not items:
        return api_error('순서 변경할 항목이 없습니다.')

    corporate_settings_service.reorder_classifications(company_id, items)
    return api_success(message='순서가 변경되었습니다.')
