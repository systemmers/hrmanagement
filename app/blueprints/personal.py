"""
개인 계정 Blueprint

개인 회원가입, 프로필 관리, 개인 대시보드를 처리합니다.
Phase 2: 개인-법인 분리 아키텍처의 일부입니다.
Phase 6: 백엔드 리팩토링 - 프로필 헬퍼 통합
Sprint 1: Repository 계층 적용 - ORM 직접 사용 제거
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename

from app.services.personal_service import personal_service

# 사진 업로드 설정
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


def allowed_image_file(filename):
    """이미지 파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def get_personal_photo_folder():
    """개인 프로필 사진 저장 폴더 반환"""
    folder = os.path.join(current_app.static_folder, 'uploads', 'personal_photos')
    os.makedirs(folder, exist_ok=True)
    return folder


def save_personal_photo(file, user_id):
    """개인 프로필 사진 저장"""
    ext = file.filename.rsplit('.', 1)[1].lower()
    unique_filename = f"personal_{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}_{uuid.uuid4().hex[:8]}.{ext}"

    folder = get_personal_photo_folder()
    file_path = os.path.join(folder, unique_filename)
    file.save(file_path)

    return f"/static/uploads/personal_photos/{unique_filename}"
from app.utils.decorators import personal_login_required
from app.utils.personal_helpers import get_current_profile, profile_required_no_inject

personal_bp = Blueprint('personal', __name__, url_prefix='/personal')


