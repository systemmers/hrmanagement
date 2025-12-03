"""
직원 관리 Blueprint

직원 CRUD 및 관련 기능을 제공합니다.
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app, session

from ..utils.employee_number import generate_employee_number
from ..utils.decorators import login_required, admin_required, manager_or_admin_required
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
from ..models.company import Company

employees_bp = Blueprint('employees', __name__)


# ========================================
# 멀티테넌시 헬퍼 함수
# ========================================

def get_current_organization_id():
    """현재 로그인한 회사의 root_organization_id 반환

    Returns:
        organization_id 또는 None
    """
    company_id = session.get('company_id')
    if not company_id:
        return None
    company = Company.query.get(company_id)
    return company.root_organization_id if company else None


def verify_employee_access(employee_id: int) -> bool:
    """현재 회사가 해당 직원에 접근 가능한지 확인

    Args:
        employee_id: 직원 ID

    Returns:
        접근 가능 여부
    """
    org_id = get_current_organization_id()
    if not org_id:
        return False
    return employee_repo.verify_ownership(employee_id, org_id)


def extract_employee_from_form(form_data, employee_id=0):
    """폼 데이터에서 Employee 객체 생성 (SSOT 헬퍼 함수)"""
    # organization_id 처리
    org_id = form_data.get('organization_id')
    organization_id = int(org_id) if org_id and org_id.strip() else None

    return Employee(
        id=employee_id,
        # 기본 필드
        name=form_data.get('name', ''),
        photo=form_data.get('photo') or 'https://i.pravatar.cc/150',
        department=form_data.get('department', ''),
        position=form_data.get('position', ''),
        status=form_data.get('status', 'active'),
        hire_date=form_data.get('hire_date') or form_data.get('hireDate', ''),
        phone=form_data.get('phone', ''),
        email=form_data.get('email', ''),
        # 조직 연결
        organization_id=organization_id,
        # 소속정보 추가 필드
        employee_number=form_data.get('employee_number') or None,
        team=form_data.get('team') or None,
        job_title=form_data.get('job_title') or None,
        work_location=form_data.get('work_location') or None,
        internal_phone=form_data.get('internal_phone') or None,
        company_email=form_data.get('company_email') or None,
        # 확장 필드 - 개인정보
        english_name=form_data.get('english_name') or form_data.get('name_en') or None,
        birth_date=form_data.get('birth_date') or None,
        gender=form_data.get('gender') or None,
        address=form_data.get('address') or None,
        detailed_address=form_data.get('detailed_address') or None,
        postal_code=form_data.get('postal_code') or None,
        resident_number=form_data.get('resident_number') or form_data.get('rrn') or None,
        mobile_phone=form_data.get('mobile_phone') or None,
        home_phone=form_data.get('home_phone') or None,
        nationality=form_data.get('nationality') or None,
        blood_type=form_data.get('blood_type') or None,
        religion=form_data.get('religion') or None,
        hobby=form_data.get('hobby') or None,
        specialty=form_data.get('specialty') or None,
    )


@employees_bp.route('/employees')
@manager_or_admin_required
def employee_list():
    """직원 목록 - 매니저/관리자만 접근 가능 (멀티테넌시 적용)"""
    # 현재 회사의 organization_id 가져오기
    org_id = get_current_organization_id()

    # 필터 파라미터 추출
    departments = request.args.getlist('department')
    positions = request.args.getlist('position')
    statuses = request.args.getlist('status')

    # 정렬 파라미터 추출
    sort_by = request.args.get('sort', None)
    sort_order = request.args.get('order', 'asc')

    # 정렬 필드 매핑 (camelCase → snake_case)
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

    # 분류 옵션 전달
    classification_options = classification_repo.get_all()
    return render_template('employee_list.html',
                           employees=employees,
                           classification_options=classification_options)


@employees_bp.route('/employees/<int:employee_id>')
@login_required
def employee_detail(employee_id):
    """직원 상세 정보 (멀티테넌시 적용)

    일반 직원(employee role)은 본인 정보만 열람 가능
    관리자/매니저는 자사 소속 직원만 열람 가능
    view 파라미터에 따라 다른 페이지 렌더링:
    - basic: 개인 기본정보만 (Employee role 전용)
    - history: 이력정보만 (Employee role 전용)
    - full: 전체 정보 (관리자/매니저용, 기본값)
    """
    from flask import session

    user_role = session.get('user_role')
    view_type = request.args.get('view', 'full')

    # Employee role은 본인 정보만 접근 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 열람할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_detail',
                                   employee_id=my_employee_id, view=view_type))

    # 관리자/매니저는 자사 소속 직원만 접근 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # Employee role: view 파라미터에 따라 분기
    if user_role == 'employee':
        # 기본정보 페이지
        if view_type == 'basic':
            family_list = family_repo.get_by_employee_id(employee_id)
            attachment_list = attachment_repo.get_by_employee_id(employee_id)
            return render_template('employee_detail_basic.html',
                                   employee=employee,
                                   family_list=family_list,
                                   attachment_list=attachment_list)

        # 이력정보 페이지
        elif view_type == 'history':
            education_list = education_repo.get_by_employee_id(employee_id)
            career_list = career_repo.get_by_employee_id(employee_id)
            certificate_list = certificate_repo.get_by_employee_id(employee_id)
            language_list = language_repo.get_by_employee_id(employee_id)
            military = military_repo.get_by_employee_id(employee_id)
            project_list = project_repo.get_by_employee_id(employee_id)
            award_list = award_repo.get_by_employee_id(employee_id)
            attachment_list = attachment_repo.get_by_employee_id(employee_id)
            return render_template('employee_detail_history.html',
                                   employee=employee,
                                   education_list=education_list,
                                   career_list=career_list,
                                   certificate_list=certificate_list,
                                   language_list=language_list,
                                   military=military,
                                   project_list=project_list,
                                   award_list=award_list,
                                   attachment_list=attachment_list)

        # 기본값: basic 페이지로 리다이렉트
        else:
            return redirect(url_for('employees.employee_detail',
                                   employee_id=employee_id, view='basic'))

    # 관리자/매니저: 전체 정보 페이지 (기존 로직)
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

    # 명함 이미지 조회
    business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
    business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')

    # 명함 편집 권한 체크: 본인 또는 관리자
    can_edit_business_card = (
        session.get('user_role') == 'admin' or
        (session.get('user_role') == 'employee' and session.get('employee_id') == employee_id)
    )

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
                           attachment_list=attachment_list,
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           can_edit_business_card=can_edit_business_card)


@employees_bp.route('/employees/new', methods=['GET'])
@manager_or_admin_required
def employee_new():
    """직원 등록 폼"""
    classification_options = classification_repo.get_all_options()
    return render_template('employee_form.html',
                           employee=None,
                           action='create',
                           classification_options=classification_options)


@employees_bp.route('/employees', methods=['POST'])
@manager_or_admin_required
def employee_create():
    """직원 등록 처리 (멀티테넌시 적용)"""
    try:
        employee = extract_employee_from_form(request.form, employee_id=0)

        # 사번 자동 생성 (폼에서 입력하지 않은 경우)
        if not employee.employee_number:
            employee.employee_number = generate_employee_number()

        # organization_id 자동 설정 (멀티테넌시)
        org_id = get_current_organization_id()
        if org_id and not employee.organization_id:
            employee.organization_id = org_id

        created_employee = employee_repo.create(employee)
        flash(f'{created_employee.name} 직원이 등록되었습니다. 사진과 명함을 추가해주세요.', 'success')
        # 신규 등록 완료 후 수정 페이지로 리다이렉트 (사진/명함 업로드 가능)
        return redirect(url_for('employees.employee_edit', employee_id=created_employee.id))

    except Exception as e:
        flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employees.employee_new'))


@employees_bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
@login_required
def employee_edit(employee_id):
    """직원 수정 폼 (멀티테넌시 적용)

    - 관리자/매니저: 자사 소속 직원 수정 가능
    - 일반 직원: 본인 정보만 수정 가능 (일부 필드 제한)
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # Phase 6: 첨부파일 조회
    attachment_list = attachment_repo.get_by_employee_id(employee_id)

    # 명함 이미지 조회
    business_card_front = attachment_repo.get_one_by_category(employee_id, 'business_card_front')
    business_card_back = attachment_repo.get_one_by_category(employee_id, 'business_card_back')

    # 분류 옵션 조회
    classification_options = classification_repo.get_all_options()

    return render_template('employee_form.html',
                           employee=employee,
                           action='update',
                           attachment_list=attachment_list,
                           business_card_front=business_card_front,
                           business_card_back=business_card_back,
                           classification_options=classification_options)


