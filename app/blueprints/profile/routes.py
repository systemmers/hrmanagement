"""
Profile Routes - 통합 프로필 라우트

법인 직원, 법인 관리자, 개인 계정의 프로필을 통합 처리하는 라우트
Phase 8: 상수 모듈 적용
Phase 2: Service 계층 표준화
"""
import os
from flask import render_template, g, jsonify, request, flash, redirect, url_for, session, current_app

from app.blueprints.profile import profile_bp
from app.constants.session_keys import SessionKeys, AccountType
from app.blueprints.profile.decorators import (
    unified_profile_required,
    corporate_only,
    corporate_admin_only
)
from app.services.attachment_service import attachment_service
from app.services.corporate_admin_profile_service import corporate_admin_profile_service
from app.services.file_storage_service import file_storage
from app.models.user import User


@profile_bp.route('/')
@unified_profile_required
def view():
    """
    통합 프로필 조회

    법인 직원과 개인 계정 모두 동일한 템플릿 사용
    계정 유형에 따라 표시되는 섹션이 다름
    """
    adapter = g.profile

    # 어댑터의 to_template_context 메서드 사용
    # 기존 파셜과의 호환성을 위해 항상 'employee' 변수 사용
    # (profile/detail.html에서 profile_data = employee if employee is defined else profile 처리)
    context = adapter.to_template_context(variable_name='employee')

    # 추가 컨텍스트 - 가족정보, 수상내역 등 (법인/개인 공통)
    if hasattr(adapter, 'get_family_list'):
        context['family_list'] = adapter.get_family_list()
    if hasattr(adapter, 'get_award_list'):
        context['award_list'] = adapter.get_award_list()
    if hasattr(adapter, 'get_project_participation_list'):
        context['project_participation_list'] = adapter.get_project_participation_list()

    # 추가 컨텍스트 (법인 직원 전용)
    if adapter.is_corporate() and hasattr(adapter, 'get_hr_project_list'):
        context['hr_project_list'] = adapter.get_hr_project_list()

    # 메타 정보
    context['sections'] = adapter.get_available_sections()

    # 페이지 모드: 프로필 (개인정보만 표시)
    context['page_mode'] = 'profile'

    # 첨부파일 목록 조회 (프로필에서는 수정/삭제 가능)
    profile_id = adapter.get_profile_id()
    if profile_id:
        context['attachment_list'] = attachment_service.get_by_employee_id(profile_id)
    else:
        context['attachment_list'] = []
    context['is_readonly'] = False  # 프로필에서는 수정 가능

    return render_template('profile/detail.html', **context)


@profile_bp.route('/edit', methods=['GET', 'POST'])
@unified_profile_required
def edit():
    """
    통합 프로필 수정

    법인 직원과 개인 계정 모두 동일한 템플릿 사용
    계정 유형에 따라 편집 가능한 섹션이 다름
    """
    adapter = g.profile

    if request.method == 'POST':
        # POST 처리는 각 계정 타입별 서비스로 위임
        account_type = adapter.get_account_type()

        if account_type == AccountType.CORPORATE:
            # 법인 직원 수정은 기존 employees 라우트로
            employee_id = adapter.get_profile_id()
            return redirect(url_for('employees.employee_edit', employee_id=employee_id))
        elif account_type == AccountType.PERSONAL:
            # 개인 프로필 수정
            return redirect(url_for('personal.profile_edit'))
        elif account_type == AccountType.CORPORATE_ADMIN:
            # 법인 관리자 프로필 수정
            return redirect(url_for('profile.admin_profile_edit'))

    # GET: 수정 폼 표시
    # 기존 파셜과의 호환성을 위해 항상 'employee' 변수 사용
    context = adapter.to_template_context(variable_name='employee')
    context['sections'] = adapter.get_available_sections()
    context['action'] = 'update'

    # 페이지 모드: 프로필 (개인정보만 표시)
    context['page_mode'] = 'profile'

    # 첨부파일 목록 조회 (프로필 수정에서도 수정/삭제 가능)
    profile_id = adapter.get_profile_id()
    if profile_id:
        context['attachment_list'] = attachment_service.get_by_employee_id(profile_id)
    else:
        context['attachment_list'] = []
    context['is_readonly'] = False  # 프로필에서는 수정 가능

    return render_template('profile/edit.html', **context)


