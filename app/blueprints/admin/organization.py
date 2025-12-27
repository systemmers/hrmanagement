"""
조직 관리 Blueprint

조직 구조 CRUD 및 트리 관리 기능을 제공합니다.
멀티테넌시: 현재 로그인한 회사의 조직만 접근 가능합니다.
Phase 2: Service 계층 표준화
"""
from flask import render_template, request, jsonify, flash, redirect, url_for, session

from . import admin_bp
from ...constants.session_keys import SessionKeys
from ...services.organization_service import organization_service
from ...services.company_service import company_service
from ...utils.decorators import admin_required, login_required


def get_current_root_organization_id():
    """현재 로그인한 회사의 root_organization_id 반환

    Returns:
        root_organization_id 또는 None
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        return None
    company = company_service.get_by_id(company_id)
    return company.root_organization_id if company else None


@admin_bp.route('/organizations')
@admin_required
def organization_list():
    """조직 관리 페이지 (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()

    tree = organization_service.get_tree(root_organization_id=root_org_id)
    flat_list = organization_service.get_flat_list(root_organization_id=root_org_id)
    stats = organization_service.get_organization_statistics(root_organization_id=root_org_id)

    return render_template('admin/organization.html',
                           tree=tree,
                           organizations=flat_list,
                           stats=stats)


@admin_bp.route('/api/organizations', methods=['GET'])
@login_required
def api_get_organizations():
    """조직 목록 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    format_type = request.args.get('format', 'tree')

    if format_type == 'tree':
        data = organization_service.get_tree(root_organization_id=root_org_id)
    elif format_type == 'flat':
        data = organization_service.get_flat_list(root_organization_id=root_org_id)
    else:
        data = organization_service.get_tree(root_organization_id=root_org_id)

    return jsonify({'success': True, 'data': data})


@admin_bp.route('/api/organizations/<int:org_id>', methods=['GET'])
@login_required
def api_get_organization(org_id):
    """조직 상세 조회 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()

    # 멀티테넌시 검증
    if root_org_id and not organization_service.verify_ownership(org_id, root_org_id):
        return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    org = organization_service.get_by_id(org_id)
    if not org:
        return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    return jsonify({'success': True, 'data': org})


@admin_bp.route('/api/organizations', methods=['POST'])
@admin_required
def api_create_organization():
    """조직 생성 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
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

    # parent_id가 없는 경우 현재 회사의 root_organization_id를 기본값으로 설정
    if not parent_id and root_org_id:
        parent_id = root_org_id

    # 코드 중복 검사 (테넌트 범위 내)
    if code and organization_service.code_exists(code, root_organization_id=root_org_id):
        return jsonify({'success': False, 'error': '이미 사용 중인 조직 코드입니다.'}), 400

    try:
        org = organization_service.create_organization(
            name=name,
            org_type=org_type,
            parent_id=parent_id,
            code=code,
            manager_id=manager_id,
            description=description,
            root_organization_id=root_org_id
        )
        return jsonify({'success': True, 'data': org.to_dict()}), 201

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>', methods=['PUT'])
@admin_required
def api_update_organization(org_id):
    """조직 수정 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    data = request.get_json()

    # 멀티테넌시 검증
    if root_org_id and not organization_service.verify_ownership(org_id, root_org_id):
        return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    # 코드 중복 검사 (자기 자신 제외, 테넌트 범위 내)
    code = data.get('code', '').strip() or None
    if code and organization_service.code_exists(code, exclude_id=org_id, root_organization_id=root_org_id):
        return jsonify({'success': False, 'error': '이미 사용 중인 조직 코드입니다.'}), 400

    try:
        org = organization_service.update_organization(org_id, data, root_organization_id=root_org_id)
        if not org:
            return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

        return jsonify({'success': True, 'data': org.to_dict()})

    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>', methods=['DELETE'])
@admin_required
def api_delete_organization(org_id):
    """조직 비활성화 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    cascade = request.args.get('cascade', 'false').lower() == 'true'

    try:
        if organization_service.deactivate(org_id, cascade=cascade, root_organization_id=root_org_id):
            return jsonify({'success': True, 'message': '조직이 비활성화되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '조직을 찾을 수 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>/move', methods=['POST'])
@admin_required
def api_move_organization(org_id):
    """조직 이동 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    data = request.get_json()
    new_parent_id = data.get('parent_id')

    try:
        if organization_service.move_organization(org_id, new_parent_id, root_organization_id=root_org_id):
            return jsonify({'success': True, 'message': '조직이 이동되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '조직 이동에 실패했습니다.'}), 400

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@admin_bp.route('/api/organizations/<int:org_id>/children', methods=['GET'])
@login_required
def api_get_children(org_id):
    """하위 조직 목록 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    children = organization_service.get_children(org_id, root_organization_id=root_org_id)
    return jsonify({'success': True, 'data': children})


@admin_bp.route('/api/organizations/search', methods=['GET'])
@login_required
def api_search_organizations():
    """조직 검색 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    query = request.args.get('q', '').strip()
    if not query:
        return jsonify({'success': True, 'data': []})

    results = organization_service.search(query, root_organization_id=root_org_id)
    return jsonify({'success': True, 'data': results})
