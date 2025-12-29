"""
직원 데이터 변경 라우트

직원 생성, 수정, 삭제 처리를 담당합니다.
21번/22번 원칙: 직원 등록 시 계정 동시 생성 지원
Phase 8: 상수 모듈 적용
Phase 9: DRY 원칙 - file_storage 서비스 활용
Phase 24: 레이어 분리 - Service 경유
"""
from datetime import datetime
from flask import Blueprint, request, redirect, url_for, flash, session, render_template

from ...constants.session_keys import SessionKeys, UserRole, AccountType
from ...utils.employee_number import generate_employee_number
from ...utils.decorators import login_required, admin_required, manager_or_admin_required
from ...utils.tenant import get_current_organization_id
from ...utils.object_helpers import safe_get
from ...services.employee_service import employee_service
from ...services import employee_account_service
from ...services.file_storage_service import file_storage, CATEGORY_PROFILE_PHOTO
from ...services.user_employee_link_service import user_employee_link_service
from .helpers import (
    verify_employee_access, extract_employee_from_form, extract_basic_fields_from_form,
    update_family_data, update_education_data, update_career_data,
    update_certificate_data, update_language_data, update_military_data,
    update_hr_project_data, update_project_participation_data, update_award_data,
    get_business_card_folder, generate_unique_filename
)
from ...services.organization_service import organization_service


# ========================================
# 개인정보 보호 상수 및 헬퍼
# ========================================

# 개인 계정에서만 수정 가능한 필드 목록 (법인에서 수정 불가)
PERSONAL_PROTECTED_FIELDS = [
    'name', 'english_name', 'name_en', 'birth_date', 'gender',
    'nationality', 'resident_number', 'rrn', 'mobile_phone', 'home_phone',
    'address', 'detailed_address', 'postal_code',
    'blood_type', 'religion', 'hobby', 'specialty',
    'marital_status', 'emergency_contact_name', 'emergency_contact_phone',
    'emergency_contact_relation',
]

# 계약 후 수정 불가 필드 목록 (승인된 개인계약 존재 시 수정 불가)
# 주의: status 필드는 관리자가 변경 가능해야 하므로 제외
CONTRACT_PROTECTED_FIELDS = [
    # 소속정보
    'organization_id', 'department', 'team', 'position', 'job_grade',
    'job_title', 'job_role', 'work_location', 'internal_phone', 'company_email',
    # 계약정보 (status 제외)
    'hire_date', 'employment_type', 'contract_period', 'probation_end',
    # 급여정보
    'base_salary', 'position_allowance', 'meal_allowance', 'transport_allowance',
    'bonus_rate', 'pay_type', 'bank_name', 'account_number',
    'annual_salary', 'hourly_wage', 'overtime_hours', 'overtime_allowance',
    'night_hours', 'night_allowance', 'holiday_days', 'holiday_allowance',
    # 4대보험
    'national_pension_number', 'national_pension_date',
    'health_insurance_number', 'health_insurance_date',
    'employment_insurance_number', 'employment_insurance_date',
    'industrial_insurance_number', 'industrial_insurance_date',
    'pension_exempt', 'health_exempt', 'employment_exempt',
]


def _has_person_contract(employee_id: int, company_id: int) -> bool:
    """직원이 개인 계정과 연동된 계약이 있는지 확인

    Args:
        employee_id: 직원 ID
        company_id: 회사 ID

    Returns:
        개인 계약 존재 여부
    """
    if not employee_id or not company_id:
        return False

    return user_employee_link_service.has_approved_personal_contract(
        employee_id, company_id
    )


def _filter_personal_fields(form_data: dict, employee_id: int) -> dict:
    """법인 계정에서 개인 정보 필드 필터링 (보안 강화)

    개인 계약이 있는 직원의 경우, 법인 계정에서 개인 정보 필드를 수정하지 못하도록 필터링

    Args:
        form_data: 폼에서 추출한 데이터
        employee_id: 직원 ID

    Returns:
        필터링된 데이터
    """
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)
    company_id = session.get(SessionKeys.COMPANY_ID)

    # 법인 계정이 아니면 필터링 불필요
    if account_type != AccountType.CORPORATE:
        return form_data

    # 개인 계약 존재 여부 확인
    if not _has_person_contract(employee_id, company_id):
        return form_data

    # 개인 정보 필드 제거
    filtered_data = form_data.copy()
    for field in PERSONAL_PROTECTED_FIELDS:
        filtered_data.pop(field, None)

    return filtered_data


