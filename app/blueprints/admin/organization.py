"""
조직 관리 Blueprint

조직 구조 CRUD 및 트리 관리 기능을 제공합니다.
"""
from flask import render_template, request, jsonify, flash, redirect, url_for

from . import admin_bp
from ...extensions import organization_repo, employee_repo
from ...utils.decorators import admin_required, login_required


@admin_bp.route('/organizations')
@admin_required
def organization_list():
    """조직 관리 페이지"""
    tree = organization_repo.get_tree()
    flat_list = organization_repo.get_flat_list()
    stats = organization_repo.get_organization_statistics()

    return render_template('admin/organization.html',
                           tree=tree,
                           organizations=flat_list,
                           stats=stats)


@admin_bp.route('/api/organizations', methods=['GET'])
@login_required
def api_get_organizations():
    """조직 목록 API"""
    format_type = request.args.get('format', 'tree')

    if format_type == 'tree':
        data = organization_repo.get_tree()
    elif format_type == 'flat':
        data = organization_repo.get_flat_list()
    else:
        data = organization_repo.get_tree()

    return jsonify({'success': True, 'data': data})


@admin_bp.route('/api/organizations/<int:org_id>', methods=['GET'])
@login_required
def api_get_organization(org_id):
    """조직 상세 조회 API"""
    org = organization_repo.get_by_id(org_id)
    if not org:
        return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    return jsonify({'success': True, 'data': org})


@admin_bp.route('/api/organizations', methods=['POST'])
@admin_required
def api_create_organization():
    """조직 생성 API"""
    data = request.get_json()

    name = data.get('name', '').strip()
    org_type = data.get('org_type', 'department')
    parent_id = data.get('parent_id')
    code = data.get('code', '').strip() or None
    manager_id = data.get('manager_id')
    description = data.get('description', '').strip() or None

    # 필수 값 검증
    if not name:
        return jsonify({'success': False, 'error': '조직명은 필수입니다.'}), 400

    # 코드 중복 검사
    if code and organization_repo.code_exists(code):
        return jsonify({'success': False, 'error': '이미 사용 중인 조직 코드입니다.'}), 400

    try:
        org = organization_repo.create_organization(
            name=name,
            org_type=org_type,
            parent_id=parent_id,
            code=code,
            manager_id=manager_id,
            description=description
        )
        return jsonify({'success': True, 'data': org.to_dict()}), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>', methods=['PUT'])
@admin_required
def api_update_organization(org_id):
    """조직 수정 API"""
    data = request.get_json()

    # 코드 중복 검사 (자기 자신 제외)
    code = data.get('code', '').strip() or None
    if code and organization_repo.code_exists(code, exclude_id=org_id):
        return jsonify({'success': False, 'error': '이미 사용 중인 조직 코드입니다.'}), 400

    try:
        org = organization_repo.update_organization(org_id, data)
        if not org:
            return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

        return jsonify({'success': True, 'data': org.to_dict()})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>', methods=['DELETE'])
@admin_required
def api_delete_organization(org_id):
    """조직 비활성화 API"""
    cascade = request.args.get('cascade', 'false').lower() == 'true'

    try:
        if organization_repo.deactivate(org_id, cascade=cascade):
            return jsonify({'success': True, 'message': '조직이 비활성화되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>/move', methods=['POST'])
@admin_required
def api_move_organization(org_id):
    """조직 이동 API"""
    data = request.get_json()
    new_parent_id = data.get('parent_id')

    try:
        if organization_repo.move_organization(org_id, new_parent_id):
            return jsonify({'success': True, 'message': '조직이 이동되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '조직 이동에 실패했습니다.'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>/children', methods=['GET'])
@login_required
def api_get_children(org_id):
    """하위 조직 목록 API"""
    children = organization_repo.get_children(org_id)
    return jsonify({'success': True, 'data': children})


@admin_bp.route('/api/organizations/search', methods=['GET'])
@login_required
def api_search_organizations():
    """조직 검색 API"""
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'success': True, 'data': []})

    results = organization_repo.search(query)
    return jsonify({'success': True, 'data': results})
