"""
직원 데이터 변경 라우트

직원 생성, 수정, 삭제 처리를 담당합니다.
"""
import os
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, session

from ...utils.employee_number import generate_employee_number
from ...utils.decorators import login_required, admin_required, manager_or_admin_required
from ...utils.tenant import get_current_organization_id
from ...extensions import employee_repo, attachment_repo
from .helpers import (
    verify_employee_access, extract_employee_from_form, extract_basic_fields_from_form,
    update_family_data, update_education_data, update_career_data,
    update_certificate_data, update_language_data, update_military_data,
    update_project_data, update_award_data,
    allowed_image_file, get_file_extension, get_profile_photo_folder, get_business_card_folder,
    generate_unique_filename, MAX_IMAGE_SIZE
)


def register_mutation_routes(bp: Blueprint):
    """데이터 변경 라우트를 Blueprint에 등록"""

    # ========================================
    # 직원 생성
    # ========================================

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
            employee_id = created_employee['id']

            # 프로필 사진 파일 처리
            photo_uploaded = _handle_profile_photo_upload(employee_id)

            # 명함 파일 처리 (앞면/뒷면)
            business_card_uploaded = _handle_business_card_upload(employee_id)

            if photo_uploaded or business_card_uploaded:
                flash(f'{created_employee["name"]} 직원이 등록되었습니다.', 'success')
            else:
                flash(f'{created_employee["name"]} 직원이 등록되었습니다. 사진과 명함을 추가해주세요.', 'success')
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))

        except Exception as e:
            flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_new'))

    # ========================================
    # 직원 수정
    # ========================================

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

    @bp.route('/employees/<int:employee_id>/update/basic', methods=['POST'])
    @login_required
    def employee_update_basic(employee_id):
        """기본정보 전용 수정 처리"""
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


# ========================================
# 파일 업로드 헬퍼 함수
# ========================================

def _handle_profile_photo_upload(employee_id):
    """프로필 사진 업로드 처리"""
    if 'photoFile' not in request.files:
        return False

    file = request.files['photoFile']
    if not file or not file.filename or not allowed_image_file(file.filename):
        return False

    # 파일 크기 확인
    file.seek(0, os.SEEK_END)
    file_size = file.tell()
    file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return False

    # 파일 저장
    ext = get_file_extension(file.filename)
    unique_filename = generate_unique_filename(employee_id, file.filename, 'profile')
    upload_folder = get_profile_photo_folder()
    file_path = os.path.join(upload_folder, unique_filename)
    file.save(file_path)

    # 웹 접근 경로
    web_path = f"/static/uploads/profile_photos/{unique_filename}"

    # DB 저장
    attachment_data = {
        'employeeId': employee_id,
        'fileName': file.filename,
        'filePath': web_path,
        'fileType': ext,
        'fileSize': file_size,
        'category': 'profile_photo',
        'uploadDate': datetime.now().strftime('%Y-%m-%d')
    }
    attachment_repo.create(attachment_data)
    return True


def _handle_business_card_upload(employee_id):
    """명함 파일 업로드 처리 (앞면/뒷면)"""
    uploaded = False

    for side in ['Front', 'Back']:
        file_key = f'businessCard{side}File'
        if file_key not in request.files:
            continue

        file = request.files[file_key]
        if not file or not file.filename or not allowed_image_file(file.filename):
            continue

        # 파일 크기 확인
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_IMAGE_SIZE:
            continue

        # 파일 저장
        ext = get_file_extension(file.filename)
        unique_filename = generate_unique_filename(employee_id, file.filename, f'business_card_{side.lower()}')
        upload_folder = get_business_card_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 웹 접근 경로
        web_path = f"/static/uploads/business_cards/{unique_filename}"

        # DB 저장
        attachment_data = {
            'employeeId': employee_id,
            'fileName': file.filename,
            'filePath': web_path,
            'fileType': ext,
            'fileSize': file_size,
            'category': f'business_card_{side.lower()}',
            'uploadDate': datetime.now().strftime('%Y-%m-%d')
        }
        attachment_repo.create(attachment_data)
        uploaded = True

    return uploaded
