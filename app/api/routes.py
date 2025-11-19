"""
API 라우트
AJAX용 REST API
"""
from flask import jsonify, request
from flask_login import login_required
from app.api import api_bp
from app.models import Employee, Department, Position
from sqlalchemy import or_


@api_bp.route('/employees', methods=['GET'])
@login_required
def get_employees():
    """직원 목록 조회 (검색/필터)"""
    # 검색 파라미터
    query_text = request.args.get('q', '').strip()
    department_id = request.args.get('department', type=int)
    position_id = request.args.get('position', type=int)
    status = request.args.get('status', '').strip()

    # 기본 쿼리
    query = Employee.query

    # 검색 조건 적용
    if query_text:
        query = query.filter(
            or_(
                Employee.name.contains(query_text),
                Employee.phone.contains(query_text),
                Employee.email.contains(query_text)
            )
        )

    # 부서 필터
    if department_id:
        query = query.filter_by(department_id=department_id)

    # 직급 필터
    if position_id:
        query = query.filter_by(position_id=position_id)

    # 상태 필터
    if status:
        query = query.filter_by(status=status)

    # 결과 조회
    employees = query.order_by(Employee.created_at.desc()).all()

    # JSON 응답
    return jsonify({
        'success': True,
        'count': len(employees),
        'employees': [emp.to_dict() for emp in employees]
    })


@api_bp.route('/employees/<int:id>', methods=['GET'])
@login_required
def get_employee(id):
    """직원 상세 조회"""
    employee = Employee.query.get_or_404(id)

    return jsonify({
        'success': True,
        'employee': employee.to_dict()
    })


@api_bp.route('/statistics', methods=['GET'])
@login_required
def get_statistics():
    """대시보드 통계"""
    total_count = Employee.query.count()
    active_count = Employee.query.filter_by(status='active').count()
    warning_count = Employee.query.filter_by(status='warning').count()
    expired_count = Employee.query.filter_by(status='expired').count()

    # 부서별 통계
    departments = Department.query.all()
    department_stats = []
    for dept in departments:
        count = Employee.query.filter_by(department_id=dept.id).count()
        department_stats.append({
            'id': dept.id,
            'name': dept.name,
            'count': count
        })

    # 직급별 통계
    positions = Position.query.all()
    position_stats = []
    for pos in positions:
        count = Employee.query.filter_by(position_id=pos.id).count()
        position_stats.append({
            'id': pos.id,
            'name': pos.name,
            'count': count
        })

    return jsonify({
        'success': True,
        'statistics': {
            'total': total_count,
            'active': active_count,
            'warning': warning_count,
            'expired': expired_count,
            'departments': department_stats,
            'positions': position_stats
        }
    })
