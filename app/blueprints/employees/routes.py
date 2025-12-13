"""
직원 관리 라우트

직원 CRUD 및 상세 정보 관련 라우트를 제공합니다.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ...utils.employee_number import generate_employee_number
from ...utils.decorators import login_required, admin_required, manager_or_admin_required
from ...utils.tenant import get_current_organization_id
from ...extensions import (
    employee_repo, classification_repo,
    education_repo, career_repo, certificate_repo,
    family_repo, language_repo, military_repo,
    salary_repo, benefit_repo, contract_repo, salary_history_repo,
    promotion_repo, evaluation_repo, training_repo, attendance_repo,
    insurance_repo, project_repo, award_repo, asset_repo,
    salary_payment_repo, attachment_repo
)
from .helpers import (
    verify_employee_access, extract_employee_from_form, extract_basic_fields_from_form,
    update_family_data, update_education_data, update_career_data,
    update_certificate_data, update_language_data, update_military_data,
    update_project_data, update_award_data
)


def register_routes(bp: Blueprint):
    """CRUD 라우트를 Blueprint에 등록"""

    # ========================================
    # 직원 목록 및 상세
    # ========================================

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
            employees = employee_repo.filter_employees(
                departments=departments if departments else None,
                positions=positions if positions else None,
                statuses=statuses if statuses else None,
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )
        elif department or position or status:
            employees = employee_repo.filter_employees(
                department=department,
                position=position,
                status=status,
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )
        else:
            employees = employee_repo.filter_employees(
                sort_by=sort_column,
                sort_order=sort_order,
                organization_id=org_id
            )

        classification_options = classification_repo.get_all()
        return render_template('employees/list.html',
                               employees=employees,
                               classification_options=classification_options)

    @bp.route('/employees/<int:employee_id>')
    @login_required
    def employee_detail(employee_id):
        """직원 상세 정보 (멀티테넌시 적용) - 통합 템플릿 사용"""
        user_role = session.get('user_role')

        # Employee role은 본인 정보만 접근 가능
        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 열람할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_detail', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 접근 가능
        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_repo.get_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        # 모든 role에서 통합 템플릿 사용
        return _render_employee_full_view(employee_id, employee)

    def _render_employee_full_view(employee_id, employee):
        """전체 정보 페이지 렌더링 (관리자/매니저용)"""
        # 관계형 데이터 조회
        education_list = education_repo.get_by_employee_id(employee_id)
        career_list = career_repo.get_by_employee_id(employee_id)
        certificate_list = certificate_repo.get_by_employee_id(employee_id)
        family_list = family_repo.get_by_employee_id(employee_id)
        language_list = language_repo.get_by_employee_id(employee_id)
        military = military_repo.get_by_employee_id(employee_id)

        # 핵심 기능 데이터 조회
        salary = salary_repo.get_by_employee_id(employee_id)
        benefit = benefit_repo.get_by_employee_id(employee_id)
        contract = contract_repo.get_by_employee_id(employee_id)
        salary_history_list = salary_history_repo.get_by_employee_id(employee_id)

        # 인사평가 기능 데이터 조회
        promotion_list = promotion_repo.get_by_employee_id(employee_id)
        evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
        training_list = training_repo.get_by_employee_id(employee_id)
        attendance_summary = attendance_repo.get_summary_by_employee(employee_id, 2025)

        # 부가 기능 데이터 조회
        insurance = insurance_repo.get_by_employee_id(employee_id)
        project_list = project_repo.get_by_employee_id(employee_id)
        award_list = award_repo.get_by_employee_id(employee_id)
        asset_list = asset_repo.get_by_employee_id(employee_id)

        # 급여 지급 이력 조회
        salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)

        # 첨부파일 조회
        attachment_list = attachment_repo.get_by_employee_id(employee_id)

        # 명함 이미지 조회
        business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
        business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')

        # 명함 편집 권한 체크
        can_edit_business_card = (
            session.get('user_role') == 'admin' or
            (session.get('user_role') == 'employee' and session.get('employee_id') == employee_id)
        )

        return render_template('profile/detail.html',
                               employee=employee,
                               is_corporate=True,
                               account_type='corporate',
                               page_mode='hr_card',
                               education_list=education_list,
                               career_list=career_list,
                               certificate_list=certificate_list,
                               family_list=family_list,
                               language_list=language_list,
                               military=military,
                               salary=salary,
                               benefit=benefit,
                               contract=contract,
                               salary_history_list=salary_history_list,
                               promotion_list=promotion_list,
                               evaluation_list=evaluation_list,
                               training_list=training_list,
                               attendance_summary=attendance_summary,
                               insurance=insurance,
                               project_list=project_list,
                               award_list=award_list,
                               asset_list=asset_list,
                               salary_payment_list=salary_payment_list,
                               attachment_list=attachment_list,
                               business_card_front=business_card_front,
                               business_card_back=business_card_back,
                               can_edit_business_card=can_edit_business_card)

    # ========================================
    # 직원 생성
    # ========================================

    @bp.route('/employees/new', methods=['GET'])
    @manager_or_admin_required
    def employee_new():
        """직원 등록 폼 - 통합 템플릿 사용"""
        classification_options = classification_repo.get_all_options()
        return render_template('profile/edit.html',
                               employee=None,
                               action='create',
                               is_corporate=True,
                               account_type='corporate',
                               classification_options=classification_options)

    @bp.route('/employees', methods=['POST'])
    @manager_or_admin_required
    def employee_create():
        """직원 등록 처리 (멀티테넌시 적용)"""
        try:
            employee = extract_employee_from_form(request.form, employee_id=0)

            # 사번 자동 생성
            if not employee.employee_number:
                employee.employee_number = generate_employee_number()

            # organization_id 자동 설정
            org_id = get_current_organization_id()
            if org_id and not employee.organization_id:
                employee.organization_id = org_id

            # Employee 객체를 Dict로 변환하여 repository에 전달
            employee_data = employee.to_dict() if hasattr(employee, 'to_dict') else vars(employee)
            created_employee = employee_repo.create(employee_data)
            flash(f'{created_employee["name"]} 직원이 등록되었습니다. 사진과 명함을 추가해주세요.', 'success')
            return redirect(url_for('employees.employee_edit', employee_id=created_employee['id']))

        except Exception as e:
            flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_new'))

    # ========================================
    # 직원 수정 (전체)
    # ========================================

    @bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
    @login_required
    def employee_edit(employee_id):
        """직원 수정 폼 (멀티테넌시 적용)"""
        user_role = session.get('user_role')

        # Employee role은 본인 정보만 수정 가능
        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 수정 가능
        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        employee = employee_repo.get_model_by_id(employee_id)
        if not employee:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        attachment_list = attachment_repo.get_by_employee_id(employee_id)
        business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
        business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')
        classification_options = classification_repo.get_all_options()

        return render_template('profile/edit.html',
                               employee=employee,
                               action='update',
                               is_corporate=True,
                               account_type='corporate',
                               attachment_list=attachment_list,
                               business_card_front=business_card_front,
                               business_card_back=business_card_back,
                               classification_options=classification_options,
                               language_list=list(employee.languages),
                               project_list=list(employee.projects),
                               salary=employee.salary,
                               insurance=employee.insurance)

    @bp.route('/employees/<int:employee_id>/update', methods=['POST'])
    @login_required
    def employee_update(employee_id):
        """직원 수정 처리 (멀티테넌시 적용)"""
        user_role = session.get('user_role')

        # Employee role은 본인 정보만 수정 가능
        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 수정 가능
        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            employee = extract_employee_from_form(request.form, employee_id=employee_id)
            updated_employee = employee_repo.update(employee_id, employee)
            if updated_employee:
                flash(f'{updated_employee.name} 직원 정보가 수정되었습니다.', 'success')
                return redirect(url_for('employees.employee_detail', employee_id=employee_id))
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
                return redirect(url_for('main.index'))

        except Exception as e:
            flash(f'직원 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    # ========================================
    # Employee 전용 수정 (레거시 - 통합 템플릿으로 리다이렉트)
    # ========================================

    @bp.route('/employees/<int:employee_id>/edit/basic', methods=['GET'])
    @login_required
    def employee_edit_basic(employee_id):
        """기본정보 전용 수정 폼 - 통합 템플릿으로 리다이렉트"""
        return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    @bp.route('/employees/<int:employee_id>/update/basic', methods=['POST'])
    @login_required
    def employee_update_basic(employee_id):
        """기본정보 전용 수정 처리 - 통합 라우트로 리다이렉트"""
        user_role = session.get('user_role')

        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            basic_fields = extract_basic_fields_from_form(request.form)
            updated_employee = employee_repo.update_partial(employee_id, basic_fields)
            update_family_data(employee_id, request.form)

            if updated_employee:
                flash('기본정보가 수정되었습니다.', 'success')
                return redirect(url_for('employees.employee_detail', employee_id=employee_id))
            else:
                flash('직원을 찾을 수 없습니다.', 'error')
                return redirect(url_for('main.index'))

        except Exception as e:
            flash(f'기본정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    @bp.route('/employees/<int:employee_id>/edit/history', methods=['GET'])
    @login_required
    def employee_edit_history(employee_id):
        """이력정보 전용 수정 폼 - 통합 템플릿으로 리다이렉트"""
        return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    @bp.route('/employees/<int:employee_id>/update/history', methods=['POST'])
    @login_required
    def employee_update_history(employee_id):
        """이력정보 전용 수정 처리"""
        user_role = session.get('user_role')

        if user_role == 'employee':
            my_employee_id = session.get('employee_id')
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        if user_role in ['admin', 'manager']:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            update_education_data(employee_id, request.form)
            update_career_data(employee_id, request.form)
            update_certificate_data(employee_id, request.form)
            update_language_data(employee_id, request.form)
            update_military_data(employee_id, request.form)
            update_project_data(employee_id, request.form)
            update_award_data(employee_id, request.form)

            flash('이력정보가 수정되었습니다.', 'success')
            return redirect(url_for('employees.employee_detail', employee_id=employee_id))

        except Exception as e:
            flash(f'이력정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))

    # ========================================
    # 직원 삭제
    # ========================================

    @bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
    @admin_required
    def employee_delete(employee_id):
        """직원 삭제 처리 (멀티테넌시 적용)"""
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

        try:
            employee = employee_repo.get_by_id(employee_id)
            if employee:
                if employee_repo.delete(employee_id):
                    flash(f'{employee.name} 직원이 삭제되었습니다.', 'success')
                else:
                    flash('직원 삭제에 실패했습니다.', 'error')
            else:
                flash('직원을 찾을 수 없습니다.', 'error')

        except Exception as e:
            flash(f'직원 삭제 중 오류가 발생했습니다: {str(e)}', 'error')

        return redirect(url_for('main.index'))
