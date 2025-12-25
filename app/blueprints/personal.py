"""
개인 계정 Blueprint

개인 회원가입, 프로필 관리, 개인 대시보드를 처리합니다.
Phase 2: 개인-법인 분리 아키텍처의 일부입니다.
Phase 6: 백엔드 리팩토링 - 프로필 헬퍼 통합
Sprint 1: Repository 계층 적용 - ORM 직접 사용 제거
Phase 8: 상수 모듈 적용
"""
import os
import uuid
from datetime import datetime
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify, current_app
from werkzeug.utils import secure_filename

from app.constants.session_keys import SessionKeys, AccountType
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
    if session.get(SessionKeys.USER_ID):
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
    user_id = session.get(SessionKeys.USER_ID)

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
        'english_name': request.form.get('name_en', '').strip() or None,  # 템플릿은 'name_en' 사용
        'chinese_name': request.form.get('chinese_name', '').strip() or None,
        'resident_number': request.form.get('rrn', '').strip() or None,  # 템플릿은 'rrn' 사용
        'birth_date': request.form.get('birth_date', '').strip() or None,
        'lunar_birth': request.form.get('lunar_birth') == 'true',
        'gender': request.form.get('gender', '').strip() or None,
        'mobile_phone': request.form.get('phone', '').strip() or None,  # 템플릿은 'phone' 사용
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

    if not success:
        flash(f'프로필 수정 중 오류가 발생했습니다: {error_msg}', 'error')
        return redirect(url_for('profile.edit'))

    # ========================================
    # 학력 정보 저장
    # ========================================
    education_school_names = request.form.getlist('education_school_name[]')
    education_degrees = request.form.getlist('education_degree[]')
    education_majors = request.form.getlist('education_major[]')
    education_graduation_years = request.form.getlist('education_graduation_year[]')
    education_gpas = request.form.getlist('education_gpa[]')
    education_graduation_statuses = request.form.getlist('education_graduation_status[]')
    education_notes = request.form.getlist('education_note[]')

    # 기존 학력 삭제 후 새로 저장
    personal_service.delete_all_educations(profile_obj.id)
    for i, school_name in enumerate(education_school_names):
        if school_name.strip():  # 학교명이 있는 경우만 저장
            edu_data = {
                'school_name': school_name.strip(),
                'degree': education_degrees[i] if i < len(education_degrees) else None,
                'major': education_majors[i] if i < len(education_majors) else None,
                'graduation_date': education_graduation_years[i] if i < len(education_graduation_years) else None,
                'gpa': education_gpas[i] if i < len(education_gpas) else None,
                'status': education_graduation_statuses[i] if i < len(education_graduation_statuses) else None,
                'notes': education_notes[i] if i < len(education_notes) else None,
            }
            personal_service.add_education(profile_obj.id, edu_data)

    # ========================================
    # 경력 정보 저장
    # ========================================
    career_company_names = request.form.getlist('career_company_name[]')
    career_departments = request.form.getlist('career_department[]')
    career_positions = request.form.getlist('career_position[]')
    career_job_grades = request.form.getlist('career_job_grade[]')
    career_job_titles = request.form.getlist('career_job_title[]')
    career_job_roles = request.form.getlist('career_job_role[]')
    career_duties = request.form.getlist('career_duties[]')
    career_salary_types = request.form.getlist('career_salary_type[]')
    career_salaries = request.form.getlist('career_salary[]')
    career_monthly_salaries = request.form.getlist('career_monthly_salary[]')
    career_pay_steps = request.form.getlist('career_pay_step[]')
    career_start_dates = request.form.getlist('career_start_date[]')
    career_end_dates = request.form.getlist('career_end_date[]')

    # 기존 경력 삭제 후 새로 저장
    personal_service.delete_all_careers(profile_obj.id)
    for i, company_name in enumerate(career_company_names):
        if company_name.strip():  # 회사명이 있는 경우만 저장
            career_data = {
                'company_name': company_name.strip(),
                'department': career_departments[i] if i < len(career_departments) else None,
                'position': career_positions[i] if i < len(career_positions) else None,
                'job_grade': career_job_grades[i] if i < len(career_job_grades) else None,
                'job_title': career_job_titles[i] if i < len(career_job_titles) else None,
                'job_role': career_job_roles[i] if i < len(career_job_roles) else None,
                'responsibilities': career_duties[i] if i < len(career_duties) else None,
                'salary_type': career_salary_types[i] if i < len(career_salary_types) else None,
                'salary': int(career_salaries[i]) if i < len(career_salaries) and career_salaries[i] else None,
                'monthly_salary': int(career_monthly_salaries[i]) if i < len(career_monthly_salaries) and career_monthly_salaries[i] else None,
                'pay_step': int(career_pay_steps[i]) if i < len(career_pay_steps) and career_pay_steps[i] else None,
                'start_date': career_start_dates[i] if i < len(career_start_dates) else None,
                'end_date': career_end_dates[i] if i < len(career_end_dates) else None,
            }
            personal_service.add_career(profile_obj.id, career_data)

    # ========================================
    # 자격증 정보 저장
    # ========================================
    cert_names = request.form.getlist('certificate_name[]')
    cert_issuers = request.form.getlist('certificate_issuer[]')
    cert_acquisition_dates = request.form.getlist('certificate_acquisition_date[]')
    cert_expiry_dates = request.form.getlist('certificate_expiry_date[]')
    cert_numbers = request.form.getlist('certificate_number[]')
    cert_grades = request.form.getlist('certificate_grade[]')

    # 기존 자격증 삭제 후 새로 저장
    personal_service.delete_all_certificates(profile_obj.id)
    for i, cert_name in enumerate(cert_names):
        if cert_name.strip():  # 자격증명이 있는 경우만 저장
            cert_data = {
                'name': cert_name.strip(),
                'issuing_organization': cert_issuers[i] if i < len(cert_issuers) else None,
                'issue_date': cert_acquisition_dates[i] if i < len(cert_acquisition_dates) else None,
                'expiry_date': cert_expiry_dates[i] if i < len(cert_expiry_dates) else None,
                'certificate_number': cert_numbers[i] if i < len(cert_numbers) else None,
                'grade': cert_grades[i] if i < len(cert_grades) else None,
            }
            personal_service.add_certificate(profile_obj.id, cert_data)

    # ========================================
    # 어학 정보 저장
    # ========================================
    lang_names = request.form.getlist('language_name[]')
    lang_proficiencies = request.form.getlist('language_proficiency[]')
    lang_test_names = request.form.getlist('language_test_name[]')
    lang_scores = request.form.getlist('language_score[]')
    lang_test_dates = request.form.getlist('language_test_date[]')

    # 기존 어학 삭제 후 새로 저장
    personal_service.delete_all_languages(profile_obj.id)
    for i, lang_name in enumerate(lang_names):
        if lang_name.strip():  # 언어명이 있는 경우만 저장
            lang_data = {
                'language': lang_name.strip(),
                'proficiency': lang_proficiencies[i] if i < len(lang_proficiencies) else None,
                'test_name': lang_test_names[i] if i < len(lang_test_names) else None,
                'score': lang_scores[i] if i < len(lang_scores) else None,
                'test_date': lang_test_dates[i] if i < len(lang_test_dates) else None,
            }
            personal_service.add_language(profile_obj.id, lang_data)

    # ========================================
    # 병역 정보 저장
    # ========================================
    military_status = request.form.get('military_status', '').strip()
    if military_status:
        # 복무기간 파싱 (2018.01 ~ 2019.10 형식)
        military_period = request.form.get('military_period', '').strip()
        start_date = None
        end_date = None
        if military_period and '~' in military_period:
            parts = military_period.split('~')
            if len(parts) == 2:
                start_date = parts[0].strip()
                end_date = parts[1].strip()

        military_data = {
            'service_type': military_status,
            'branch': request.form.get('military_branch', '').strip() or None,
            'rank': request.form.get('military_rank', '').strip() or None,
            'start_date': start_date,
            'end_date': end_date,
            'specialty': request.form.get('military_specialty', '').strip() or None,
            'duty': request.form.get('military_duty', '').strip() or None,
            'notes': request.form.get('military_exemption_reason', '').strip() or None,
        }
        personal_service.save_military(profile_obj.id, military_data)

    flash('프로필이 수정되었습니다.', 'success')
    return redirect(url_for('profile.view'))


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
    종료된 계약도 3년 보관 기간 내에는 열람 가능합니다.
    """
    user_id = session.get(SessionKeys.USER_ID)

    # 열람 가능한 모든 계약 조회 (활성 + 종료)
    contracts = personal_service.get_viewable_contracts(user_id, include_terminated=True)

    # 활성/종료 계약 분리 (템플릿에서 그룹화 표시용)
    active_contracts = [c for c in contracts if c.get('is_active')]
    terminated_contracts = [c for c in contracts if not c.get('is_active')]

    return render_template('personal/company_card_list.html',
                           contracts=contracts,
                           active_contracts=active_contracts,
                           terminated_contracts=terminated_contracts)


@personal_bp.route('/company-cards/<int:contract_id>')
@personal_login_required
def company_card_detail(contract_id):
    """특정 회사 인사카드 상세

    개인 계정의 특정 법인 계약에 대한 인사카드 상세 정보를 표시합니다.
    공유 파셜 템플릿을 사용하여 법인 직원 인사카드와 동일한 구조로 표시합니다.
    종료된 계약도 3년 보관 기간 내에는 읽기 전용으로 열람 가능합니다.
    """
    user_id = session.get(SessionKeys.USER_ID)

    # 계약 정보 및 회사 인사카드 데이터 조회
    card_data = personal_service.get_company_card_data(user_id, contract_id)

    if not card_data:
        flash('인사카드 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('personal.company_card_list'))

    # 종료된 계약 여부
    is_terminated = card_data.get('is_terminated', False)

    return render_template('personal/company_card_detail.html',
                           # 기본 정보
                           contract=card_data['contract'],
                           company=card_data['company'],
                           employee=card_data.get('employee'),
                           contract_info=card_data.get('contract_info'),
                           # 급여/복리후생 (현재 미구현)
                           salary=card_data.get('salary'),
                           benefit=card_data.get('benefit'),
                           insurance=card_data.get('insurance'),
                           # 이력 정보 (공유 파셜용 - _history_info.html)
                           education_list=card_data.get('education_list', []),
                           career_list=card_data.get('career_list', []),
                           certificate_list=card_data.get('certificate_list', []),
                           language_list=card_data.get('language_list', []),
                           military=card_data.get('military'),
                           award_list=card_data.get('award_list', []),
                           family_list=card_data.get('family_list', []),
                           # 인사기록 정보 (법인 DB 기반)
                           salary_history_list=card_data.get('salary_history_list', []),
                           salary_payment_list=card_data.get('salary_payment_list', []),
                           promotion_list=card_data.get('promotion_list', []),
                           evaluation_list=card_data.get('evaluation_list', []),
                           training_list=card_data.get('training_list', []),
                           attendance_summary=card_data.get('attendance_summary'),
                           asset_list=card_data.get('asset_list', []),
                           # 첨부파일 (인사카드에서는 조회 전용)
                           attachment_list=[],
                           is_readonly=True,
                           # 종료 상태 정보
                           is_terminated=is_terminated,
                           terminated_at=card_data.get('terminated_at'),
                           termination_reason=card_data.get('termination_reason'),
                           show_termination_notice=is_terminated,
                           # 페이지 모드 및 계정 타입
                           page_mode='hr_card',
                           account_type=AccountType.PERSONAL,
                           is_corporate=False)
