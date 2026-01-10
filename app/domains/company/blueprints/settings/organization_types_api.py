"""
조직유형 설정 API

회사별 조직유형 설정 CRUD API를 제공합니다.
Phase 4: 조직유형 설정 기능
"""
from flask import request

from app.domains.company.blueprints.settings import corporate_settings_api_bp
from app.domains.company.blueprints.settings.helpers import get_company_id
from app.domains.company.services import organization_type_config_service
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden, api_not_found
from app.shared.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/organization-types', methods=['GET'])
@corporate_admin_required
def get_organization_types():
    """조직유형 목록 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 기본값이 없으면 생성 (Lazy Initialization)
    types = organization_type_config_service.ensure_defaults_exist(company_id)
    return api_success(types)


@corporate_settings_api_bp.route('/organization-types/active', methods=['GET'])
@corporate_admin_required
def get_active_organization_types():
    """활성화된 조직유형만 조회 (select 옵션용)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    options = organization_type_config_service.get_type_options_for_select(company_id)
    return api_success(options)


@corporate_settings_api_bp.route('/organization-types', methods=['POST'])
@corporate_admin_required
def create_organization_type():
    """조직유형 추가"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    if not data:
        return api_error('요청 데이터가 없습니다.')

    # 필수 필드 검증
    type_label_ko = data.get('type_label_ko', '').strip()
    if not type_label_ko:
        return api_error('한글명은 필수입니다.')

    result = organization_type_config_service.create_config(company_id, data)
    if not result.get('success'):
        return api_error(result.get('error', '조직유형 추가에 실패했습니다.'))

    return api_success(result.get('data'), message='조직유형이 추가되었습니다.')


@corporate_settings_api_bp.route('/organization-types/<int:config_id>', methods=['GET'])
@corporate_admin_required
def get_organization_type(config_id):
    """조직유형 상세 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 소유권 확인
    if not organization_type_config_service.verify_ownership(config_id, company_id):
        return api_not_found('조직유형')

    config = organization_type_config_service.get_by_id(config_id)
    return api_success(config)


@corporate_settings_api_bp.route('/organization-types/<int:config_id>', methods=['DELETE'])
@corporate_admin_required
def delete_organization_type(config_id):
    """조직유형 삭제 (사용 중인 조직이 없는 경우만)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    result = organization_type_config_service.delete_config(config_id, company_id)
    if not result.get('success'):
        return api_error(result.get('error', '삭제에 실패했습니다.'))

    return api_success({'message': '조직유형이 삭제되었습니다.'})


@corporate_settings_api_bp.route('/organization-types/<int:config_id>', methods=['PUT'])
@corporate_admin_required
def update_organization_type(config_id):
    """조직유형 수정 (라벨, 활성화 상태, 아이콘)"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 소유권 확인
    if not organization_type_config_service.verify_ownership(config_id, company_id):
        return api_not_found('조직유형')

    data = request.get_json()
    result = organization_type_config_service.update_config(config_id, data)

    if not result:
        return api_error('조직유형 수정에 실패했습니다.')

    return api_success(result)


@corporate_settings_api_bp.route('/organization-types/<int:config_id>/toggle', methods=['POST'])
@corporate_admin_required
def toggle_organization_type(config_id):
    """조직유형 활성화 상태 토글"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 소유권 확인
    if not organization_type_config_service.verify_ownership(config_id, company_id):
        return api_not_found('조직유형')

    result = organization_type_config_service.toggle_active(config_id)

    if not result:
        return api_error('상태 변경에 실패했습니다.')

    return api_success(result)


@corporate_settings_api_bp.route('/organization-types/reorder', methods=['POST'])
@corporate_admin_required
def reorder_organization_types():
    """조직유형 순서 변경"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    type_ids = data.get('type_ids', [])

    if not type_ids or not isinstance(type_ids, list):
        return api_error('유효한 조직유형 ID 목록이 필요합니다.')

    types = organization_type_config_service.reorder_types(company_id, type_ids)
    return api_success(types, message='순서가 저장되었습니다.')


@corporate_settings_api_bp.route('/organization-types/reset', methods=['POST'])
@corporate_admin_required
def reset_organization_types():
    """조직유형 기본값으로 복원"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    types = organization_type_config_service.reset_to_default(company_id)
    return api_success(types, message='기본값으로 복원되었습니다.')


@corporate_settings_api_bp.route('/organization-types/statistics', methods=['GET'])
@corporate_admin_required
def get_organization_types_statistics():
    """조직유형 통계 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    stats = organization_type_config_service.get_statistics(company_id)
    return api_success(stats)
