"""
Platform Settings Management

시스템 설정 관리 라우트
Phase 24: PlatformService 경유로 레이어 분리 준수
"""
from flask import render_template, request, jsonify

from . import platform_bp
from ...utils.decorators import superadmin_required, api_superadmin_required
from ...services.platform_service import platform_service


@platform_bp.route('/settings')
@superadmin_required
def settings_list():
    """시스템 설정 목록"""
    settings = platform_service.get_all_settings()

    return render_template(
        'platform/settings.html',
        settings=settings
    )


@platform_bp.route('/api/settings/<string:key>', methods=['PUT'])
@api_superadmin_required
def update_setting(key):
    """시스템 설정 수정"""
    data = request.get_json()
    if 'value' not in data:
        return jsonify({
            'success': False,
            'error': 'value 필드가 필요합니다.'
        }), 400

    success, error, setting_info = platform_service.update_setting(key, data['value'])

    if not success:
        status_code = 404 if '찾을 수 없습니다' in (error or '') else 400
        return jsonify({'success': False, 'error': error}), status_code

    return jsonify({
        'success': True,
        'message': f'설정 "{key}"이(가) 수정되었습니다.',
        'setting': setting_info
    })


@platform_bp.route('/api/settings', methods=['POST'])
@api_superadmin_required
def create_setting():
    """시스템 설정 생성"""
    data = request.get_json()

    if not data.get('key') or 'value' not in data:
        return jsonify({
            'success': False,
            'error': 'key와 value 필드가 필요합니다.'
        }), 400

    success, error, setting_info = platform_service.create_setting(
        key=data['key'],
        value=data['value'],
        description=data.get('description', '')
    )

    if not success:
        return jsonify({'success': False, 'error': error}), 400

    return jsonify({
        'success': True,
        'message': f'설정 "{data["key"]}"이(가) 생성되었습니다.',
        'setting': setting_info
    }), 201