# ========================================
# Employee 전용 수정 라우트 (기본정보/이력정보 분리)
# ========================================

@employees_bp.route('/employees/<int:employee_id>/edit/basic', methods=['GET'])
@login_required
def employee_edit_basic(employee_id):
    """기본정보 전용 수정 폼 (Employee role 전용, 멀티테넌시 적용)

    개인 기본정보와 가족정보만 수정 가능
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit_basic', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 가족정보 조회
    family_list = family_repo.get_by_employee_id(employee_id)

    return render_template('employee_form_basic.html',
                           employee=employee,
                           family_list=family_list,
                           action='update')


@employees_bp.route('/employees/<int:employee_id>/update/basic', methods=['POST'])
@login_required
def employee_update_basic(employee_id):
    """기본정보 전용 수정 처리 (Employee role 전용, 멀티테넌시 적용)

    개인 기본정보와 가족정보만 업데이트
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit_basic', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    try:
        # 기본정보 필드만 추출하여 업데이트
        basic_fields = {
            'name': request.form.get('name', ''),
            'photo': request.form.get('photo') or 'https://i.pravatar.cc/150',
            'english_name': request.form.get('english_name') or request.form.get('name_en') or None,
            'birth_date': request.form.get('birth_date') or None,
            'gender': request.form.get('gender') or None,
            'phone': request.form.get('phone', ''),
            'email': request.form.get('email', ''),
            'mobile_phone': request.form.get('mobile_phone') or None,
            'home_phone': request.form.get('home_phone') or None,
            'address': request.form.get('address') or None,
            'detailed_address': request.form.get('detailed_address') or None,
            'postal_code': request.form.get('postal_code') or None,
            'resident_number': request.form.get('resident_number') or request.form.get('rrn') or None,
            'nationality': request.form.get('nationality') or None,
            'blood_type': request.form.get('blood_type') or None,
            'religion': request.form.get('religion') or None,
            'hobby': request.form.get('hobby') or None,
            'specialty': request.form.get('specialty') or None,
        }

        # 기본정보만 업데이트
        updated_employee = employee_repo.update_partial(employee_id, basic_fields)

        # 가족정보 업데이트 처리
        _update_family_data(employee_id, request.form)

        if updated_employee:
            flash('기본정보가 수정되었습니다.', 'success')
            return redirect(url_for('employees.employee_detail', employee_id=employee_id, view='basic'))
        else:
            flash('직원을 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

    except Exception as e:
        flash(f'기본정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employees.employee_edit_basic', employee_id=employee_id))