@personal_bp.route('/register', methods=['GET', 'POST'])
def register():
    """개인 회원가입"""
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 계정 정보
        username = request.form.get('username', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        password_confirm = request.form.get('password_confirm', '')

        # 프로필 정보
        name = request.form.get('name', '').strip()
        mobile_phone = request.form.get('mobile_phone', '').strip()

        # 유효성 검사
        errors = personal_service.validate_registration(
            username, email, password, password_confirm, name
        )

        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('personal/register.html',
                                   username=username,
                                   email=email,
                                   name=name,
                                   mobile_phone=mobile_phone)

        # 회원가입 처리
        success, user, error_msg = personal_service.register(
            username=username,
            email=email,
            password=password,
            name=name,
            mobile_phone=mobile_phone
        )

        if success:
            flash('회원가입이 완료되었습니다. 로그인해주세요.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash(f'회원가입 중 오류가 발생했습니다: {error_msg}', 'error')
            return render_template('personal/register.html',
                                   username=username,
                                   email=email,
                                   name=name,
                                   mobile_phone=mobile_phone)

    return render_template('personal/register.html')


@personal_bp.route('/dashboard')
@personal_login_required
def dashboard():
    """개인 대시보드"""
    user_id = session.get('user_id')
    data = personal_service.get_dashboard_data(user_id)

    if not data:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if not data['profile']:
        flash('프로필을 먼저 작성해주세요.', 'info')
        return redirect(url_for('personal.profile_edit'))

    return render_template('dashboard/base_dashboard.html',
                           account_type='personal',
                           user=data['user'],
                           profile=data['profile'],
                           stats=data['stats'])


@personal_bp.route('/profile')
@personal_login_required
def profile():
    """프로필 조회 - 통합 프로필로 리다이렉트"""
    # 통합 프로필 시스템으로 리다이렉트 (301 영구 이동)
    return redirect(url_for('profile.view'), code=301)


@personal_bp.route('/profile/edit', methods=['GET', 'POST'])
@personal_login_required
def profile_edit():
    """
    프로필 수정
    - GET: 통합 프로필 수정 페이지로 리다이렉트
    - POST: 폼 데이터 저장 처리 (통합 템플릿에서 이 엔드포인트로 POST)
    """
    user_id = session.get('user_id')

    # GET 요청: 통합 프로필 수정 페이지로 리다이렉트
    if request.method == 'GET':
        return redirect(url_for('profile.edit'), code=301)

    # POST 요청: 폼 데이터 저장 처리
    user, profile_obj = personal_service.get_user_with_profile(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 프로필이 없으면 생성
    if not profile_obj:
        profile_obj = personal_service.ensure_profile_exists(user_id, user.username)

    # 사진 업로드 처리
    photo_path = profile_obj.photo  # 기존 사진 경로 유지
    if 'photoFile' in request.files:
        photo_file = request.files['photoFile']
        if photo_file and photo_file.filename:
            if allowed_image_file(photo_file.filename):
                # 파일 크기 검사
                photo_file.seek(0, os.SEEK_END)
                file_size = photo_file.tell()
                photo_file.seek(0)

                if file_size <= MAX_IMAGE_SIZE:
                    photo_path = save_personal_photo(photo_file, user_id)
                else:
                    flash('사진 파일 크기는 5MB 이하여야 합니다.', 'warning')
            else:
                flash('이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)', 'warning')

    # 폼 데이터 수집 - 법인과 동일한 필드 구조
    data = {
        'name': request.form.get('name', profile_obj.name).strip(),
        'english_name': request.form.get('english_name', '').strip() or None,
        'chinese_name': request.form.get('chinese_name', '').strip() or None,
        'resident_number': request.form.get('resident_number', '').strip() or None,
        'birth_date': request.form.get('birth_date', '').strip() or None,
        'lunar_birth': request.form.get('lunar_birth') == 'true',
        'gender': request.form.get('gender', '').strip() or None,
        'mobile_phone': request.form.get('mobile_phone', '').strip() or None,
        'home_phone': request.form.get('home_phone', '').strip() or None,
        'email': request.form.get('email', '').strip() or None,
        'postal_code': request.form.get('postal_code', '').strip() or None,
        'address': request.form.get('address', '').strip() or None,
        'detailed_address': request.form.get('detailed_address', '').strip() or None,
        'nationality': request.form.get('nationality', '').strip() or None,
        'blood_type': request.form.get('blood_type', '').strip() or None,
        'religion': request.form.get('religion', '').strip() or None,
        'hobby': request.form.get('hobby', '').strip() or None,
        'specialty': request.form.get('specialty', '').strip() or None,
        'is_public': request.form.get('is_public') == 'true',
        'photo': photo_path,
    }

    success, error_msg = personal_service.update_profile(user_id, data)

    if success:
        flash('프로필이 수정되었습니다.', 'success')
        return redirect(url_for('profile.view'))
    else:
        flash(f'수정 중 오류가 발생했습니다: {error_msg}', 'error')
        return redirect(url_for('profile.edit'))


# ============================================================
# 학력 관리 API
# ============================================================

@personal_bp.route('/education', methods=['GET'])
@personal_login_required
@profile_required_no_inject
def education_list():
    """학력 목록 조회"""
    profile = get_current_profile()
    educations = personal_service.get_educations(profile.id)
    return jsonify({'educations': educations})


@personal_bp.route('/education', methods=['POST'])
@personal_login_required
@profile_required_no_inject
def education_add():
    """학력 추가"""
    profile = get_current_profile()
    data = request.get_json()
    education = personal_service.add_education(profile.id, data)
    return jsonify({'success': True, 'education': education})


@personal_bp.route('/education/<int:education_id>', methods=['DELETE'])
@personal_login_required
@profile_required_no_inject
def education_delete(education_id):
    """학력 삭제"""
    profile = get_current_profile()
    success = personal_service.delete_education(education_id, profile.id)

    if not success:
        return jsonify({'error': '학력 정보를 찾을 수 없습니다.'}), 404

    return jsonify({'success': True})


# ============================================================
# 경력 관리 API
# ============================================================

@personal_bp.route('/career', methods=['GET'])
@personal_login_required
@profile_required_no_inject
def career_list():
    """경력 목록 조회"""
    profile = get_current_profile()
    careers = personal_service.get_careers(profile.id)
    return jsonify({'careers': careers})


@personal_bp.route('/career', methods=['POST'])
@personal_login_required
@profile_required_no_inject
def career_add():
    """경력 추가"""
    profile = get_current_profile()
    data = request.get_json()
    career = personal_service.add_career(profile.id, data)
    return jsonify({'success': True, 'career': career})


@personal_bp.route('/career/<int:career_id>', methods=['DELETE'])
@personal_login_required
@profile_required_no_inject
def career_delete(career_id):
    """경력 삭제"""
    profile = get_current_profile()
    success = personal_service.delete_career(career_id, profile.id)

    if not success:
        return jsonify({'error': '경력 정보를 찾을 수 없습니다.'}), 404

    return jsonify({'success': True})


# ============================================================
# 자격증 관리 API
# ============================================================

@personal_bp.route('/certificate', methods=['GET'])
@personal_login_required
@profile_required_no_inject
def certificate_list():
    """자격증 목록 조회"""
    profile = get_current_profile()
    certificates = personal_service.get_certificates(profile.id)
    return jsonify({'certificates': certificates})


@personal_bp.route('/certificate', methods=['POST'])
@personal_login_required
@profile_required_no_inject
def certificate_add():
    """자격증 추가"""
    profile = get_current_profile()
    data = request.get_json()
    certificate = personal_service.add_certificate(profile.id, data)
    return jsonify({'success': True, 'certificate': certificate})


@personal_bp.route('/certificate/<int:certificate_id>', methods=['DELETE'])
@personal_login_required
@profile_required_no_inject
def certificate_delete(certificate_id):
    """자격증 삭제"""
    profile = get_current_profile()
    success = personal_service.delete_certificate(certificate_id, profile.id)

    if not success:
        return jsonify({'error': '자격증 정보를 찾을 수 없습니다.'}), 404

    return jsonify({'success': True})


# ============================================================
# 어학 관리 API
# ============================================================

@personal_bp.route('/language', methods=['GET'])
@personal_login_required
@profile_required_no_inject
def language_list():
    """어학 목록 조회"""
    profile = get_current_profile()
    languages = personal_service.get_languages(profile.id)
    return jsonify({'languages': languages})


@personal_bp.route('/language', methods=['POST'])
@personal_login_required
@profile_required_no_inject
def language_add():
    """어학 추가"""
    profile = get_current_profile()
    data = request.get_json()
    language = personal_service.add_language(profile.id, data)
    return jsonify({'success': True, 'language': language})


@personal_bp.route('/language/<int:language_id>', methods=['DELETE'])
@personal_login_required
@profile_required_no_inject
def language_delete(language_id):
    """어학 삭제"""
    profile = get_current_profile()
    success = personal_service.delete_language(language_id, profile.id)

    if not success:
        return jsonify({'error': '어학 정보를 찾을 수 없습니다.'}), 404

    return jsonify({'success': True})


# ============================================================
# 병역 관리 API
# ============================================================

@personal_bp.route('/military', methods=['GET'])
@personal_login_required
@profile_required_no_inject
def military_get():
    """병역 정보 조회"""
    profile = get_current_profile()
    military = personal_service.get_military(profile.id)
    return jsonify({'military': military})


@personal_bp.route('/military', methods=['POST'])
@personal_login_required
@profile_required_no_inject
def military_save():
    """병역 정보 저장/수정"""
    profile = get_current_profile()
    data = request.get_json()
    military = personal_service.save_military(profile.id, data)
    return jsonify({'success': True, 'military': military})


# ============================================================
# 회사 인사카드 (Phase 2: 개인 계정용)
# ============================================================

@personal_bp.route('/company-cards')
@personal_login_required
def company_card_list():
    """계약된 회사 인사카드 목록

    개인 계정이 계약한 법인들의 인사카드 목록을 표시합니다.
    """
    user_id = session.get('user_id')

    # 승인된 계약 목록 조회
    contracts = personal_service.get_approved_contracts(user_id)

    return render_template('personal/company_card_list.html',
                           contracts=contracts)


@personal_bp.route('/company-cards/<int:contract_id>')
@personal_login_required
def company_card_detail(contract_id):
    """특정 회사 인사카드 상세

    개인 계정의 특정 법인 계약에 대한 인사카드 상세 정보를 표시합니다.
    """
    user_id = session.get('user_id')

    # 계약 정보 및 회사 인사카드 데이터 조회
    card_data = personal_service.get_company_card_data(user_id, contract_id)

    if not card_data:
        flash('인사카드 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('personal.company_card_list'))

    return render_template('personal/company_card_detail.html',
                           contract=card_data['contract'],
                           company=card_data['company'],
                           employee=card_data.get('employee'),
                           salary=card_data.get('salary'),
                           benefit=card_data.get('benefit'),
                           insurance=card_data.get('insurance'),
                           contract_info=card_data.get('contract_info'),
                           page_mode='hr_card')
