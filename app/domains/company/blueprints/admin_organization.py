"""
조직 관리 Blueprint

조직 구조 CRUD 및 트리 관리 기능을 제공합니다.
멀티테넌시: 현재 로그인한 회사의 조직만 접근 가능합니다.
Phase 2: Service 계층 표준화
Phase 9: 도메인 마이그레이션 - app/domains/company/blueprints/로 이동
"""
from flask import Blueprint, render_template, request, flash, redirect, url_for, session

from app.shared.constants.session_keys import SessionKeys
from app.domains.company.services.organization_service import organization_service
from app.domains.company.services.company_service import company_service
from app.domains.employee.services import employee_service
from app.shared.utils.decorators import admin_required, login_required
from app.shared.utils.api_helpers import api_success, api_error, api_not_found, api_server_error

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


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
    """조직 관리 페이지 - 법인설정 조직관리 탭으로 리다이렉트"""
    # Phase 6: 독립 페이지 제거 - 법인설정 조직관리 탭으로 통합
    return redirect(url_for('corporate.settings') + '#org-management')


@admin_bp.route('/api/organizations', methods=['GET'])
@login_required
def api_get_organizations():
    """조직 목록 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    format_type = request.args.get('format', 'tree')

    if format_type == 'tree':
        data = organization_service.get_tree_with_member_count(root_organization_id=root_org_id)
    elif format_type == 'flat':
        data = organization_service.get_flat_list(root_organization_id=root_org_id)
    else:
        data = organization_service.get_tree_with_member_count(root_organization_id=root_org_id)

    return api_success(data)


@admin_bp.route('/api/organizations/stats', methods=['GET'])
@login_required
def api_get_organization_stats():
    """조직 통계 API (멀티테넌시 적용, 동적 유형 포함)"""
    from app.domains.company.services import organization_type_config_service

    root_org_id = get_current_root_organization_id()
    company_id = session.get(SessionKeys.COMPANY_ID)
    stats = organization_service.get_organization_statistics(root_organization_id=root_org_id)

    # 활성화된 조직유형 정보 포함
    active_types = []
    if company_id:
        type_configs = organization_type_config_service.get_active_type_models(company_id)
        for config in type_configs:
            active_types.append({
                'code': config.type_code,
                'label': config.type_label_ko,
                'icon': config.icon,
                'count': stats.get('by_type', {}).get(config.type_code, 0)
            })

    return api_success({
        'total': stats.get('total', 0),
        'by_type': stats.get('by_type', {}),
        'active_types': active_types
    })


@admin_bp.route('/api/organizations/<int:org_id>', methods=['GET'])
@login_required
def api_get_organization(org_id):
    """조직 상세 조회 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()

    # 멀티테넌시 검증
    if root_org_id and not organization_service.verify_ownership(org_id, root_org_id):
        return api_not_found('조직')

    org = organization_service.get_by_id(org_id)
    if not org:
        return api_not_found('조직')

    # 소속인원 추가
    org['member_count'] = organization_service.get_member_count(org_id, root_org_id)

    return api_success(org)


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
    department_phone = data.get('department_phone', '').strip() or None
    department_email = data.get('department_email', '').strip() or None

    # 필수 값 검증
    if not name:
        return api_error('조직명은 필수입니다.')

    # parent_id가 없는 경우 현재 회사의 root_organization_id를 기본값으로 설정
    if not parent_id and root_org_id:
        parent_id = root_org_id

    # 코드 중복 검사 (테넌트 범위 내)
    if code and organization_service.code_exists(code, root_organization_id=root_org_id):
        return api_error('이미 사용 중인 조직 코드입니다.')

    try:
        org = organization_service.create_organization(
            name=name,
            org_type=org_type,
            parent_id=parent_id,
            code=code,
            manager_id=manager_id,
            description=description,
            root_organization_id=root_org_id,
            department_phone=department_phone,
            department_email=department_email
        )
        return api_success({'data': org.to_dict()}, status_code=201)

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_server_error(str(e))