@employees_bp.route('/employees/<int:employee_id>/edit/history', methods=['GET'])
@login_required
def employee_edit_history(employee_id):
    """이력정보 전용 수정 폼 (Employee role 전용, 멀티테넌시 적용)

    학력, 경력, 자격증, 언어능력, 병역/프로젝트/수상 수정 가능
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit_history', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    employee = employee_repo.get_by_id(employee_id)
    if not employee:
        flash('직원을 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 이력정보 데이터 조회
    education_list = education_repo.get_by_employee_id(employee_id)
    career_list = career_repo.get_by_employee_id(employee_id)
    certificate_list = certificate_repo.get_by_employee_id(employee_id)
    language_list = language_repo.get_by_employee_id(employee_id)
    military = military_repo.get_by_employee_id(employee_id)
    project_list = project_repo.get_by_employee_id(employee_id)
    award_list = award_repo.get_by_employee_id(employee_id)

    return render_template('employee_form_history.html',
                           employee=employee,
                           education_list=education_list,
                           career_list=career_list,
                           certificate_list=certificate_list,
                           language_list=language_list,
                           military=military,
                           project_list=project_list,
                           award_list=award_list,
                           action='update')


@employees_bp.route('/employees/<int:employee_id>/update/history', methods=['POST'])
@login_required
def employee_update_history(employee_id):
    """이력정보 전용 수정 처리 (Employee role 전용, 멀티테넌시 적용)

    학력, 경력, 자격증, 언어능력, 병역/프로젝트/수상만 업데이트
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit_history', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
    if user_role in ['admin', 'manager']:
        if not verify_employee_access(employee_id):
            flash('접근 권한이 없습니다.', 'error')
            return redirect(url_for('main.index'))

    try:
        # 이력정보 업데이트 처리 (각 관계형 데이터)
        _update_education_data(employee_id, request.form)
        _update_career_data(employee_id, request.form)
        _update_certificate_data(employee_id, request.form)
        _update_language_data(employee_id, request.form)
        _update_military_data(employee_id, request.form)
        _update_project_data(employee_id, request.form)
        _update_award_data(employee_id, request.form)

        flash('이력정보가 수정되었습니다.', 'success')
        return redirect(url_for('employees.employee_detail', employee_id=employee_id, view='history'))

    except Exception as e:
        flash(f'이력정보 수정 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employees.employee_edit_history', employee_id=employee_id))


