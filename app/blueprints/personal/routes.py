"""
개인 계정 라우트 (Personal Blueprint)

SRP 원칙 적용:
- 라우트 정의만 담당
- 데이터 추출은 form_extractors.py로 위임
- 관계형 데이터 업데이트는 relation_updaters.py로 위임
"""
import os
import uuid
from datetime import datetime
from flask import (
    render_template, request, redirect, url_for, flash,
    session, jsonify, current_app
)
from werkzeug.utils import secure_filename

from ...constants.session_keys import SessionKeys, AccountType
from ...database import db
from ...services.personal_service import personal_service
from ...utils.decorators import personal_login_required
from ...utils.personal_helpers import get_current_profile, profile_required_no_inject

from .form_extractors import extract_profile_data
from .relation_updaters import update_profile_relations


# ========================================
# 사진 업로드 헬퍼 함수
# ========================================

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


def handle_photo_upload(request_files, user_id, existing_photo_path):
    """사진 업로드 처리 (SRP: 사진 업로드 로직 분리)

    Args:
        request_files: request.files 객체
        user_id: 사용자 ID
        existing_photo_path: 기존 사진 경로

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

    # 파일 크기 검사
    photo_file.seek(0, os.SEEK_END)
    file_size = photo_file.tell()
    photo_file.seek(0)

    if file_size > MAX_IMAGE_SIZE:
        return photo_path, '사진 파일 크기는 5MB 이하여야 합니다.'

    photo_path = save_personal_photo(photo_file, user_id)
    return photo_path, None


# ========================================
# 라우트 등록 함수
# ========================================

def register_routes(bp):
    """Blueprint에 라우트 등록 (SRP 적용)"""

    # ========================================
    # 회원가입 / 대시보드
    # ========================================

    @bp.route('/register', methods=['GET', 'POST'])
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

    # ========================================
    # 프로필 조회 / 수정
    # ========================================

    @bp.route('/profile')
    @personal_login_required
    def profile():
        """프로필 조회 - 통합 프로필로 리다이렉트"""
        return redirect(url_for('profile.view'), code=301)

    @bp.route('/profile/edit', methods=['GET', 'POST'])
    @personal_login_required
    def profile_edit():
        """프로필 수정

        GET: 통합 프로필 수정 페이지로 리다이렉트
        POST: 폼 데이터 저장 처리 (form_extractors + relation_updaters 활용)
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

        # 사진 업로드 처리 (헬퍼 함수 사용)
        photo_path, photo_error = handle_photo_upload(
            request.files, user_id, profile_obj.photo
        )
        if photo_error:
            flash(photo_error, 'warning')

        # ========================================
        # 기본 프로필 데이터 저장 (form_extractors 활용)
        # ========================================
        profile_data = extract_profile_data(request.form, profile_obj)
        profile_data['photo'] = photo_path  # 사진 경로 추가

        result = personal_service.update_profile(user_id, profile_data)

        if not result:
            flash(f'프로필 수정 중 오류가 발생했습니다: {result.message}', 'error')
            return redirect(url_for('profile.edit'))

        # ========================================
        # 관계형 데이터 일괄 저장 (relation_updaters 활용)
        # 트랜잭션 안전성: 단일 트랜잭션으로 처리
        # ========================================
        try:
            update_profile_relations(profile_obj.id, request.form)
        except Exception as e:
            current_app.logger.error(f"관계형 데이터 저장 실패: {str(e)}")
            flash('일부 이력 정보 저장에 실패했습니다.', 'warning')

        flash('프로필이 수정되었습니다.', 'success')
        return redirect(url_for('profile.view'))

    # ========================================
    # 학력 관리 API
    # ========================================

    @bp.route('/education', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def education_list():
        """학력 목록 조회"""
        profile = get_current_profile()
        educations = personal_service.get_educations(profile.id)
        return jsonify({'educations': educations})

    @bp.route('/education', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def education_add():
        """학력 추가"""
        profile = get_current_profile()
        data = request.get_json()
        education = personal_service.add_education(profile.id, data)
        return jsonify({'success': True, 'education': education})

    @bp.route('/education/<int:education_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def education_delete(education_id):
        """학력 삭제"""
        profile = get_current_profile()
        success = personal_service.delete_education(education_id, profile.id)

        if not success:
            return jsonify({'error': '학력 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # 경력 관리 API
    # ========================================

    @bp.route('/career', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def career_list():
        """경력 목록 조회"""
        profile = get_current_profile()
        careers = personal_service.get_careers(profile.id)
        return jsonify({'careers': careers})

    @bp.route('/career', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def career_add():
        """경력 추가"""
        profile = get_current_profile()
        data = request.get_json()
        career = personal_service.add_career(profile.id, data)
        return jsonify({'success': True, 'career': career})

    @bp.route('/career/<int:career_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def career_delete(career_id):
        """경력 삭제"""
        profile = get_current_profile()
        success = personal_service.delete_career(career_id, profile.id)

        if not success:
            return jsonify({'error': '경력 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # 자격증 관리 API
    # ========================================

    @bp.route('/certificate', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_list():
        """자격증 목록 조회"""
        profile = get_current_profile()
        certificates = personal_service.get_certificates(profile.id)
        return jsonify({'certificates': certificates})

    @bp.route('/certificate', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_add():
        """자격증 추가"""
        profile = get_current_profile()
        data = request.get_json()
        certificate = personal_service.add_certificate(profile.id, data)
        return jsonify({'success': True, 'certificate': certificate})

    @bp.route('/certificate/<int:certificate_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def certificate_delete(certificate_id):
        """자격증 삭제"""
        profile = get_current_profile()
        success = personal_service.delete_certificate(certificate_id, profile.id)

        if not success:
            return jsonify({'error': '자격증 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # 어학 관리 API
    # ========================================

    @bp.route('/language', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def language_list():
        """어학 목록 조회"""
        profile = get_current_profile()
        languages = personal_service.get_languages(profile.id)
        return jsonify({'languages': languages})

    @bp.route('/language', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def language_add():
        """어학 추가"""
        profile = get_current_profile()
        data = request.get_json()
        language = personal_service.add_language(profile.id, data)
        return jsonify({'success': True, 'language': language})

    @bp.route('/language/<int:language_id>', methods=['DELETE'])
    @personal_login_required
    @profile_required_no_inject
    def language_delete(language_id):
        """어학 삭제"""
        profile = get_current_profile()
        success = personal_service.delete_language(language_id, profile.id)

        if not success:
            return jsonify({'error': '어학 정보를 찾을 수 없습니다.'}), 404

        return jsonify({'success': True})

    # ========================================
    # 병역 관리 API
    # ========================================

    @bp.route('/military', methods=['GET'])
    @personal_login_required
    @profile_required_no_inject
    def military_get():
        """병역 정보 조회"""
        profile = get_current_profile()
        military = personal_service.get_military(profile.id)
        return jsonify({'military': military})

    @bp.route('/military', methods=['POST'])
    @personal_login_required
    @profile_required_no_inject
    def military_save():
        """병역 정보 저장/수정"""
        profile = get_current_profile()
        data = request.get_json()
        military = personal_service.save_military(profile.id, data)
        return jsonify({'success': True, 'military': military})

    # ========================================
    # 회사 인사카드 (Phase 2: 개인 계정용)
    # ========================================

    @bp.route('/company-cards')
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

    @bp.route('/company-cards/<int:contract_id>')
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
