"""
Platform Settings Management

시스템 설정 관리 라우트

Phase 7: 도메인 중심 마이그레이션 (app/domains/platform/blueprints/)
Phase 24: PlatformService 경유로 레이어 분리 준수
"""
from flask import render_template, request

from . import platform_bp
from app.shared.utils.decorators import superadmin_required, api_superadmin_required
from app.domains.platform.services.platform_service import platform_service
from app.shared.utils.api_helpers import api_success, api_error, api_not_found


@platform_bp.route('/settings')
@superadmin_required
def settings_list():
    """시스템 설정 목록"""
    settings = platform_service.get_all_settings()

    return render_template(
        'domains/platform/settings.html',
        settings=settings
    )


@platform_bp.route('/api/settings/<string:key>', methods=['PUT'])
@api_superadmin_required
def update_setting(key):
    """시스템 설정 수정"""
    data = request.get_json()
    if 'value' not in data:
        return api_error('value 필드가 필요합니다.')

    success, error, setting_info = platform_service.update_setting(key, data['value'])

    if not success:
        if '찾을 수 없습니다' in (error or ''):
            return api_not_found('설정')
        return api_error(error)

    return api_success({
        'message': f'설정 "{key}"이(가) 수정되었습니다.',
        'setting': setting_info
    })


@platform_bp.route('/api/settings', methods=['POST'])
@api_superadmin_required
def create_setting():
    """시스템 설정 생성"""
    data = request.get_json()

    if not data.get('key') or 'value' not in data:
        return api_error('key와 value 필드가 필요합니다.')

    success, error, setting_info = platform_service.create_setting(
        key=data['key'],
        value=data['value'],
        description=data.get('description', '')
    )

    if not success:
        return api_error(error)

    return api_success({
        'message': f'설정 "{data["key"]}"이(가) 생성되었습니다.',
        'setting': setting_info
    }, status_code=201)