# ========================================
# 관계형 데이터 업데이트 헬퍼 함수
# ========================================

def _update_family_data(employee_id, form_data):
    """가족정보 업데이트"""
    # 기존 데이터 삭제 후 새로 입력
    family_repo.delete_by_employee_id(employee_id)

    # 폼에서 가족정보 추출
    relations = form_data.getlist('family_relation[]')
    names = form_data.getlist('family_name[]')
    birth_dates = form_data.getlist('family_birth_date[]')
    occupations = form_data.getlist('family_occupation[]')
    phones = form_data.getlist('family_phone[]')
    cohabitings = form_data.getlist('family_cohabiting[]')

    from ..models import Family
    for i in range(len(relations)):
        if relations[i] and names[i]:  # 필수 필드가 있는 경우만
            family = Family(
                employee_id=employee_id,
                relation=relations[i],
                name=names[i],
                birth_date=birth_dates[i] if i < len(birth_dates) else None,
                occupation=occupations[i] if i < len(occupations) else None,
                phone=phones[i] if i < len(phones) else None,
                cohabiting=cohabitings[i] if i < len(cohabitings) else None
            )
            family_repo.create(family)


def _update_education_data(employee_id, form_data):
    """학력정보 업데이트"""
    education_repo.delete_by_employee_id(employee_id)

    school_types = form_data.getlist('education_school_type[]')
    school_names = form_data.getlist('education_school_name[]')
    graduation_years = form_data.getlist('education_graduation_year[]')
    majors = form_data.getlist('education_major[]')
    degrees = form_data.getlist('education_degree[]')
    gpas = form_data.getlist('education_gpa[]')
    graduation_statuses = form_data.getlist('education_graduation_status[]')

    from ..models import Education
    for i in range(len(school_names)):
        if school_names[i]:
            education = Education(
                employee_id=employee_id,
                school_type=school_types[i] if i < len(school_types) else None,
                school_name=school_names[i],
                graduation_year=graduation_years[i] if i < len(graduation_years) else None,
                major=majors[i] if i < len(majors) else None,
                degree=degrees[i] if i < len(degrees) else None,
                gpa=gpas[i] if i < len(gpas) else None,
                graduation_status=graduation_statuses[i] if i < len(graduation_statuses) else None
            )
            education_repo.create(education)


