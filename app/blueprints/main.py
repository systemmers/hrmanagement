"""
메인 페이지 Blueprint

대시보드 및 검색 기능을 제공합니다.
Phase 2: Service 계층 표준화
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from ..constants.session_keys import SessionKeys, AccountType, UserRole
from ..services.employee_service import employee_service
from ..utils.decorators import login_required
from ..utils.tenant import get_current_organization_id

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """메인 페이지

    비로그인: 랜딩페이지
    로그인: 계정 유형에 따라 적절한 대시보드로 리다이렉트
    """
    # 비로그인 사용자는 랜딩페이지로
    if not session.get(SessionKeys.USER_ID):
        return render_template('landing.html')

    account_type = session.get(SessionKeys.ACCOUNT_TYPE)

    # 개인 계정은 개인 대시보드로
    if account_type == AccountType.PERSONAL:
        return redirect(url_for('personal.dashboard'))

    # 법인 계정(corporate) 또는 직원 하위계정(employee_sub)인 경우
    # Employee role은 대시보드로 리다이렉트
    if session.get(SessionKeys.USER_ROLE) == 'employee':
        employee_id = session.get(SessionKeys.EMPLOYEE_ID)
        if employee_id:
            return redirect(url_for('profile.dashboard'))
        else:
            # employee_id가 없는 경우 (계정이 직원과 연결되지 않음)
            from flask import flash
            flash('계정에 연결된 직원 정보가 없습니다. 관리자에게 문의하세요.', 'warning')
            return redirect(url_for('auth.logout'))

    # 멀티테넌시: 현재 회사의 organization_id로 필터링
    org_id = get_current_organization_id()

    stats = employee_service.get_statistics(organization_id=org_id)
    dept_stats = employee_service.get_department_statistics(organization_id=org_id)
    recent_employees = employee_service.get_recent_employees(organization_id=org_id, limit=5)
    classification_options = employee_service.get_all_classification_options()
    return render_template('index.html',
                           stats=stats,
                           dept_stats=dept_stats,
                           recent_employees=recent_employees,
                           classification_options=classification_options)


@main_bp.route('/examples/data-table')
@login_required
def data_table_demo():
    """고급 데이터 테이블 데모 페이지"""
    return render_template('examples/data_table_demo.html')


@main_bp.route('/examples/styleguide')
@login_required
def styleguide():
    """스타일 가이드 페이지

    프로젝트의 모든 UI 컴포넌트와 디자인 시스템을 문서화합니다.
    """
    return render_template('examples/styleguide.html')


@main_bp.route('/search')
@login_required
def search():
    """직원 검색"""
    query = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    department_filter = request.args.get('department', '')
    position_filter = request.args.get('position', '')

    # 멀티테넌시: 현재 회사의 organization_id로 필터링
    org_id = get_current_organization_id()

    # 필터 적용 (organization_id 포함)
    if status_filter or department_filter or position_filter:
        employees = employee_service.filter_employees(
            organization_id=org_id,
            department=department_filter if department_filter else None,
            position=position_filter if position_filter else None,
            status=status_filter if status_filter else None
        )
    elif query:
        employees = employee_service.search_employees(query, organization_id=org_id)
    else:
        employees = employee_service.get_all_employees(organization_id=org_id)

    stats = employee_service.get_statistics(organization_id=org_id)

    # AJAX 요청인 경우 JSON 반환
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'employees': [emp.to_dict() for emp in employees],
            'stats': stats
        })

    dept_stats = employee_service.get_department_statistics(organization_id=org_id)
    recent_employees = employee_service.get_recent_employees(organization_id=org_id, limit=5)
    classification_options = employee_service.get_all_classification_options()
    return render_template('index.html',
                           employees=employees,
                           stats=stats,
                           dept_stats=dept_stats,
                           recent_employees=recent_employees,
                           search_query=query,
                           classification_options=classification_options)
