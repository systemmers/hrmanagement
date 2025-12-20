"""
직원 데이터 변경 라우트

직원 생성, 수정, 삭제 처리를 담당합니다.
21번/22번 원칙: 직원 등록 시 계정 동시 생성 지원
Phase 8: 상수 모듈 적용
"""
import os
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, session

from ...constants.session_keys import SessionKeys, UserRole
from ...utils.employee_number import generate_employee_number
from ...utils.decorators import login_required, admin_required, manager_or_admin_required
from ...utils.tenant import get_current_organization_id
from ...services.employee_service import employee_service
from ...services import employee_account_service
from .helpers import (
    verify_employee_access, extract_employee_from_form, extract_basic_fields_from_form,
    update_family_data, update_education_data, update_career_data,
    update_certificate_data, update_language_data, update_military_data,
    update_hr_project_data, update_project_participation_data, update_award_data,
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
        """직원 등록 처리 (멀티테넌시 적용)

        21번/22번 원칙: 계정 생성 토글에 따라 직원+계정 동시 생성
        """
        try:
            # 계정 생성 여부 확인
            create_account = request.form.get('create_account') == 'true'
            org_id = get_current_organization_id()
            company_id = session.get(SessionKeys.COMPANY_ID)
            admin_user_id = session.get(SessionKeys.USER_ID)

            if create_account and company_id:
                # === 계정과 함께 직원 생성 (21번/22번 원칙) ===
                employee_data = _extract_employee_data_for_service(request.form, org_id)
                account_data = _extract_account_data(request.form)

                success, result, error = employee_account_service.create_employee_with_account(
                    employee_data=employee_data,
                    account_data=account_data,
                    company_id=company_id,
                    admin_user_id=admin_user_id
                )

                if not success:
                    flash(f'직원 등록 실패: {error}', 'error')
                    return redirect(url_for('employees.employee_new'))

                employee_id = result['employee_id']

                # 프로필 사진/명함 처리
                _handle_profile_photo_upload(employee_id)
                _handle_business_card_upload(employee_id)

                flash(f'직원 및 계정이 등록되었습니다. {result["message"]}', 'success')
                return redirect(url_for('employees.employee_edit', employee_id=employee_id))

            else:
                # === 기존 로직: 직원만 생성 (계정 없이) ===
                employee = extract_employee_from_form(request.form, employee_id=0)

                # 사번 자동 생성
                if not employee.employee_number:
                    employee.employee_number = generate_employee_number()

                # organization_id 자동 설정
                if org_id and not employee.organization_id:
                    employee.organization_id = org_id

                # Employee 객체를 Dict로 변환하여 service에 전달
                employee_data = employee.to_dict() if hasattr(employee, 'to_dict') else vars(employee)
                created_employee = employee_service.create_employee_direct(employee_data)
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
        user_role = session.get(SessionKeys.USER_ROLE)

        # Employee role은 본인 정보만 수정 가능
        if user_role == UserRole.EMPLOYEE:
            my_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        # 관리자/매니저는 자사 소속 직원만 수정 가능
        if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            employee = extract_employee_from_form(request.form, employee_id=employee_id)
            updated_employee = employee_service.update_employee_direct(employee_id, employee)
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
        user_role = session.get(SessionKeys.USER_ROLE)

        if user_role == UserRole.EMPLOYEE:
            my_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            basic_fields = extract_basic_fields_from_form(request.form)
            updated_employee = employee_service.update_employee_partial(employee_id, basic_fields)
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
        user_role = session.get(SessionKeys.USER_ROLE)

        if user_role == UserRole.EMPLOYEE:
            my_employee_id = session.get(SessionKeys.EMPLOYEE_ID)
            if my_employee_id != employee_id:
                flash('본인 정보만 수정할 수 있습니다.', 'warning')
                return redirect(url_for('employees.employee_edit', employee_id=my_employee_id))

        if user_role in [UserRole.ADMIN, UserRole.MANAGER]:
            if not verify_employee_access(employee_id):
                flash('접근 권한이 없습니다.', 'error')
                return redirect(url_for('main.index'))

        try:
            update_education_data(employee_id, request.form)
            update_career_data(employee_id, request.form)
            update_certificate_data(employee_id, request.form)
            update_language_data(employee_id, request.form)
            update_military_data(employee_id, request.form)
            update_hr_project_data(employee_id, request.form)
            update_project_participation_data(employee_id, request.form)
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
            employee = employee_service.get_employee_by_id(employee_id)
            if employee:
                if employee_service.delete_employee_direct(employee_id):
                    employee_name = employee.get('name') if isinstance(employee, dict) else employee.name
                    flash(f'{employee_name} 직원이 삭제되었습니다.', 'success')
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
    employee_service.create_attachment(attachment_data)
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
        employee_service.create_attachment(attachment_data)
        uploaded = True

    return uploaded


def _extract_employee_data_for_service(form, org_id):
    """폼 데이터에서 직원 정보 추출 (서비스용 Dict)

    Args:
        form: request.form
        org_id: 조직 ID

    Returns:
        직원 정보 Dict
    """
    employee_number = form.get('employee_number')
    if not employee_number:
        employee_number = generate_employee_number()

    return {
        'name': form.get('name', ''),
        'photo': form.get('photo') or '/static/images/face/face_01_m.png',
        'department': form.get('department', ''),
        'position': form.get('position', ''),
        'status': form.get('status', 'active'),
        'hire_date': form.get('hire_date', ''),
        'phone': form.get('phone', ''),
        'email': form.get('email', ''),
        'organization_id': int(form.get('organization_id')) if form.get('organization_id') else org_id,
        'employee_number': employee_number,
        'team': form.get('team') or None,
        # 직급 체계 (Career 모델과 일관성)
        'job_grade': form.get('job_grade') or None,
        'job_title': form.get('job_title') or None,
        'job_role': form.get('job_role') or None,
        'work_location': form.get('work_location') or None,
        'internal_phone': form.get('internal_phone') or None,
        'company_email': form.get('company_email') or None,
        'english_name': form.get('name_en') or form.get('english_name') or None,
        'birth_date': form.get('birth_date') or None,
        'gender': form.get('gender') or None,
        'address': form.get('address') or None,
        'detailed_address': form.get('detailed_address') or None,
        'postal_code': form.get('postal_code') or None,
        'resident_number': form.get('rrn') or form.get('resident_number') or None,
        'mobile_phone': form.get('mobile_phone') or None,
        'home_phone': form.get('home_phone') or None,
        'nationality': form.get('nationality') or None,
        'blood_type': form.get('blood_type') or None,
        'religion': form.get('religion') or None,
        'hobby': form.get('hobby') or None,
        'specialty': form.get('specialty') or None,
    }


def _extract_account_data(form):
    """폼 데이터에서 계정 정보 추출

    Args:
        form: request.form

    Returns:
        계정 정보 Dict
    """
    return {
        'username': form.get('account_username', ''),
        'email': form.get('account_email', ''),
        'password': form.get('account_password', ''),
        'role': form.get('account_role', 'employee'),
    }