def _update_career_data(employee_id, form_data):
    """경력정보 업데이트"""
    career_repo.delete_by_employee_id(employee_id)

    company_names = form_data.getlist('career_company_name[]')
    start_dates = form_data.getlist('career_start_date[]')
    end_dates = form_data.getlist('career_end_date[]')
    departments = form_data.getlist('career_department[]')
    positions = form_data.getlist('career_position[]')
    duties = form_data.getlist('career_duties[]')

    from ..models import Career
    for i in range(len(company_names)):
        if company_names[i]:
            career = Career(
                employee_id=employee_id,
                company_name=company_names[i],
                start_date=start_dates[i] if i < len(start_dates) else None,
                end_date=end_dates[i] if i < len(end_dates) else None,
                department=departments[i] if i < len(departments) else None,
                position=positions[i] if i < len(positions) else None,
                duties=duties[i] if i < len(duties) else None
            )
            career_repo.create(career)


def _update_certificate_data(employee_id, form_data):
    """자격증정보 업데이트"""
    certificate_repo.delete_by_employee_id(employee_id)

    cert_types = form_data.getlist('certificate_type[]')
    cert_names = form_data.getlist('certificate_name[]')
    cert_grades = form_data.getlist('certificate_grade[]')
    cert_issuers = form_data.getlist('certificate_issuer[]')
    cert_dates = form_data.getlist('certificate_date[]')

    from ..models import Certificate
    for i in range(len(cert_names)):
        if cert_names[i]:
            certificate = Certificate(
                employee_id=employee_id,
                cert_type=cert_types[i] if i < len(cert_types) else None,
                cert_name=cert_names[i],
                grade=cert_grades[i] if i < len(cert_grades) else None,
                issuer=cert_issuers[i] if i < len(cert_issuers) else None,
                acquisition_date=cert_dates[i] if i < len(cert_dates) else None
            )
            certificate_repo.create(certificate)


def _update_language_data(employee_id, form_data):
    """언어능력정보 업데이트"""
    language_repo.delete_by_employee_id(employee_id)

    languages = form_data.getlist('language_name[]')
    levels = form_data.getlist('language_level[]')
    test_names = form_data.getlist('language_test_name[]')
    scores = form_data.getlist('language_score[]')
    test_dates = form_data.getlist('language_test_date[]')

    from ..models import Language
    for i in range(len(languages)):
        if languages[i]:
            language = Language(
                employee_id=employee_id,
                language=languages[i],
                level=levels[i] if i < len(levels) else None,
                test_name=test_names[i] if i < len(test_names) else None,
                score=scores[i] if i < len(scores) else None,
                test_date=test_dates[i] if i < len(test_dates) else None
            )
            language_repo.create(language)


def _update_military_data(employee_id, form_data):
    """병역정보 업데이트"""
    military_repo.delete_by_employee_id(employee_id)

    military_status = form_data.get('military_status')
    if military_status:
        from ..models import Military
        military = Military(
            employee_id=employee_id,
            military_status=military_status,
            branch=form_data.get('military_branch') or None,
            start_date=form_data.get('military_start_date') or None,
            end_date=form_data.get('military_end_date') or None,
            rank=form_data.get('military_rank') or None,
            specialty=form_data.get('military_specialty') or None,
            discharge_reason=form_data.get('military_discharge_reason') or None
        )
        military_repo.create(military)


def _update_project_data(employee_id, form_data):
    """프로젝트정보 업데이트"""
    project_repo.delete_by_employee_id(employee_id)

    project_names = form_data.getlist('project_name[]')
    start_dates = form_data.getlist('project_start_date[]')
    end_dates = form_data.getlist('project_end_date[]')
    duties = form_data.getlist('project_duties[]')
    roles = form_data.getlist('project_role[]')
    clients = form_data.getlist('project_client[]')

    from ..models import Project
    for i in range(len(project_names)):
        if project_names[i]:
            project = Project(
                employee_id=employee_id,
                project_name=project_names[i],
                start_date=start_dates[i] if i < len(start_dates) else None,
                end_date=end_dates[i] if i < len(end_dates) else None,
                duties=duties[i] if i < len(duties) else None,
                role=roles[i] if i < len(roles) else None,
                client=clients[i] if i < len(clients) else None
            )
            project_repo.create(project)


