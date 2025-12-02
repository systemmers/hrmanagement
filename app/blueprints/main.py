"""
메인 페이지 Blueprint

대시보드 및 검색 기능을 제공합니다.
"""
from flask import Blueprint, render_template, request, jsonify, session, redirect, url_for

from ..extensions import employee_repo, classification_repo
from ..utils.decorators import login_required

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
@login_required
def index():
    """대시보드 - 통계 및 정보

    일반 직원(employee role)은 본인 인사카드로 리다이렉트
    """
    # Employee role은 본인 인사카드로 리다이렉트
    if session.get('user_role') == 'employee':
        employee_id = session.get('employee_id')
        if employee_id:
            return redirect(url_for('employees.employee_detail', employee_id=employee_id))
        else:
            # employee_id가 없는 경우 (계정이 직원과 연결되지 않음)
            from flask import flash
            flash('계정에 연결된 직원 정보가 없습니다. 관리자에게 문의하세요.', 'warning')
            return redirect(url_for('auth.logout'))

    stats = employee_repo.get_statistics()
    dept_stats = employee_repo.get_department_statistics()
    recent_employees = employee_repo.get_recent_employees(limit=5)
    classification_options = classification_repo.get_all_options()
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
def search():
    """직원 검색"""
    query = request.args.get('q', '')
    status_filter = request.args.get('status', '')
    department_filter = request.args.get('department', '')
    position_filter = request.args.get('position', '')

    # 필터 적용
    if status_filter or department_filter or position_filter:
        employees = employee_repo.filter_employees(
            department=department_filter if department_filter else None,
            position=position_filter if position_filter else None,
            status=status_filter if status_filter else None
        )
    elif query:
        employees = employee_repo.search(query)
    else:
        employees = employee_repo.get_all()

    stats = employee_repo.get_statistics()

    # AJAX 요청인 경우 JSON 반환
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return jsonify({
            'employees': [emp.to_dict() for emp in employees],
            'stats': stats
        })

    dept_stats = employee_repo.get_department_statistics()
    recent_employees = employee_repo.get_recent_employees(limit=5)
    classification_options = classification_repo.get_all_options()
    return render_template('index.html',
                           employees=employees,
                           stats=stats,
                           dept_stats=dept_stats,
                           recent_employees=recent_employees,
                           search_query=query,
                           classification_options=classification_options)
