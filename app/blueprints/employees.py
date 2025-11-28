"""
직원 관리 Blueprint

직원 CRUD 및 관련 기능을 제공합니다.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash

from ..extensions import (
    employee_repo, classification_repo,
    education_repo, career_repo, certificate_repo,
    family_repo, language_repo, military_repo,
    salary_repo, benefit_repo, contract_repo, salary_history_repo,
    promotion_repo, evaluation_repo, training_repo, attendance_repo,
    insurance_repo, project_repo, award_repo, asset_repo,
    salary_payment_repo, attachment_repo
)
from ..models import Employee

employees_bp = Blueprint('employees', __name__)


def extract_employee_from_form(form_data, employee_id=0):
    """폼 데이터에서 Employee 객체 생성 (SSOT 헬퍼 함수)"""
    return Employee(
        id=employee_id,
        # 기본 필드
        name=form_data.get('name', ''),
        photo=form_data.get('photo') or 'https://i.pravatar.cc/150',
        department=form_data.get('department', ''),
        position=form_data.get('position', ''),
        status=form_data.get('status', 'active'),
        hireDate=form_data.get('hireDate', ''),
        phone=form_data.get('phone', ''),
        email=form_data.get('email', ''),
        # 확장 필드 - 개인정보
        name_en=form_data.get('name_en') or None,
        birth_date=form_data.get('birth_date') or None,
        gender=form_data.get('gender') or None,
        address=form_data.get('address') or None,
        emergency_contact=form_data.get('emergency_contact') or None,
        emergency_relation=form_data.get('emergency_relation') or None,
        rrn=form_data.get('rrn') or None,
        # 확장 필드 - 소속정보
        employee_number=form_data.get('employee_number') or None,
        team=form_data.get('team') or None,
        job_title=form_data.get('job_title') or None,
        work_location=form_data.get('work_location') or None,
        internal_phone=form_data.get('internal_phone') or None,
        company_email=form_data.get('company_email') or None,
        # 확장 필드 - 계약정보
        employment_type=form_data.get('employment_type') or None,
        contract_period=form_data.get('contract_period') or None,
        probation_end=form_data.get('probation_end') or None,
        resignation_date=form_data.get('resignation_date') or None
    )


@employees_bp.route('/employees')
def employee_list():
    """직원 목록"""
    # 필터 파라미터 추출
    departments = request.args.getlist('department')
    positions = request.args.getlist('position')
    statuses = request.args.getlist('status')

    # 단일 값도 지원 (하위 호환성)
    department = request.args.get('department', None)
    position = request.args.get('position', None)
    status = request.args.get('status', None)

    # 다중 필터 적용
    if departments or positions or statuses:
        employees = employee_repo.filter_employees(
            departments=departments if departments else None,
            positions=positions if positions else None,
            statuses=statuses if statuses else None
        )
    elif department or position or status:
        employees = employee_repo.filter_employees(
            department=department,
            position=position,
            status=status
        )
    else:
        employees = employee_repo.get_all()

    # 분류 옵션 전달
    classification_options = classification_repo.get_all()
    return render_template('employee_list.html',
                           employees=employees,
                           classification_options=classification_options)


@employees_bp.route('/employees/<int:employee_id>')
def employee_detail(employee_id):
    """직원 상세 정보"""
    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 관계형 데이터 조회
    education_list = education_repo.get_by_employee_id(employee_id)
    career_list = career_repo.get_by_employee_id(employee_id)
    certificate_list = certificate_repo.get_by_employee_id(employee_id)
    family_list = family_repo.get_by_employee_id(employee_id)
    language_list = language_repo.get_by_employee_id(employee_id)
    military = military_repo.get_by_employee_id(employee_id)

    # Phase 2: 핵심 기능 데이터 조회
    salary = salary_repo.get_by_employee_id(employee_id)
    benefit = benefit_repo.get_by_employee_id(employee_id)
    contract = contract_repo.get_by_employee_id(employee_id)
    salary_history_list = salary_history_repo.get_by_employee_id(employee_id)

    # Phase 3: 인사평가 기능 데이터 조회
    promotion_list = promotion_repo.get_by_employee_id(employee_id)
    evaluation_list = evaluation_repo.get_by_employee_id(employee_id)
    training_list = training_repo.get_by_employee_id(employee_id)
    attendance_summary = attendance_repo.get_summary_by_employee(employee_id, 2025)

    # Phase 4: 부가 기능 데이터 조회
    insurance = insurance_repo.get_by_employee_id(employee_id)
    project_list = project_repo.get_by_employee_id(employee_id)
    award_list = award_repo.get_by_employee_id(employee_id)
    asset_list = asset_repo.get_by_employee_id(employee_id)

    # Phase 5: 급여 지급 이력 조회
    salary_payment_list = salary_payment_repo.get_by_employee_id(employee_id)

    # Phase 6: 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    return render_template('employee_detail.html',
                           employee=employee,
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
                           attachment_list=attachment_list)


@employees_bp.route('/employees/new', methods=['GET'])
def employee_new():
    """직원 등록 폼"""
    return render_template('employee_form.html', employee=None, action='create')


@employees_bp.route('/employees', methods=['POST'])
def employee_create():
    """직원 등록 처리"""
    try:
        employee = extract_employee_from_form(request.form, employee_id=0)

        created_employee = employee_repo.create(employee)
        flash(f'{created_employee.name} 직원이 등록되었습니다.', 'success')
        return redirect(url_for('employees.employee_detail', employee_id=created_employee.id))

    except Exception as e:
        flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employees.employee_new'))


@employees_bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
def employee_edit(employee_id):
    """직원 수정 폼"""
    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # Phase 6: 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    return render_template('employee_form.html',
                           employee=employee,
                           action='update',
                           attachment_list=attachment_list)


@employees_bp.route('/employees/<int:employee_id>/update', methods=['POST'])
def employee_update(employee_id):
    """직원 수정 처리"""
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


@employees_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
def employee_delete(employee_id):
    """직원 삭제 처리"""
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
