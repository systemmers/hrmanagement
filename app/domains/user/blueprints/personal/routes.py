"""
Personal Account Routes (Personal Blueprint)

SRP principle applied:
- Route definitions only
- Data extraction delegated to form_extractors.py
- Relation data updates delegated to relation_updaters.py

Phase 1 Migration: domains/user/blueprints/personal/routes.py
Phase 1.3: attachment_service 통합 - 프로필 사진 Attachment 레코드 생성
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
from app.domains.user.services.personal_service import personal_service
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
    """Get personal profile photo folder (legacy - for backward compatibility)"""
    folder = os.path.join(current_app.static_folder, 'uploads', 'personal_photos')
    os.makedirs(folder, exist_ok=True)
    return folder


def save_personal_photo(file, user_id):
    """Save personal profile photo using FileStorageService

    Phase 1.3: FileStorageService 활성화
    - 구조화된 경로 사용: personal/{user_id}/attachments/profile_photo/
    """
    from app.shared.services.file_storage_service import file_storage

    try:
        # FileStorageService를 사용하여 구조화된 경로에 저장
        _, web_path, _ = file_storage.save_personal_file(
            file, user_id, 'attachments/profile_photo'
        )
        return web_path
    except Exception as e:
        current_app.logger.error(f'프로필 사진 저장 실패: {e}')
        # Fallback: 레거시 방식 사용
        from app.shared.utils.file_helpers import get_file_extension
        ext = get_file_extension(file.filename)
        unique_filename = f"personal_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"
        folder = get_personal_photo_folder()
        file_path = os.path.join(folder, unique_filename)
        file.save(file_path)
        return f"/static/uploads/personal_photos/{unique_filename}"


def handle_photo_upload(request_files, user_id, profile_id, existing_photo_path):
    """Handle photo upload (SRP: photo upload logic separated)

    Phase 1.3: attachment_service 통합 - profile.photo + Attachment 이중 저장
    - profile.photo 필드 업데이트 (하위 호환성)
    - Attachment 레코드 생성 (SSOT 첨부파일 시스템)

    Args:
        request_files: request.files object
        user_id: User ID
        profile_id: Profile ID (for attachment owner)
        existing_photo_path: Existing photo path

    Returns:
        tuple: (photo_path, error_message)
    """
    from app.domains.attachment.services import attachment_service
    from app.domains.attachment.constants import AttachmentCategory, OwnerType
    from app.shared.utils.file_helpers import get_file_extension

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

    # 1. 파일 저장 (기존 방식 - profile.photo 호환성 유지)
    photo_path = save_personal_photo(photo_file, user_id)

    # 2. 기존 프로필 사진 Attachment 삭제 (있는 경우)
    if profile_id:
        attachment_service.delete_by_owner_and_category(
            OwnerType.PROFILE,
            profile_id,
            AttachmentCategory.PROFILE_PHOTO,
            commit=False
        )

    # 3. 새 Attachment 레코드 생성
    if profile_id:
        ext = get_file_extension(photo_file.filename)
        attachment_service.create({
            'owner_type': OwnerType.PROFILE,
            'owner_id': profile_id,
            'file_name': photo_file.filename,
            'file_path': photo_path,
            'file_type': ext,
            'file_size': file_size,
            'category': AttachmentCategory.PROFILE_PHOTO,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
        }, commit=False)

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
                return render_template('domains/user/personal/register.html',
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
                return render_template('domains/user/personal/register.html',
                                       username=username,
                                       email=email,
                                       name=name,
                                       mobile_phone=mobile_phone)

        return render_template('domains/user/personal/register.html')

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
            return redirect(url_for('profile.view'))

        return render_template('domains/user/dashboard/base_dashboard.html',
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
        """Profile edit - 레거시 라우트

        인라인 편집으로 대체됨 (2026-01-16)
        하위 호환성을 위해 profile.view로 리다이렉트
        """
        # GET/POST 모두 프로필 페이지로 리다이렉트 (인라인 편집 사용)
        return redirect(url_for('profile.view'), code=301)

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

        return render_template('domains/user/personal/company_card_list.html',
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

        return render_template('domains/user/personal/company_card_detail.html',
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