def _update_award_data(employee_id, form_data):
    """수상정보 업데이트"""
    award_repo.delete_by_employee_id(employee_id)

    award_dates = form_data.getlist('award_date[]')
    award_names = form_data.getlist('award_name[]')
    award_issuers = form_data.getlist('award_issuer[]')
    award_notes = form_data.getlist('award_note[]')

    from ..models import Award
    for i in range(len(award_names)):
        if award_names[i]:
            award = Award(
                employee_id=employee_id,
                award_date=award_dates[i] if i < len(award_dates) else None,
                award_name=award_names[i],
                issuer=award_issuers[i] if i < len(award_issuers) else None,
                note=award_notes[i] if i < len(award_notes) else None
            )
            award_repo.create(award)


@employees_bp.route('/employees/<int:employee_id>/update', methods=['POST'])
@login_required
def employee_update(employee_id):
    """직원 수정 처리 (멀티테넌시 적용)

    - 관리자/매니저: 자사 소속 직원 수정 가능
    - 일반 직원: 본인 정보만 수정 가능
    """
    from flask import session

    user_role = session.get('user_role')

    # Employee role은 본인 정보만 수정 가능
    if user_role == 'employee':
        my_employee_id = session.get('employee_id')
        if my_employee_id != employee_id:
            flash('본인 정보만 수정할 수 있습니다.', 'warning')
            return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

    # 관리자/매니저는 자사 소속 직원만 수정 가능 (멀티테넌시 검증)
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


@employees_bp.route('/employees/<int:employee_id>/delete', methods=['POST'])
@admin_required
def employee_delete(employee_id):
    """직원 삭제 처리 (멀티테넌시 적용)"""
    # 관리자는 자사 소속 직원만 삭제 가능 (멀티테넌시 검증)
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


# ========================================
# 첨부파일 API
# ========================================

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    """허용된 파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_upload_folder():
    """업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


