"""
Platform Settings Management

시스템 설정 관리 라우트
"""
from flask import render_template, request, jsonify

from . import platform_bp
from ...utils.decorators import superadmin_required, api_superadmin_required
from ...models import SystemSetting
from ...database import db


@platform_bp.route('/settings')
@superadmin_required
def settings_list():
    """시스템 설정 목록"""
    settings = SystemSetting.query.order_by(SystemSetting.key).all()

    return render_template(
        'platform/settings.html',
        settings=settings
    )


@platform_bp.route('/api/settings/<string:key>', methods=['PUT'])
@api_superadmin_required
def update_setting(key):
    """시스템 설정 수정"""
    setting = SystemSetting.query.filter_by(key=key).first()

    if not setting:
        return jsonify({
            'success': False,
            'error': f'설정 "{key}"을(를) 찾을 수 없습니다.'
        }), 404

    data = request.get_json()
    if 'value' not in data:
        return jsonify({
            'success': False,
            'error': 'value 필드가 필요합니다.'
        }), 400

    setting.value = data['value']
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'설정 "{key}"이(가) 수정되었습니다.',
        'setting': {
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        }
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

    # 중복 확인
    if SystemSetting.query.filter_by(key=data['key']).first():
        return jsonify({
            'success': False,
            'error': f'설정 "{data["key"]}"이(가) 이미 존재합니다.'
        }), 400

    setting = SystemSetting(
        key=data['key'],
        value=data['value'],
        description=data.get('description', '')
    )
    db.session.add(setting)
    db.session.commit()

    return jsonify({
        'success': True,
        'message': f'설정 "{data["key"]}"이(가) 생성되었습니다.',
        'setting': {
            'key': setting.key,
            'value': setting.value,
            'description': setting.description
        }
    }), 201
