"""
직원 관리 Blueprint

직원 CRUD 및 관련 기능을 제공합니다.
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import Blueprint, render_template, request, redirect, url_for, flash, jsonify, current_app

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
@login_required
def employee_list():
    """직원 목록"""
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

    # 다중 필터 적용
    if departments or positions or statuses or sort_column:
        employees = employee_repo.filter_employees(
            departments=departments if departments else None,
            positions=positions if positions else None,
            statuses=statuses if statuses else None,
            sort_by=sort_column,
            sort_order=sort_order
        )
    elif department or position or status:
        employees = employee_repo.filter_employees(
            department=department,
            position=position,
            status=status,
            sort_by=sort_column,
            sort_order=sort_order
        )
    else:
        employees = employee_repo.filter_employees(
            sort_by=sort_column,
            sort_order=sort_order
        )

    # 분류 옵션 전달
    classification_options = classification_repo.get_all()
    return render_template('employee_list.html',
                           employees=employees,
                           classification_options=classification_options)


@employees_bp.route('/employees/<int:employee_id>')
@login_required
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
@manager_or_admin_required
def employee_new():
    """직원 등록 폼"""
    return render_template('employee_form.html', employee=None, action='create')


@employees_bp.route('/employees', methods=['POST'])
@manager_or_admin_required
def employee_create():
    """직원 등록 처리"""
    try:
        employee = extract_employee_from_form(request.form, employee_id=0)

        # 사번 자동 생성 (폼에서 입력하지 않은 경우)
        if not employee.employee_number:
            employee.employee_number = generate_employee_number()

        created_employee = employee_repo.create(employee)
        flash(f'{created_employee.name} 직원이 등록되었습니다. (사번: {created_employee.employee_number})', 'success')
        return redirect(url_for('employees.employee_detail', employee_id=created_employee.id))

    except Exception as e:
        flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
        return redirect(url_for('employees.employee_new'))


@employees_bp.route('/employees/<int:employee_id>/edit', methods=['GET'])
@manager_or_admin_required
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
@manager_or_admin_required
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
@admin_required
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

        # DB 저장
        from ..models import Attachment
        attachment = Attachment(
            employee_id=employee_id,
            file_name=filename,
            file_path=web_path,
            file_type=ext,
            file_size=file_size,
            category=category,
            upload_date=datetime.now().strftime('%Y-%m-%d')
        )
        created = attachment_repo.create(attachment)

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