def _filter_contract_fields(form_data: dict, employee_id: int) -> dict:
    """계약 후 보호 필드 필터링 (승인된 개인계약 없으면 수정 가능)

    승인된 개인계약이 있는 직원의 경우, 계약 관련 필드를 수정하지 못하도록 필터링
    조건 통일: 템플릿의 has_person_contract와 동일한 조건 사용

    Args:
        form_data: 폼에서 추출한 데이터
        employee_id: 직원 ID

    Returns:
        필터링된 데이터
    """
    if not employee_id:
        return form_data

    company_id = session.get(SessionKeys.COMPANY_ID)

    # 승인된 개인계약 존재 여부 확인 (템플릿과 동일한 조건)
    if not _has_person_contract(employee_id, company_id):
        return form_data  # 계약 없으면 수정 가능

    # 승인된 개인계약이 있으면 계약 관련 필드 제거
    filtered_data = form_data.copy()
    for field in CONTRACT_PROTECTED_FIELDS:
        filtered_data.pop(field, None)

    return filtered_data


def register_mutation_routes(bp: Blueprint):
    """데이터 변경 라우트를 Blueprint에 등록"""

    # ========================================
    # 직원 생성
    # ========================================

    @bp.route('/employees', methods=['POST'])
    @manager_or_admin_required
    def employee_create():
        """직원 등록 처리 (멀티테넌시 적용)

        21번/22번 원칙: 직원 등록 시 계정 필수 생성
        """
        try:
            org_id = get_current_organization_id()
            company_id = session.get(SessionKeys.COMPANY_ID)
            admin_user_id = session.get(SessionKeys.USER_ID)

            # 회사 정보 필수 확인
            if not company_id:
                flash('회사 정보가 없습니다.', 'error')
                return redirect(url_for('employees.employee_new'))

            # === 계정과 함께 직원 생성 (계정 생성 필수) ===
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

        except Exception as e:
            flash(f'직원 등록 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_new'))

    # ========================================
    # 계정 발급 (Account Provisioning)
    # ========================================

    @bp.route('/employees/provision', methods=['GET', 'POST'])
    @manager_or_admin_required
    def employee_account_provision():
        """계정 발급: 계정만 발급, 직원이 로그인 후 정보 입력

        기존 create_account_only() 서비스 메서드 활용
        Employee(status='pending_info') + User(account_type='employee_sub') 생성
        """
        company_id = session.get(SessionKeys.COMPANY_ID)
        admin_user_id = session.get(SessionKeys.USER_ID)

        if request.method == 'GET':
            # 조직 목록 조회 (선택 옵션용)
            org_id = get_current_organization_id()
            organizations = []
            if org_id:
                organizations = organization_service.get_flat_list(root_organization_id=org_id)

            return render_template(
                'employees/account_provision.html',
                organizations=organizations
            )

        # POST: 계정 발급 처리
        try:
            account_data = {
                'username': request.form.get('username', '').strip(),
                'email': request.form.get('email', '').strip(),
                'password': request.form.get('password', '').strip() or None,
                'role': request.form.get('role', 'employee')
            }

            minimal_employee_data = {
                'name': request.form.get('name', '').strip()
            }

            # 선택적 조직 ID
            org_id = request.form.get('organization_id')
            if org_id:
                minimal_employee_data['organization_id'] = int(org_id)

            success, result, error = employee_account_service.create_account_only(
                account_data=account_data,
                minimal_employee_data=minimal_employee_data,
                company_id=company_id,
                admin_user_id=admin_user_id
            )

            if success:
                flash_msg = f'계정이 발급되었습니다. (사용자명: {result["username"]})'
                if result.get('status') == EmployeeStatus.PENDING_INFO:
                    flash_msg += ' 직원이 로그인하여 정보를 입력해야 합니다.'
                flash(flash_msg, 'success')
                return redirect(url_for('employees.employee_list'))
            else:
                flash(f'계정 발급 실패: {error}', 'error')
                return redirect(url_for('employees.employee_account_provision'))

        except Exception as e:
            flash(f'계정 발급 중 오류가 발생했습니다: {str(e)}', 'error')
            return redirect(url_for('employees.employee_account_provision'))

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
            # Employee 객체를 Dict로 변환하여 전달 (BaseRepository.update는 Dict 기대)
            employee_data = employee.to_dict() if hasattr(employee, 'to_dict') else vars(employee)

            # 개인 계약 연동 직원의 개인 정보 필드 필터링 (보안 강화)
            employee_data = _filter_personal_fields(employee_data, employee_id)

            # 계약 후 보호 필드 필터링 (계약 확정 시 수정 불가)
            employee_data = _filter_contract_fields(employee_data, employee_id)

            updated_employee = employee_service.update_employee_direct(employee_id, employee_data)
            if updated_employee:
                # update_employee_direct는 Dict 반환
                employee_name = safe_get(updated_employee, 'name', '')
                flash(f'{employee_name} 직원 정보가 수정되었습니다.', 'success')
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
            # 기존 직원 정보 조회 (상태 확인용)
            existing_employee = employee_service.get_employee_by_id(employee_id)
            original_status = existing_employee.get('status') if existing_employee else None

            basic_fields = extract_basic_fields_from_form(request.form)

            # 개인 계약 연동 직원의 개인 정보 필드 필터링 (보안 강화)
            basic_fields = _filter_personal_fields(basic_fields, employee_id)

            # 계약 후 보호 필드 필터링 (계약 확정 시 수정 불가)
            basic_fields = _filter_contract_fields(basic_fields, employee_id)

            updated_employee = employee_service.update_employee_partial(employee_id, basic_fields)

            # 개인 계약 연동 직원의 가족 정보 수정 차단 (법인에서는 동기화만 가능)
            company_id = session.get(SessionKeys.COMPANY_ID)
            account_type = session.get(SessionKeys.ACCOUNT_TYPE)
            if not (account_type == AccountType.CORPORATE and _has_person_contract(employee_id, company_id)):
                update_family_data(employee_id, request.form)

            if updated_employee:
                # employee_sub 계정이 프로필 완성한 경우 상태 전환
                account_type = session.get(SessionKeys.ACCOUNT_TYPE)
                if account_type == AccountType.EMPLOYEE_SUB and original_status == EmployeeStatus.PENDING_INFO:
                    # pending_info → pending_contract 상태 전환
                    employee_service.update_employee_partial(employee_id, {'status': 'pending_contract'})
                    flash('프로필이 완성되었습니다. 계약 요청을 기다리고 있습니다.', 'success')
                    return redirect(url_for('mypage.company_info'))

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
            # 개인 계약 연동 직원의 이력정보 수정 차단 (법인에서는 동기화만 가능)
            company_id = session.get(SessionKeys.COMPANY_ID)
            account_type = session.get(SessionKeys.ACCOUNT_TYPE)
            if account_type == AccountType.CORPORATE and _has_person_contract(employee_id, company_id):
                flash('개인 계정 연동 직원의 이력 정보는 동기화를 통해서만 업데이트됩니다.', 'warning')
                return redirect(url_for('employees.employee_detail', employee_id=employee_id))

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
                    employee_name = safe_get(employee, 'name')
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
    """프로필 사진 업로드 처리 (DRY: file_storage 서비스 활용)"""
    if 'photoFile' not in request.files:
        return False

    file = request.files['photoFile']

    # 파일 검증 (중앙화된 서비스 사용)
    is_valid, error_msg = file_storage.validate_file(file, is_image=True)
    if not is_valid:
        return False

    # 파일 저장 (중앙화된 서비스 사용)
    file_size = file_storage.get_file_size(file)
    web_path, error = file_storage.handle_photo_upload(
        file,
        employee_id,
        CATEGORY_PROFILE_PHOTO
    )

    if error or not web_path:
        return False

    # DB 저장 (첨부파일 기록)
    ext = file_storage.get_file_extension(file.filename)
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
    """명함 파일 업로드 처리 (앞면/뒷면) - DRY: file_storage 서비스 활용"""
    uploaded = False

    for side in ['Front', 'Back']:
        file_key = f'businessCard{side}File'
        if file_key not in request.files:
            continue

        file = request.files[file_key]

        # 파일 검증 (중앙화된 서비스 사용)
        is_valid, error_msg = file_storage.validate_file(file, is_image=True)
        if not is_valid:
            continue

        # 파일 저장 (business_card 카테고리)
        category = f'business_card_{side.lower()}'
        file_size = file_storage.get_file_size(file)
        web_path, error = file_storage.handle_photo_upload(
            file,
            employee_id,
            category
        )

        if error or not web_path:
            continue

        # DB 저장 (첨부파일 기록)
        ext = file_storage.get_file_extension(file.filename)
        attachment_data = {
            'employeeId': employee_id,
            'fileName': file.filename,
            'filePath': web_path,
            'fileType': ext,
            'fileSize': file_size,
            'category': category,
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
        'status': form.get('status', EmployeeStatus.ACTIVE),
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
