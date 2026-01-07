"""
노출 설정 API

필드 노출 설정 CRUD API를 제공합니다.
Phase 2.4: API 응답 표준화 (2025-12-29)
Phase 2 Migration: 도메인으로 이동
"""
from flask import request

from app.domains.company.blueprints.settings import corporate_settings_api_bp
from app.domains.company.blueprints.settings.helpers import get_company_id
from app.domains.company.services.corporate_settings_service import corporate_settings_service
from app.shared.utils.api_helpers import api_success, api_forbidden
from app.shared.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/visibility', methods=['GET'])
@corporate_admin_required
def get_visibility_settings():
    """노출 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    settings = corporate_settings_service.get_visibility_settings(company_id)
    return api_success(settings)


@corporate_settings_api_bp.route('/visibility', methods=['PUT'])
@corporate_admin_required
def update_visibility_settings():
    """노출 설정 저장"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    data = request.get_json()
    result = corporate_settings_service.update_visibility_settings(company_id, data)

    return api_success(result)


@corporate_settings_api_bp.route('/visibility/reset', methods=['POST'])
@corporate_admin_required
def reset_visibility_settings():
    """노출 설정 기본값 초기화"""
    company_id = get_company_id()
    if not company_id:
        return api_forbidden('법인 정보를 찾을 수 없습니다.')

    result = corporate_settings_service.reset_visibility_settings(company_id)
    return api_success(result)
