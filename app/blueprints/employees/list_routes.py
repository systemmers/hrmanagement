"""
직원 목록 라우트

직원 목록 조회 및 API 엔드포인트를 제공합니다.

21번 원칙 확장: 직원 계약 상태 표시 및 계약 요청 기능
Phase 8: 상수 모듈 적용
Phase 9: 통합 계약 필터 서비스 적용 (N+1 쿼리 제거)
Phase 24: Option A - isinstance 체크 제거 (Service가 Dict 보장)
"""
from flask import Blueprint, render_template, request, jsonify, session

from ...constants.session_keys import SessionKeys, AccountType
from ...utils.decorators import manager_or_admin_required
from ...utils.tenant import get_current_organization_id
from ...services.employee_service import employee_service
from ...services.contract_service import contract_service
from ...services.contract_filter_service import contract_filter_service
from ...services.user_service import user_service
from ...models.user import User


def register_list_routes(bp: Blueprint):
    """목록 조회 라우트를 Blueprint에 등록"""

    @bp.route('/employees')
    @manager_or_admin_required
    def employee_list():
        """직원 목록 - 매니저/관리자만 접근 가능 (멀티테넌시 적용)"""
        org_id = get_current_organization_id()

        # 필터 파라미터 추출
        departments = request.args.getlist('department')
        positions = request.args.getlist('position')
        statuses = request.args.getlist('status')

        # 정렬 파라미터 추출
        sort_by = request.args.get('sort', None)
        sort_order = request.args.get('order', 'asc')

        # 정렬 필드 매핑 (camelCase -> snake_case)
        sort_field_map = {
            'id': 'id',
            'name': 'name',
            'department': 'department',
            'position': 'position',
            'hireDate': 'hire_date',
            'status': 'status'
        }
        sort_column = sort_field_map.get(sort_by) if sort_by else None

        # 단일 값도 지원 (하위 호환성)
        department = request.args.get('department', None) if not departments else None
        position = request.args.get('position', None) if not positions else None
        status = request.args.get('status', None) if not statuses else None

        # 다중 필터 적용 (organization_id 필터 추가)
        if departments or positions or statuses or sort_column:
            employees = employee_service.filter_employees(
                departments=departments if departments else None,
                positions=positions if positions else None,
                statuses=statuses if statuses else None,
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )
        elif department or position or status:
            employees = employee_service.filter_employees(
                department=department,
                position=position,
                status=status,
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )
        else:
            employees = employee_service.filter_employees(
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )

        # 21번 원칙: 계약 approved인 직원만 표시
        # Phase 9: 벌크 조회로 N+1 쿼리 제거
        company_id = session.get(SessionKeys.COMPANY_ID)

        if not company_id:
            employees_with_contract = []
        else:
            # 벌크 조회: 모든 employee_number에 대해 한번에 계약 조회
            # Phase 24: filter_employees()가 항상 Dict 리스트 반환하므로 isinstance 불필요
            employee_numbers = [
                emp.get('employee_number')
                for emp in employees
            ]
            contract_map = contract_filter_service.get_contracts_by_employee_numbers(
                employee_numbers=employee_numbers,
                company_id=company_id,
                statuses=['approved'],
                exclude_resigned=True
            )

            employees_with_contract = []
            for emp in employees:
                # Phase 24: emp는 항상 Dict (isinstance 체크 제거)
                employee_number = emp.get('employee_number')

                # 퇴사 직원 제외 (resignation_date가 있으면 퇴사 처리된 직원)
                if emp.get('resignation_date'):
                    continue

                # 벌크 조회 결과에서 계약 확인
                contract = contract_map.get(employee_number)
                if contract:
                    emp['user_id'] = contract.person_user_id
                    emp['user_email'] = (
                        contract.person_user.email
                        if contract.person_user else None
                    )
                    emp['contract_status'] = contract.status
                    employees_with_contract.append(emp)

        classification_options = employee_service.get_classification_options()
        return render_template('employees/list.html',
                               employees=employees_with_contract,
                               classification_options=classification_options)

    @bp.route('/employees/pending')
    @manager_or_admin_required
    def employee_pending_list():
        """계약대기 목록 - 계약 없거나 대기 중인 직원"""
        company_id = session.get(SessionKeys.COMPANY_ID)
        if not company_id:
            return render_template('employees/pending_list.html',
                                   employees=[],
                                   pending_count=0)

        # employee_sub 계정 중 계약 없거나 pending인 경우
        pending_employees = []
        users = user_service.get_employee_sub_users_with_employee(company_id)

        for user in users:
            # 해당 법인과의 계약 상태 확인
            contract_status = contract_service.get_employee_contract_status(
                user.id, company_id
            )

            # 계약 없음 또는 pending (requested)
            if contract_status in ['none', 'requested', 'pending']:
                employee = employee_service.get_employee_model_by_id(user.employee_id)
                if employee:
                    emp_dict = employee.to_dict()
                    emp_dict['user_id'] = user.id
                    emp_dict['user_email'] = user.email
                    emp_dict['contract_status'] = contract_status
                    pending_employees.append(emp_dict)

        return render_template('employees/pending_list.html',
                               employees=pending_employees,
                               pending_count=len(pending_employees))

    @bp.route('/api/employees')
    @manager_or_admin_required
    def api_employee_list():
        """직원 목록 API - 내보내기 등에서 사용"""
        try:
            org_id = get_current_organization_id()
            employees = employee_service.get_all_employees(organization_id=org_id)

            # 직원 데이터를 딕셔너리로 변환
            employee_list = []
            for emp in employees:
                emp_dict = emp.to_dict() if hasattr(emp, 'to_dict') else emp
                employee_list.append({
                    'id': emp_dict.get('id'),
                    'employee_number': emp_dict.get('employee_number', ''),
                    'name': emp_dict.get('name', ''),
                    'department': emp_dict.get('department', ''),
                    'position': emp_dict.get('position', ''),
                    'email': emp_dict.get('email', ''),
                    'phone': emp_dict.get('phone', ''),
                    'hire_date': str(emp_dict.get('hire_date', '')) if emp_dict.get('hire_date') else '',
                    'status': emp_dict.get('status', '')
                })

            return jsonify({
                'success': True,
                'employees': employee_list,
                'total': len(employee_list)
            })
        except Exception as e:
            return jsonify({
                'success': False,
                'error': str(e)
            }), 500
