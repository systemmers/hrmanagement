"""
REST API Blueprint

분류 옵션 CRUD API를 제공합니다.
Phase 2: Service 계층 표준화
Phase 6: FieldRegistry API 추가
"""
from flask import Blueprint, jsonify, request, session

from ..services.classification_service import classification_service
from ..constants.field_registry import FieldRegistry
from ..constants.session_keys import SessionKeys
from ..utils.decorators import login_required, admin_required

api_bp = Blueprint('api', __name__)


# ===== Field Registry API =====

@api_bp.route('/fields/sections', methods=['GET'])
@login_required
def get_all_field_sections():
    """
    모든 필드 섹션 메타데이터 조회

    Query Params:
        account_type: 계정 타입 (personal/corporate/employee_sub)
        domain: 도메인명 (profile/employee 등)

    Returns:
        {
            "sections": [...],
            "accountType": "corporate"
        }
    """
    # 계정 타입 결정 (쿼리 파라미터 우선, 없으면 세션에서)
    account_type = request.args.get('account_type') or session.get(SessionKeys.ACCOUNT_TYPE)
    domain = request.args.get('domain')

    if domain:
        # 도메인별 섹션 조회
        sections = FieldRegistry.get_sections_by_domain(domain)
    else:
        # 모든 섹션 조회
        sections = FieldRegistry.get_all_sections()

    # 계정 타입별 가시성 필터링 및 변환
    result_sections = []
    for section in sections:
        if account_type and not section.is_visible_for(account_type):
            continue
        result_sections.append(
            FieldRegistry.get_js_config(section.id, account_type)
        )

    return jsonify({
        'sections': result_sections,
        'accountType': account_type,
        'domain': domain,
    })


@api_bp.route('/fields/sections/<section_id>', methods=['GET'])
@login_required
def get_field_section(section_id):
    """
    특정 필드 섹션 메타데이터 조회

    Args:
        section_id: 섹션 ID

    Query Params:
        account_type: 계정 타입 (필터링용)

    Returns:
        섹션 메타데이터 JSON
    """
    account_type = request.args.get('account_type') or session.get(SessionKeys.ACCOUNT_TYPE)

    section = FieldRegistry.get_section(section_id)
    if not section:
        return jsonify({'error': f'Section not found: {section_id}'}), 404

    # 계정 타입별 가시성 체크
    if account_type and not section.is_visible_for(account_type):
        return jsonify({'error': 'Section not accessible for this account type'}), 403

    return jsonify({
        'section': FieldRegistry.get_js_config(section_id, account_type),
        'accountType': account_type,
    })


@api_bp.route('/fields/domains', methods=['GET'])
@login_required
def get_all_domains():
    """
    등록된 모든 도메인 목록 조회

    Returns:
        {"domains": ["profile", "employee", ...]}
    """
    return jsonify({
        'domains': FieldRegistry.get_all_domains()
    })


@api_bp.route('/classification-options', methods=['GET'])
@login_required
def get_classification_options():
    """분류 옵션 조회"""
    options = classification_service.get_all()
    return jsonify(options)


# ===== 부서 관리 API =====

@api_bp.route('/classification-options/departments', methods=['POST'])
@admin_required
def add_department():
    """부서 추가"""
    data = request.get_json()
    department = data.get('department', '').strip()

    if not department:
        return jsonify({'error': '부서명이 필요합니다.'}), 400

    if classification_service.add_department(department):
        return jsonify({'success': True, 'message': f'{department} 부서가 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 부서입니다.'}), 400


@api_bp.route('/classification-options/departments/<old_department>', methods=['PUT'])
@admin_required
def update_department(old_department):
    """부서 수정"""
    data = request.get_json()
    new_department = data.get('department', '').strip()

    if not new_department:
        return jsonify({'error': '새 부서명이 필요합니다.'}), 400

    if classification_service.update_department(old_department, new_department):
        return jsonify({'success': True, 'message': f'부서가 {new_department}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404


@api_bp.route('/classification-options/departments/<department>', methods=['DELETE'])
@admin_required
def delete_department(department):
    """부서 삭제"""
    if classification_service.delete_department(department):
        return jsonify({'success': True, 'message': f'{department} 부서가 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '부서를 찾을 수 없습니다.'}), 404


# ===== 직급 관리 API =====

@api_bp.route('/classification-options/positions', methods=['POST'])
@admin_required
def add_position():
    """직급 추가"""
    data = request.get_json()
    position = data.get('position', '').strip()

    if not position:
        return jsonify({'error': '직급명이 필요합니다.'}), 400

    if classification_service.add_position(position):
        return jsonify({'success': True, 'message': f'{position} 직급이 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 직급입니다.'}), 400


@api_bp.route('/classification-options/positions/<old_position>', methods=['PUT'])
@admin_required
def update_position(old_position):
    """직급 수정"""
    data = request.get_json()
    new_position = data.get('position', '').strip()

    if not new_position:
        return jsonify({'error': '새 직급명이 필요합니다.'}), 400

    if classification_service.update_position(old_position, new_position):
        return jsonify({'success': True, 'message': f'직급이 {new_position}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404


@api_bp.route('/classification-options/positions/<position>', methods=['DELETE'])
@admin_required
def delete_position(position):
    """직급 삭제"""
    if classification_service.delete_position(position):
        return jsonify({'success': True, 'message': f'{position} 직급이 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '직급을 찾을 수 없습니다.'}), 404


# ===== 상태 관리 API =====

@api_bp.route('/classification-options/statuses', methods=['POST'])
@admin_required
def add_status():
    """상태 추가"""
    data = request.get_json()
    value = data.get('value', '').strip()
    label = data.get('label', '').strip()

    if not value or not label:
        return jsonify({'error': '상태 값과 라벨이 필요합니다.'}), 400

    if classification_service.add_status(value, label):
        return jsonify({'success': True, 'message': f'{label} 상태가 추가되었습니다.'}), 201
    else:
        return jsonify({'error': '이미 존재하는 상태입니다.'}), 400


@api_bp.route('/classification-options/statuses/<old_value>', methods=['PUT'])
@admin_required
def update_status(old_value):
    """상태 수정"""
    data = request.get_json()
    new_value = data.get('value', '').strip()
    new_label = data.get('label', '').strip()

    if not new_value or not new_label:
        return jsonify({'error': '새 상태 값과 라벨이 필요합니다.'}), 400

    if classification_service.update_status(old_value, new_value, new_label):
        return jsonify({'success': True, 'message': f'상태가 {new_label}로 변경되었습니다.'}), 200
    else:
        return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404


@api_bp.route('/classification-options/statuses/<value>', methods=['DELETE'])
@admin_required
def delete_status(value):
    """상태 삭제"""
    if classification_service.delete_status(value):
        return jsonify({'success': True, 'message': '상태가 삭제되었습니다.'}), 200
    else:
        return jsonify({'error': '상태를 찾을 수 없습니다.'}), 404
