"""
분류 옵션 (조직 구조) API

조직 구조, 고용 정책 등 분류 옵션 CRUD API를 제공합니다.
"""
from flask import jsonify, request

from app.blueprints.corporate_settings import corporate_settings_api_bp
from app.blueprints.corporate_settings.helpers import get_company_id
from app.models import ClassificationOption
from app.services.corporate_settings_service import corporate_settings_service
from app.utils.decorators import corporate_admin_required


@corporate_settings_api_bp.route('/classifications', methods=['GET'])
@corporate_admin_required
def get_all_classifications():
    """모든 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = corporate_settings_service.get_all_classifications(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/organization', methods=['GET'])
@corporate_admin_required
def get_organization_classifications():
    """조직 구조 탭용 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = corporate_settings_service.get_organization_options(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/employment', methods=['GET'])
@corporate_admin_required
def get_employment_classifications():
    """고용 정책 탭용 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    options = corporate_settings_service.get_employment_options(company_id)
    return jsonify(options)


@corporate_settings_api_bp.route('/classifications/<category>', methods=['GET'])
@corporate_admin_required
def get_classifications_by_category(category):
    """카테고리별 분류 옵션 조회"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    if category not in ClassificationOption.VALID_CATEGORIES:
        return jsonify({'error': '유효하지 않은 카테고리입니다.'}), 400

    options = corporate_settings_service.get_classifications_by_category(category, company_id)
    return jsonify({
        'category': category,
        'categoryLabel': ClassificationOption.get_category_label(category),
        'options': options
    })


@corporate_settings_api_bp.route('/classifications/<category>', methods=['POST'])
@corporate_admin_required
def add_classification(category):
    """분류 옵션 추가"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    if category not in ClassificationOption.VALID_CATEGORIES:
        return jsonify({'error': '유효하지 않은 카테고리입니다.'}), 400

    data = request.get_json()
    value = data.get('value', '').strip()
    label = data.get('label', '').strip()

    if not value:
        return jsonify({'error': '값을 입력해주세요.'}), 400

    result = corporate_settings_service.add_classification(
        company_id=company_id,
        category=category,
        value=value,
        label=label or value
    )

    return jsonify(result), 201


@corporate_settings_api_bp.route('/classifications/<category>/<int:option_id>', methods=['PUT'])
@corporate_admin_required
def update_classification(category, option_id):
    """분류 옵션 수정"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    result = corporate_settings_service.update_classification(option_id, company_id, data)

    if not result:
        return jsonify({'error': '옵션을 찾을 수 없거나 수정할 수 없습니다.'}), 404

    return jsonify(result)


@corporate_settings_api_bp.route('/classifications/<category>/<int:option_id>', methods=['DELETE'])
@corporate_admin_required
def delete_classification(category, option_id):
    """분류 옵션 삭제"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    success = corporate_settings_service.delete_classification(option_id, company_id)

    if not success:
        return jsonify({'error': '옵션을 찾을 수 없거나 삭제할 수 없습니다.'}), 404

    return jsonify({'success': True, 'message': '옵션이 삭제되었습니다.'})


@corporate_settings_api_bp.route('/classifications/<category>/toggle', methods=['POST'])
@corporate_admin_required
def toggle_system_classification(category):
    """시스템 옵션 활성화/비활성화 토글"""
    company_id = get_company_id()
    if not company_id:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 403

    data = request.get_json()
    value = data.get('value')
    is_active = data.get('isActive', True)

    if not value:
        return jsonify({'error': '값을 입력해주세요.'}), 400

    result = corporate_settings_service.toggle_system_option(company_id, category, value, is_active)

    return jsonify({'success': True, 'result': result})
