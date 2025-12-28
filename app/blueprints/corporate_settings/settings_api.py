"""
법인 설정 API

법인 설정 CRUD API를 제공합니다.
"""
from flask import jsonify, request

from app.blueprints.corporate_settings import corporate_settings_api_bp
from app.blueprints.corporate_settings.helpers import get_company_id
from app.services.corporate_settings_service import corporate_settings_service
from app.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/settings', methods=['GET'])
@corporate_admin_required
def get_settings():
    """법인 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = corporate_settings_service.get_settings(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings', methods=['PUT'])
@corporate_admin_required
def update_settings():
    """법인 설정 저장"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()

    # 키-값 쌍 저장
    results = corporate_settings_service.update_settings(company_id, data)

    return jsonify({'success': True, 'updated': len(results)})


@corporate_settings_api_bp.route('/settings/<key>', methods=['GET'])
@corporate_admin_required
def get_setting(key):
    """단일 설정값 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    value = corporate_settings_service.get_setting(company_id, key)
    return jsonify({'key': key, 'value': value})


@corporate_settings_api_bp.route('/settings/<key>', methods=['PUT'])
@corporate_admin_required
def set_setting(key):
    """단일 설정값 저장"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    value = data.get('value')

    result = corporate_settings_service.set_setting(company_id, key, value)
    return jsonify(result)


@corporate_settings_api_bp.route('/settings/employee-number', methods=['GET'])
@corporate_admin_required
def get_employee_number_settings():
    """사번 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = corporate_settings_service.get_employee_number_settings(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings/payroll', methods=['GET'])
@corporate_admin_required
def get_payroll_settings():
    """급여 설정 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    settings = corporate_settings_service.get_payroll_settings(company_id)
    return jsonify(settings)


@corporate_settings_api_bp.route('/settings/initialize', methods=['POST'])
@corporate_admin_required
def initialize_settings():
    """기본 설정값 초기화"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    results = corporate_settings_service.initialize_settings(company_id)
    return jsonify({'success': True, 'initialized': len(results)})