@profile_bp.route('/section/<section_name>')
@unified_profile_required
def get_section(section_name):
    """
    섹션별 데이터 API

    특정 섹션의 데이터를 JSON으로 반환
    사용자가 접근 가능한 섹션만 반환

    Args:
        section_name: 섹션 이름 (basic, organization, etc.)

    Returns:
        JSON: 섹션 데이터 또는 에러 메시지
    """
    adapter = g.profile

    # 접근 권한 확인
    if section_name not in adapter.get_available_sections():
        return jsonify({
            'success': False,
            'error': '접근 권한이 없는 섹션입니다.'
        }), 403

    # 섹션별 데이터 매핑
    section_methods = {
        'basic': adapter.get_basic_info,
        'organization': adapter.get_organization_info,
        'contract': adapter.get_contract_info,
        'salary': adapter.get_salary_info,
        'benefit': adapter.get_benefit_info,
        'insurance': adapter.get_insurance_info,
        'education': adapter.get_education_list,
        'career': adapter.get_career_list,
        'certificate': adapter.get_certificate_list,
        'language': adapter.get_language_list,
        'military': adapter.get_military_info,
    }

    method = section_methods.get(section_name)
    if not method:
        return jsonify({
            'success': False,
            'error': '알 수 없는 섹션입니다.'
        }), 404

    try:
        data = method()
        return jsonify({
            'success': True,
            'data': data
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': f'데이터 조회 중 오류가 발생했습니다: {str(e)}'
        }), 500


@profile_bp.route('/corporate/salary-history')
@corporate_only
def salary_history():
    """급여 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_salary_history_list()
    })


@profile_bp.route('/corporate/promotions')
@corporate_only
def promotions():
    """승진 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_promotion_list()
    })


@profile_bp.route('/corporate/evaluations')
@corporate_only
def evaluations():
    """평가 기록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_evaluation_list()
    })


@profile_bp.route('/corporate/trainings')
@corporate_only
def trainings():
    """교육 이력 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_training_list()
    })


@profile_bp.route('/corporate/attendances')
@corporate_only
def attendances():
    """근태 기록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_attendance_list()
    })


@profile_bp.route('/corporate/assets')
@corporate_only
def assets():
    """비품 목록 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_asset_list()
    })


@profile_bp.route('/corporate/family')
@corporate_only
def family():
    """가족 정보 조회 (법인 전용)"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_family_list()
    })


@profile_bp.route('/hr-projects')
@unified_profile_required
def hr_projects():
    """인사이력 프로젝트 목록 조회 (법인 전용)"""
    adapter = g.profile

    # 법인 직원만 인사이력 프로젝트 정보 있음
    if not g.is_corporate:
        return jsonify({
            'success': True,
            'data': []
        })

    return jsonify({
        'success': True,
        'data': adapter.get_hr_project_list()
    })


@profile_bp.route('/project-participations')
@unified_profile_required
def project_participations():
    """프로젝트 참여이력 목록 조회"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_project_participation_list()
    })


@profile_bp.route('/awards')
@unified_profile_required
def awards():
    """수상 이력 조회"""
    adapter = g.profile

    # 법인 직원만 수상 정보 있음
    if not g.is_corporate:
        return jsonify({
            'success': True,
            'data': []
        })

    return jsonify({
        'success': True,
        'data': adapter.get_award_list()
    })


# ========================================
# 법인 관리자 프로필 라우트
# ========================================

def _handle_admin_photo_upload(profile_id):
    """법인 관리자 프로필 사진 업로드 처리

    Args:
        profile_id: 프로필 ID (파일명 생성용)

    Returns:
        str or None: 저장된 사진 URL 경로 또는 None
    """
    photo_file = request.files.get('photoFile')
    if not photo_file or photo_file.filename == '':
        # 파일이 없으면 기존 photo 값 사용
        return request.form.get('photo', '').strip() or None

    # 이미지 파일 검증
    if not file_storage.allowed_image_file(photo_file.filename):
        flash('허용되지 않은 이미지 형식입니다. (JPG, PNG, GIF, WebP만 가능)', 'error')
        return None

    # 파일 크기 검증 (5MB)
    photo_file.seek(0, 2)
    file_size = photo_file.tell()
    photo_file.seek(0)
    if file_size > 5 * 1024 * 1024:
        flash('파일 크기는 5MB 이하여야 합니다.', 'error')
        return None

    # 업로드 폴더 생성
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'admin_photos')
    os.makedirs(upload_folder, exist_ok=True)

    # 고유 파일명 생성 및 저장
    filename = file_storage.generate_filename(photo_file.filename, 'admin', profile_id)
    file_path = os.path.join(upload_folder, filename)
    photo_file.save(file_path)

    # URL 경로 반환
    return url_for('static', filename=f'uploads/admin_photos/{filename}')