@employees_bp.route('/api/employees/<int:employee_id>/attachments', methods=['GET'])
@login_required
def get_attachments(employee_id):
    """직원 첨부파일 목록 조회 API"""
    try:
        attachments = attachment_repo.get_by_employee_id(employee_id)
        return jsonify({'success': True, 'attachments': attachments})
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employees_bp.route('/api/employees/<int:employee_id>/attachments', methods=['POST'])
@manager_or_admin_required
def upload_attachment(employee_id):
    """첨부파일 업로드 API"""
    try:
        # 직원 존재 확인
        employee = employee_repo.get_by_id(employee_id)
        if not employee:
            return jsonify({'success': False, 'error': '직원을 찾을 수 없습니다.'}), 404

        # 파일 검증
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다.'}), 400

        if not allowed_file(file.filename):
            return jsonify({'success': False, 'error': '허용되지 않는 파일 형식입니다.'}), 400

        # 파일 크기 확인
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return jsonify({'success': False, 'error': '파일 크기가 10MB를 초과합니다.'}), 400

        # 파일 저장
        filename = secure_filename(file.filename)
        ext = filename.rsplit('.', 1)[1].lower()
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{employee_id}_{timestamp}_{filename}"

        upload_folder = get_upload_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 웹 접근 경로
        web_path = f"/static/uploads/attachments/{unique_filename}"

        # 카테고리 (폼에서 전달)
        category = request.form.get('category', '기타')

        # DB 저장 (딕셔너리 형태로 전달)
        attachment_data = {
            'employeeId': employee_id,
            'fileName': filename,
            'filePath': web_path,
            'fileType': ext,
            'fileSize': file_size,
            'category': category,
            'uploadDate': datetime.now().strftime('%Y-%m-%d')
        }
        created = attachment_repo.create(attachment_data)

        return jsonify({
            'success': True,
            'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employees_bp.route('/api/attachments/<int:attachment_id>', methods=['DELETE'])
@manager_or_admin_required
def delete_attachment(attachment_id):
    """첨부파일 삭제 API"""
    try:
        # 첨부파일 조회
        attachment = attachment_repo.get_by_id(attachment_id)
        if not attachment:
            return jsonify({'success': False, 'error': '첨부파일을 찾을 수 없습니다.'}), 404

        # 파일 경로 추출 (딕셔너리 또는 객체 처리)
        file_path = attachment.get('file_path') if isinstance(attachment, dict) else attachment.file_path

        # 실제 파일 삭제
        if file_path:
            full_path = os.path.join(current_app.root_path, file_path.lstrip('/'))
            if os.path.exists(full_path):
                os.remove(full_path)

        # DB에서 삭제
        attachment_repo.delete(attachment_id)

        return jsonify({'success': True})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# 프로필 사진 API
# ========================================

def get_profile_photo_folder():
    """프로필 사진 업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_photos')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


@employees_bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['POST'])
@login_required
def upload_profile_photo(employee_id):
    """프로필 사진 업로드 API"""
    try:
        # 권한 체크: 본인 또는 관리자/매니저
        user_role = session.get('user_role')
        is_admin_or_manager = user_role in ['admin', 'manager']
        is_self = session.get('employee_id') == employee_id
        if not is_admin_or_manager and not is_self:
            return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403

        # 직원 존재 확인
        employee = employee_repo.get_by_id(employee_id)
        if not employee:
            return jsonify({'success': False, 'error': '직원을 찾을 수 없습니다.'}), 404

        # 파일 검증
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다.'}), 400

        # 이미지 파일만 허용
        allowed_image_ext = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_image_ext:
            return jsonify({'success': False, 'error': '이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)'}), 400

        # 파일 크기 확인 (5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 5 * 1024 * 1024:
            return jsonify({'success': False, 'error': '파일 크기가 5MB를 초과합니다.'}), 400

        category = 'profile_photo'

        # 기존 프로필 사진 삭제
        old_photo = attachment_repo.get_one_by_category(employee_id, category)
        if old_photo:
            old_path = old_photo.get('file_path') if isinstance(old_photo, dict) else old_photo.file_path
            if old_path:
                full_path = os.path.join(current_app.root_path, old_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            attachment_repo.delete_by_category(employee_id, category)

        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{employee_id}_profile_{timestamp}.{ext}"

        upload_folder = get_profile_photo_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 웹 접근 경로
        web_path = f"/static/uploads/profile_photos/{unique_filename}"

        # DB 저장 (Attachment 테이블)
        attachment_data = {
            'employeeId': employee_id,
            'fileName': filename,
            'filePath': web_path,
            'fileType': ext,
            'fileSize': file_size,
            'category': category,
            'uploadDate': datetime.now().strftime('%Y-%m-%d')
        }
        created = attachment_repo.create(attachment_data)

        return jsonify({
            'success': True,
            'file_path': web_path,
            'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employees_bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['GET'])
@login_required
def get_profile_photo(employee_id):
    """프로필 사진 조회 API"""
    try:
        photo = attachment_repo.get_one_by_category(employee_id, 'profile_photo')
        if photo:
            return jsonify({
                'success': True,
                'file_path': photo.get('file_path') if isinstance(photo, dict) else photo.file_path,
                'attachment': photo
            })
        else:
            return jsonify({'success': True, 'file_path': None, 'attachment': None})

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employees_bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['DELETE'])
@login_required
def delete_profile_photo(employee_id):
    """프로필 사진 삭제 API"""
    try:
        # 권한 체크: 본인 또는 관리자/매니저
        user_role = session.get('user_role')
        is_admin_or_manager = user_role in ['admin', 'manager']
        is_self = session.get('employee_id') == employee_id
        if not is_admin_or_manager and not is_self:
            return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403

        category = 'profile_photo'

        # 기존 프로필 사진 삭제
        old_photo = attachment_repo.get_one_by_category(employee_id, category)
        if old_photo:
            old_path = old_photo.get('file_path') if isinstance(old_photo, dict) else old_photo.file_path
            if old_path:
                full_path = os.path.join(current_app.root_path, old_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            attachment_repo.delete_by_category(employee_id, category)
            return jsonify({'success': True, 'message': '프로필 사진이 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '삭제할 프로필 사진이 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


# ========================================
# 명함 이미지 API
# ========================================

def get_business_card_folder():
    """명함 이미지 업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'business_cards')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


@employees_bp.route('/api/employees/<int:employee_id>/business-card', methods=['POST'])
@login_required
def upload_business_card(employee_id):
    """명함 이미지 업로드 API (앞면/뒷면)"""
    try:
        # 권한 체크: 본인 또는 관리자
        is_admin = session.get('user_role') == 'admin'
        is_self = session.get('employee_id') == employee_id
        if not is_admin and not is_self:
            return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403

        # 직원 존재 확인
        employee = employee_repo.get_by_id(employee_id)
        if not employee:
            return jsonify({'success': False, 'error': '직원을 찾을 수 없습니다.'}), 404

        # side 파라미터 검증
        side = request.form.get('side')
        if side not in ['front', 'back']:
            return jsonify({'success': False, 'error': 'side 파라미터는 front 또는 back이어야 합니다.'}), 400

        category = f'business_card_{side}'

        # 파일 검증
        if 'file' not in request.files:
            return jsonify({'success': False, 'error': '파일이 없습니다.'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'success': False, 'error': '파일이 선택되지 않았습니다.'}), 400

        # 이미지 파일만 허용
        allowed_image_ext = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
        ext = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        if ext not in allowed_image_ext:
            return jsonify({'success': False, 'error': '이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)'}), 400

        # 파일 크기 확인 (5MB)
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > 5 * 1024 * 1024:
            return jsonify({'success': False, 'error': '파일 크기가 5MB를 초과합니다.'}), 400

        # 기존 명함 이미지 삭제
        old_card = attachment_repo.get_one_by_category(employee_id, category)
        if old_card:
            old_path = old_card.get('file_path') if isinstance(old_card, dict) else old_card.file_path
            if old_path:
                full_path = os.path.join(current_app.root_path, old_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            attachment_repo.delete_by_category(employee_id, category)

        # 파일 저장
        filename = secure_filename(file.filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        unique_filename = f"{employee_id}_{side}_{timestamp}.{ext}"

        upload_folder = get_business_card_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 웹 접근 경로
        web_path = f"/static/uploads/business_cards/{unique_filename}"

        # DB 저장 (딕셔너리 형태로 전달)
        attachment_data = {
            'employeeId': employee_id,
            'fileName': filename,
            'filePath': web_path,
            'fileType': ext,
            'fileSize': file_size,
            'category': category,
            'uploadDate': datetime.now().strftime('%Y-%m-%d')
        }
        created = attachment_repo.create(attachment_data)

        return jsonify({
            'success': True,
            'side': side,
            'file_path': web_path,
            'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
        })

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


@employees_bp.route('/api/employees/<int:employee_id>/business-card/<side>', methods=['DELETE'])
@login_required
def delete_business_card(employee_id, side):
    """명함 이미지 삭제 API"""
    try:
        # 권한 체크: 본인 또는 관리자
        is_admin = session.get('user_role') == 'admin'
        is_self = session.get('employee_id') == employee_id
        if not is_admin and not is_self:
            return jsonify({'success': False, 'error': '권한이 없습니다.'}), 403

        # side 파라미터 검증
        if side not in ['front', 'back']:
            return jsonify({'success': False, 'error': 'side 파라미터는 front 또는 back이어야 합니다.'}), 400

        category = f'business_card_{side}'

        # 기존 명함 이미지 삭제
        old_card = attachment_repo.get_one_by_category(employee_id, category)
        if old_card:
            old_path = old_card.get('file_path') if isinstance(old_card, dict) else old_card.file_path
            if old_path:
                full_path = os.path.join(current_app.root_path, old_path.lstrip('/'))
                if os.path.exists(full_path):
                    os.remove(full_path)
            attachment_repo.delete_by_category(employee_id, category)
            return jsonify({'success': True, 'message': f'명함 {side} 이미지가 삭제되었습니다.'})
        else:
            return jsonify({'success': False, 'error': '삭제할 명함 이미지가 없습니다.'}), 404

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500