@admin_bp.route('/api/organizations/<int:org_id>', methods=['PUT'])
@admin_required
def api_update_organization(org_id):
    """조직 수정 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    data = request.get_json()

    # 멀티테넌시 검증
    if root_org_id and not organization_service.verify_ownership(org_id, root_org_id):
        return api_not_found('조직')

    # 코드 중복 검사 (자기 자신 제외, 테넌트 범위 내)
    code = data.get('code', '').strip() or None
    if code and organization_service.code_exists(code, exclude_id=org_id, root_organization_id=root_org_id):
        return api_error('이미 사용 중인 조직 코드입니다.')

    try:
        org = organization_service.update_organization(org_id, data, root_organization_id=root_org_id)
        if not org:
            return api_not_found('조직')

        return api_success({'data': org.to_dict()})

    except ValueError as e:
        return api_error(str(e))
    except Exception as e:
        return api_server_error(str(e))


@admin_bp.route('/api/organizations/<int:org_id>', methods=['DELETE'])
@admin_required
def api_delete_organization(org_id):
    """조직 비활성화 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    cascade = request.args.get('cascade', 'false').lower() == 'true'

    try:
        if organization_service.deactivate(org_id, cascade=cascade, root_organization_id=root_org_id):
            return api_success(message='조직이 비활성화되었습니다.')
        else:
            return api_not_found('조직')

    except Exception as e:
        return api_server_error(str(e))


@admin_bp.route('/api/organizations/<int:org_id>/move', methods=['POST'])
@admin_required
def api_move_organization(org_id):
    """조직 이동 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    data = request.get_json()
    new_parent_id = data.get('parent_id')

    try:
        if organization_service.move_organization(org_id, new_parent_id, root_organization_id=root_org_id):
            return api_success(message='조직이 이동되었습니다.')
        else:
            return api_error('조직 이동에 실패했습니다.')

    except Exception as e:
        return api_server_error(str(e))


@admin_bp.route('/api/organizations/<int:org_id>/children', methods=['GET'])
@login_required
def api_get_children(org_id):
    """하위 조직 목록 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    children = organization_service.get_children(org_id, root_organization_id=root_org_id)
    return api_success(children)


@admin_bp.route('/api/organizations/reorder', methods=['POST'])
@admin_required
def api_reorder_children():
    """하위 조직 순서 변경 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    data = request.get_json()
    parent_id = data.get('parent_id')
    org_ids = data.get('org_ids', [])

    if not org_ids or not isinstance(org_ids, list):
        return api_error('유효한 조직 ID 목록이 필요합니다.')

    try:
        if organization_service.reorder_children(parent_id, org_ids, root_organization_id=root_org_id):
            return api_success(message='순서가 저장되었습니다.')
        else:
            return api_error('순서 변경에 실패했습니다.')
    except Exception as e:
        return api_server_error(str(e))


@admin_bp.route('/api/organizations/search', methods=['GET'])
@login_required
def api_search_organizations():
    """조직 검색 API (멀티테넌시 적용)"""
    root_org_id = get_current_root_organization_id()
    query = request.args.get('q', '').strip()
    if not query:
        return api_success([])

    results = organization_service.search(query, root_organization_id=root_org_id)
    return api_success(results)


@admin_bp.route('/api/organizations/employees', methods=['GET'])
@login_required
def api_get_employees_for_org():
    """조직장 선택을 위한 직원 목록 API (멀티테넌시 적용)"""
    company_id = session.get(SessionKeys.COMPANY_ID)

    if not company_id:
        return api_success([])

    # employee_repo.find_by_company_id는 Employee 모델 리스트 반환
    employees = employee_service.employee_repo.find_by_company_id(company_id)
    # 직원 정보를 select 옵션용으로 변환
    data = [
        {
            'id': emp.id,
            'name': emp.name,
            'position': emp.position
        }
        for emp in employees
    ]
    return api_success(data)


# ===== 감사 대시보드 (UI) =====

@admin_bp.route('/audit')
@login_required
@admin_required
def audit_dashboard():
    """감사 대시보드 페이지"""
    return render_template('domains/platform/admin/audit_dashboard.html')