@profile_bp.route('/admin/create', methods=['GET', 'POST'])
def admin_profile_create():
    """법인 관리자 프로필 생성"""
    user_id = session.get(SessionKeys.USER_ID)
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)

    # 인증 및 권한 확인
    if not user_id or account_type != AccountType.CORPORATE:
        flash('접근 권한이 없습니다.', 'warning')
        return redirect(url_for('auth.login'))

    # 이미 프로필이 있는지 확인
    if corporate_admin_profile_service.has_profile(user_id):
        flash('이미 프로필이 존재합니다.', 'info')
        return redirect(url_for('profile.view'))

    # 사용자 정보 조회
    user = User.query.get(user_id)
    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # 사진 업로드 처리 (user_id를 임시 ID로 사용)
        photo_url = _handle_admin_photo_upload(user_id)

        data = {
            'name': request.form.get('name', '').strip(),
            'english_name': request.form.get('english_name', '').strip() or None,
            'position': request.form.get('position', '').strip() or None,
            'department': request.form.get('department', '').strip() or None,
            'mobile_phone': request.form.get('mobile_phone', '').strip() or None,
            'office_phone': request.form.get('office_phone', '').strip() or None,
            'email': request.form.get('email', '').strip() or None,
            'bio': request.form.get('bio', '').strip() or None,
            'photo': photo_url,
        }

        # 필수 필드 검증
        if not data['name']:
            flash('이름은 필수 입력 항목입니다.', 'error')
            return render_template(
                'profile/admin_profile_form.html',
                mode='create',
                user=user,
                form_data=data
            )

        # 프로필 생성
        success, profile, error = corporate_admin_profile_service.create_profile(
            user_id=user_id,
            company_id=user.company_id,
            data=data
        )

        if success:
            flash('프로필이 생성되었습니다.', 'success')
            return redirect(url_for('profile.view'))
        else:
            flash(f'프로필 생성 중 오류가 발생했습니다: {error}', 'error')

    return render_template(
        'profile/admin_profile_form.html',
        mode='create',
        user=user,
        form_data={}
    )


@profile_bp.route('/admin/edit', methods=['GET', 'POST'])
@corporate_admin_only
def admin_profile_edit():
    """법인 관리자 프로필 수정"""
    adapter = g.profile
    admin_profile = g.admin_profile

    if request.method == 'POST':
        # 사진 업로드 처리
        photo_url = _handle_admin_photo_upload(admin_profile.id)

        data = {
            'name': request.form.get('name', '').strip(),
            'english_name': request.form.get('english_name', '').strip() or None,
            'position': request.form.get('position', '').strip() or None,
            'department': request.form.get('department', '').strip() or None,
            'mobile_phone': request.form.get('mobile_phone', '').strip() or None,
            'office_phone': request.form.get('office_phone', '').strip() or None,
            'email': request.form.get('email', '').strip() or None,
            'bio': request.form.get('bio', '').strip() or None,
            'photo': photo_url,
        }

        # 필수 필드 검증
        if not data['name']:
            flash('이름은 필수 입력 항목입니다.', 'error')
            return render_template(
                'profile/admin_profile_form.html',
                mode='edit',
                adapter=adapter,
                form_data=data
            )

        # 프로필 수정
        success, error = corporate_admin_profile_service.update_profile(
            user_id=session.get(SessionKeys.USER_ID),
            data=data
        )

        if success:
            flash('프로필이 수정되었습니다.', 'success')
            return redirect(url_for('profile.view'))
        else:
            flash(f'프로필 수정 중 오류가 발생했습니다: {error}', 'error')

    return render_template(
        'profile/admin_profile_form.html',
        mode='edit',
        adapter=adapter,
        form_data=adapter.get_basic_info()
    )


# ========================================
# 법인 관리자 프로필 API
# ========================================

@profile_bp.route('/api/admin/profile', methods=['GET'])
@corporate_admin_only
def api_admin_profile_get():
    """법인 관리자 프로필 조회 API"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_basic_info()
    })


@profile_bp.route('/api/admin/profile', methods=['PUT'])
@corporate_admin_only
def api_admin_profile_update():
    """법인 관리자 프로필 수정 API"""
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json()

    if not data:
        return jsonify({
            'success': False,
            'error': '요청 데이터가 없습니다.'
        }), 400

    # 필수 필드 검증
    if 'name' in data and not data['name'].strip():
        return jsonify({
            'success': False,
            'error': '이름은 필수 입력 항목입니다.'
        }), 400

    # 프로필 수정
    success, error = corporate_admin_profile_service.update_profile(
        user_id=user_id,
        data=data
    )

    if success:
        # 업데이트된 프로필 반환
        adapter = corporate_admin_profile_service.get_adapter(user_id)
        return jsonify({
            'success': True,
            'data': adapter.get_basic_info() if adapter else None,
            'message': '프로필이 수정되었습니다.'
        })
    else:
        return jsonify({
            'success': False,
            'error': error
        }), 500


@profile_bp.route('/api/admin/company', methods=['GET'])
@corporate_admin_only
def api_admin_company_get():
    """법인 관리자 소속 회사 정보 조회 API"""
    adapter = g.profile

    return jsonify({
        'success': True,
        'data': adapter.get_organization_info()
    })
