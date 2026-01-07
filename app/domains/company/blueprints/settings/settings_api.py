"""
법인 설정 API

법인별 설정 CRUD API를 제공합니다.
Phase 2.4: API 응답 표준화 (2025-12-29)
Phase 2 Migration: 도메인으로 이동
"""
from flask import request

from app.domains.company.blueprints.settings import corporate_settings_api_bp
from app.domains.company.blueprints.settings.helpers import get_company_id
from app.domains.company.services.corporate_settings_service import corporate_settings_service
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden
from app.shared.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/settings', methods=['GET'])
@corporate_admin_required
def get_settings():
    """전체 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    # 카테고리 필터 (선택적)
    category = request.args.get('category')

    settings = corporate_settings_service.get_all_settings(company_id, category)
    return api_success(settings)


@corporate_settings_api_bp.route('/settings/<key>', methods=['GET'])
@corporate_admin_required
def get_setting(key):
    """개별 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    value = corporate_settings_service.get_setting(company_id, key)
    return api_success({'key': key, 'value': value})


@corporate_settings_api_bp.route('/settings', methods=['PUT'])
@corporate_admin_required
def update_settings():
    """설정 일괄 저장"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    if not data:
        return api_error('저장할 설정이 없습니다.')

    corporate_settings_service.save_settings(company_id, data)
    return api_success(message='설정이 저장되었습니다.')


@corporate_settings_api_bp.route('/settings/<key>', methods=['PUT'])
@corporate_admin_required
def update_setting(key):
    """개별 설정 저장"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    value = data.get('value')

    corporate_settings_service.set_setting(company_id, key, value)
    return api_success({'key': key, 'value': value})


@corporate_settings_api_bp.route('/settings/<key>', methods=['DELETE'])
@corporate_admin_required
def delete_setting(key):
    """설정 삭제"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    corporate_settings_service.delete_setting(company_id, key)
    return api_success(message='설정이 삭제되었습니다.')
