"""
Personal Account Routes (Personal Blueprint)

SRP principle applied:
- Route definitions only
- Data extraction delegated to form_extractors.py
- Relation data updates delegated to relation_updaters.py

Phase 1 Migration: domains/user/blueprints/personal/routes.py
"""
import os
import uuid
from datetime import datetime
from flask import (
    render_template, request, redirect, url_for, flash,
    session, jsonify, current_app
)
from werkzeug.utils import secure_filename

from app.shared.constants.session_keys import SessionKeys, AccountType
from app.database import db
from app.services.personal_service import personal_service
from app.shared.utils.decorators import personal_login_required
from app.shared.utils.personal_helpers import get_current_profile, profile_required_no_inject

from .form_extractors import extract_profile_data
from .relation_updaters import update_profile_relations


# ========================================
# Photo upload helper functions
# ========================================

ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_image_file(filename):
    """Check image file extension"""
    from app.shared.utils.file_helpers import is_allowed_extension
    return is_allowed_extension(filename, ALLOWED_IMAGE_EXTENSIONS)


def get_personal_photo_folder():
    """Get personal profile photo folder"""
    folder = os.path.join(current_app.static_folder, 'uploads', 'personal_photos')
    os.makedirs(folder, exist_ok=True)
    return folder


def save_personal_photo(file, user_id):
    """Save personal profile photo"""
    from app.shared.utils.file_helpers import get_file_extension
    ext = get_file_extension(file.filename)
    unique_filename = f"personal_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    folder = get_personal_photo_folder()
    file_path = os.path.join(folder, unique_filename)
    file.save(file_path)

    return f"/static/uploads/personal_photos/{unique_filename}"


def handle_photo_upload(request_files, user_id, existing_photo_path):
    """Handle photo upload (SRP: photo upload logic separated)

    Args:
        request_files: request.files object
        user_id: User ID
        existing_photo_path: Existing photo path

    Returns:
        tuple: (photo_path, error_message)
    """
    photo_path = existing_photo_path

    if 'photoFile' not in request_files:
        return photo_path, None

    photo_file = request_files['photoFile']
    if not photo_file or not photo_file.filename:
        return photo_path, None

    if not allowed_image_file(photo_file.filename):
        return photo_path, '이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)'

    # File size check
    photo_file.seek(0, os.SEEK_END)
    file_size = photo_file.tell()
    photo_file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return photo_path, '사진 파일 크기는 5MB 이하여야 합니다.'

    photo_path = save_personal_photo(photo_file, user_id)
    return photo_path, None


# ========================================
# Route registration function
# ========================================

