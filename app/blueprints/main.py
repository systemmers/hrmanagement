"""
메인 페이지 Blueprint

대시보드 및 검색 기능을 제공합니다.
"""
from flask import Blueprint, render_template, request, jsonify

from ..extensions import employee_repo, classification_repo

main_bp = Blueprint('main', __name__)


@main_bp.route('/')
def index():
    """대시보드 - 통계 및 정보"""
    stats = employee_repo.get_statistics()
    dept_stats = employee_repo.get_department_statistics()
    recent_employees = employee_repo.get_recent_employees(limit=5)
    classification_options = classification_repo.get_all_options()
    return render_template('index.html',
                           stats=stats,
                           dept_stats=dept_stats,
                           recent_employees=recent_employees,
                           classification_options=classification_options)


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