def register_routes(bp):
    """Register routes to Blueprint (SRP applied)"""

    # ========================================
    # Registration / Dashboard
    # ========================================

    @bp.route('/register', methods=['GET', 'POST'])
    def register():
        """Personal registration"""
        if session.get(SessionKeys.USER_ID):
            return redirect(url_for('main.index'))

        if request.method == 'POST':
            # Account info
            username = request.form.get('username', '').strip()
            email = request.form.get('email', '').strip()
            password = request.form.get('password', '')
            password_confirm = request.form.get('password_confirm', '')

            # Profile info
            name = request.form.get('name', '').strip()
            mobile_phone = request.form.get('mobile_phone', '').strip()

            # Validation (including phone duplicate/format check)
            errors = personal_service.validate_registration(
                username, email, password, password_confirm, name, mobile_phone
            )

            if errors:
                for error in errors:
                    flash(error, 'error')
                return render_template('personal/register.html',
                                       username=username,
                                       email=email,
                                       name=name,
                                       mobile_phone=mobile_phone)

            # Process registration
            result = personal_service.register(
                username=username,
                email=email,
                password=password,
                name=name,
                mobile_phone=mobile_phone
            )

            if result:
                flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
                return redirect(url_for('auth.login'))
            else:
                flash(f'회원가입 중 오류가 발생했습니다: {result.message}', 'error')
                return render_template('personal/register.html',
                                       username=username,
                                       email=email,
                                       name=name,
                                       mobile_phone=mobile_phone)

        return render_template('personal/register.html')

    @bp.route('/dashboard')
    @personal_login_required
    def dashboard():
        """Personal dashboard"""
        user_id = session.get(SessionKeys.USER_ID)
        data = personal_service.get_dashboard_data(user_id)

        if not data:
            flash('사용자 정보를 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        if not data['profile']:
            flash('프로필을 먼저 작성해주세요.', 'info')
            return redirect(url_for('personal.profile_edit'))

        return render_template('dashboard/base_dashboard.html',
                               account_type=AccountType.PERSONAL,
                               user=data['user'],
                               profile=data['profile'],
                               stats=data['stats'])

    # ========================================
    # Profile view / edit
    # ========================================

    @bp.route('/profile')
    @personal_login_required
    def profile():
        """Profile view - redirect to unified profile"""
        return redirect(url_for('profile.view'), code=301)

    @bp.route('/profile/edit', methods=['GET', 'POST'])
    @personal_login_required
    def profile_edit():
        """Profile edit

        GET: Redirect to unified profile edit page
        POST: Save form data (using form_extractors + relation_updaters)
        """
        user_id = session.get(SessionKeys.USER_ID)

        # GET request: Redirect to unified profile edit page
        if request.method == 'GET':
            return redirect(url_for('profile.edit'), code=301)

        # POST request: Save form data
        user, profile_obj = personal_service.get_user_with_profile(user_id)

        if not user:
            flash('사용자 정보를 찾을 수 없습니다.', 'error')
            return redirect(url_for('main.index'))

        # Create profile if not exists
        if not profile_obj:
            profile_obj = personal_service.ensure_profile_exists(user_id, user.username)

        # Handle photo upload (using helper)
        photo_path, photo_error = handle_photo_upload(
            request.files, user_id, profile_obj.photo
        )
        if photo_error:
            flash(photo_error, 'warning')

        # ========================================
        # Save basic profile data (using form_extractors)
        # ========================================
        profile_data = extract_profile_data(request.form, profile_obj)
        profile_data['photo'] = photo_path

        result = personal_service.update_profile(user_id, profile_data)

        if not result:
            flash(f'프로필 수정 중 오류가 발생했습니다: {result.message}', 'error')
            return redirect(url_for('profile.edit'))

        # ========================================
        # Batch save relation data (using relation_updaters)
        # Transaction safety: processed in single transaction
        # ========================================
        try:
            update_profile_relations(profile_obj.id, request.form)
        except Exception as e:
            current_app.logger.error(f"관계형 데이터 저장 실패: {str(e)}")
            flash('일부 이력 정보 저장에 실패했습니다.', 'warning')

        flash('프로필이 수정되었습니다.', 'success')
        return redirect(url_for('profile.view'))

    # ========================================
    # Education API
    # ========================================

    @bp.route('/education', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def education_list():
        """Get education list"""
        profile = get_current_profile()
        educations = personal_service.get_educations(profile.id)
        return jsonify({'educations': educations})

    @bp.route('/education', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def education_add():
        """Add education"""
        profile = get_current_profile()
        data = request.get_json()
        education = personal_service.add_education(profile.id, data)
        return jsonify({'success': True, 'education': education})

    @bp.route('/education/<int:education_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def education_delete(education_id):
        """Delete education"""
        profile = get_current_profile()
        success = personal_service.delete_education(education_id, profile.id)

        if not success:
            return jsonify({'error': '학력 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # Career API
    # ========================================

    @bp.route('/career', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def career_list():
        """Get career list"""
        profile = get_current_profile()
        careers = personal_service.get_careers(profile.id)
        return jsonify({'careers': careers})

    @bp.route('/career', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def career_add():
        """Add career"""
        profile = get_current_profile()
        data = request.get_json()
        career = personal_service.add_career(profile.id, data)
        return jsonify({'success': True, 'career': career})

    @bp.route('/career/<int:career_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def career_delete(career_id):
        """Delete career"""
        profile = get_current_profile()
        success = personal_service.delete_career(career_id, profile.id)

        if not success:
            return jsonify({'error': '경력 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # Certificate API
    # ========================================

    @bp.route('/certificate', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_list():
        """Get certificate list"""
        profile = get_current_profile()
        certificates = personal_service.get_certificates(profile.id)
        return jsonify({'certificates': certificates})

    @bp.route('/certificate', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_add():
        """Add certificate"""
        profile = get_current_profile()
        data = request.get_json()
        certificate = personal_service.add_certificate(profile.id, data)
        return jsonify({'success': True, 'certificate': certificate})

    @bp.route('/certificate/<int:certificate_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_delete(certificate_id):
        """Delete certificate"""
        profile = get_current_profile()
        success = personal_service.delete_certificate(certificate_id, profile.id)

        if not success:
            return jsonify({'error': '자격증 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # Language API
    # ========================================

    @bp.route('/language', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def language_list():
        """Get language list"""
        profile = get_current_profile()
        languages = personal_service.get_languages(profile.id)
        return jsonify({'languages': languages})

    @bp.route('/language', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def language_add():
        """Add language"""
        profile = get_current_profile()
        data = request.get_json()
        language = personal_service.add_language(profile.id, data)
        return jsonify({'success': True, 'language': language})

    @bp.route('/language/<int:language_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def language_delete(language_id):
        """Delete language"""
        profile = get_current_profile()
        success = personal_service.delete_language(language_id, profile.id)

        if not success:
            return jsonify({'error': '어학 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # Military API
    # ========================================

    @bp.route('/military', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def military_get():
        """Get military info"""
        profile = get_current_profile()
        military = personal_service.get_military(profile.id)
        return jsonify({'military': military})

    @bp.route('/military', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def military_save():
        """Save/update military info"""
        profile = get_current_profile()
        data = request.get_json()
        military = personal_service.save_military(profile.id, data)
        return jsonify({'success': True, 'military': military})

    # ========================================
    # Company HR Card (Phase 2: for personal accounts)
    # ========================================

    @bp.route('/company-cards')
    @personal_login_required
    def company_card_list():
        """Contracted company HR card list

        Displays HR card list of companies contracted with personal account.
        Terminated contracts are viewable within 3-year retention period.
        """
        user_id = session.get(SessionKeys.USER_ID)

        # Get all viewable contracts (active + terminated)
        contracts = personal_service.get_viewable_contracts(user_id, include_terminated=True)

        # Separate active/terminated contracts (for template grouping)
        active_contracts = [c for c in contracts if c.get('is_active')]
        terminated_contracts = [c for c in contracts if not c.get('is_active')]

        return render_template('personal/company_card_list.html',
                               contracts=contracts,
                               active_contracts=active_contracts,
                               terminated_contracts=terminated_contracts)

    @bp.route('/company-cards/<int:contract_id>')
    @personal_login_required
    def company_card_detail(contract_id):
        """Specific company HR card detail

        Displays detailed HR card info for a specific company contract.
        Uses shared partial templates for consistent structure with corporate employee HR cards.
        Terminated contracts are viewable (read-only) within 3-year retention period.
        """
        user_id = session.get(SessionKeys.USER_ID)

        # Get contract info and company HR card data
        card_data = personal_service.get_company_card_data(user_id, contract_id)

        if not card_data:
            flash('인사카드 정보를 찾을 수 없습니다.', 'error')
            return redirect(url_for('personal.company_card_list'))

        # Terminated contract status
        is_terminated = card_data.get('is_terminated', False)

        return render_template('personal/company_card_detail.html',
                               # Basic info
                               contract=card_data['contract'],
                               company=card_data['company'],
                               employee=card_data.get('employee'),
                               contract_info=card_data.get('contract_info'),
                               # Salary/benefits (currently not implemented)
                               salary=card_data.get('salary'),
                               benefit=card_data.get('benefit'),
                               insurance=card_data.get('insurance'),
                               # History info (for shared partial - _history_info.html)
                               education_list=card_data.get('education_list', []),
                               career_list=card_data.get('career_list', []),
                               certificate_list=card_data.get('certificate_list', []),
                               language_list=card_data.get('language_list', []),
                               military=card_data.get('military'),
                               award_list=card_data.get('award_list', []),
                               family_list=card_data.get('family_list', []),
                               # HR record info (based on corporate DB)
                               salary_history_list=card_data.get('salary_history_list', []),
                               salary_payment_list=card_data.get('salary_payment_list', []),
                               promotion_list=card_data.get('promotion_list', []),
                               evaluation_list=card_data.get('evaluation_list', []),
                               training_list=card_data.get('training_list', []),
                               attendance_summary=card_data.get('attendance_summary'),
                               asset_list=card_data.get('asset_list', []),
                               # Attachments (view only in HR card)
                               attachment_list=[],
                               is_readonly=True,
                               # Terminated status info
                               is_terminated=is_terminated,
                               terminated_at=card_data.get('terminated_at'),
                               termination_reason=card_data.get('termination_reason'),
                               show_termination_notice=is_terminated,
                               # Page mode and account type
                               page_mode='hr_card',
                               account_type=AccountType.PERSONAL,
                               is_corporate=False)
