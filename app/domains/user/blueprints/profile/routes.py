"""
Profile Routes - 통합 프로필 라우트

법인 직원, 법인 관리자, 개인 계정의 프로필을 통합 처리하는 라우트
Phase 8: 상수 모듈 적용
Phase 2: Service 계층 표준화
Phase 9: DRY 원칙 - photo 업로드 중앙화
Phase 9: 도메인 마이그레이션 - app/domains/user/blueprints/profile/로 이동
"""
from flask import render_template, g, request, flash, redirect, url_for, session

from app.domains.user.blueprints.profile import profile_bp
from app.shared.constants.session_keys import SessionKeys, AccountType
from app.domains.user.blueprints.profile.decorators import (
    unified_profile_required,
    corporate_only,
    corporate_admin_only
)
from app.domains.user.services.user_service import user_service
from app.domains.attachment.services import attachment_service
from app.domains.user.services.corporate_admin_profile_service import corporate_admin_profile_service
from app.domains.employee.services import employee_service
from app.shared.services.file_storage_service import file_storage, CATEGORY_ADMIN_PHOTO
from app.shared.utils.api_helpers import api_success, api_error, api_not_found, api_forbidden, api_server_error


@profile_bp.route('/dashboard')
@unified_profile_required
def dashboard():
    """
    통합 대시보드

    법인 직원과 개인 계정의 대시보드 표시
    개인 계정은 기존 personal.dashboard로 리다이렉트
    법인 직원은 직원용 대시보드 표시
    """
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)

    # 개인 계정: 기존 대시보드로 리다이렉트
    if account_type == AccountType.PERSONAL:
        return redirect(url_for('personal.dashboard'))

    # 법인 관리자: 법인 대시보드로 리다이렉트
    if account_type == AccountType.CORPORATE and session.get('user_role') in ['admin', 'manager']:
        return redirect(url_for('corporate.dashboard'))

    # 법인 직원 대시보드
    employee_id = session.get(SessionKeys.EMPLOYEE_ID)
    if not employee_id:
        flash('직원 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    dashboard_data = employee_service.get_dashboard_data(employee_id)
    if not dashboard_data:
        flash('대시보드 데이터를 불러올 수 없습니다.', 'error')
        return redirect(url_for('profile.view'))

    return render_template(
        'domains/user/dashboard/base_dashboard.html',
        account_type='employee_sub',
        employee=dashboard_data['employee'],
        stats=dashboard_data['stats'],
        work_info=dashboard_data['work_info']
    )


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
    # owner_type: 법인 직원은 'employee', 개인은 'profile'
    profile_id = adapter.get_profile_id()
    account_type = adapter.get_account_type()
    owner_type = 'employee' if account_type == AccountType.CORPORATE else 'profile'

    if profile_id:
        context['attachment_list'] = attachment_service.get_by_owner(owner_type, profile_id)
    else:
        context['attachment_list'] = []
    context['is_readonly'] = False  # 프로필에서는 수정 가능

    return render_template('domains/user/profile/detail.html', **context)


# ========================================
# 레거시 라우트 삭제 (2026-01-16)
# - edit(): 인라인 편집으로 대체
# ========================================


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
        return api_forbidden('접근 권한이 없는 섹션입니다.')

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
        return api_not_found('섹션')

    try:
        data = method()
        return api_success({'data': data})
    except Exception as e:
        return api_server_error(f'데이터 조회 중 오류가 발생했습니다: {str(e)}')


@profile_bp.route('/corporate/salary-history')
@corporate_only
def salary_history():
    """급여 이력 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_salary_history_list()})


@profile_bp.route('/corporate/promotions')
@corporate_only
def promotions():
    """승진 이력 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_promotion_list()})


@profile_bp.route('/corporate/evaluations')
@corporate_only
def evaluations():
    """평가 기록 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_evaluation_list()})


@profile_bp.route('/corporate/trainings')
@corporate_only
def trainings():
    """교육 이력 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_training_list()})


@profile_bp.route('/corporate/attendances')
@corporate_only
def attendances():
    """근태 기록 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_attendance_list()})


@profile_bp.route('/corporate/assets')
@corporate_only
def assets():
    """비품 목록 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_asset_list()})


@profile_bp.route('/corporate/family')
@corporate_only
def family():
    """가족 정보 조회 (법인 전용)"""
    adapter = g.profile

    return api_success({'data': adapter.get_family_list()})


@profile_bp.route('/hr-projects')
@unified_profile_required
def hr_projects():
    """인사이력 프로젝트 목록 조회 (법인 전용)"""
    adapter = g.profile

    # 법인 직원만 인사이력 프로젝트 정보 있음
    if not g.is_corporate:
        return api_success({'data': []})

    return api_success({'data': adapter.get_hr_project_list()})


@profile_bp.route('/project-participations')
@unified_profile_required
def project_participations():
    """프로젝트 참여이력 목록 조회"""
    adapter = g.profile

    return api_success({'data': adapter.get_project_participation_list()})


@profile_bp.route('/awards')
@unified_profile_required
def awards():
    """수상 이력 조회"""
    adapter = g.profile

    # 법인 직원만 수상 정보 있음
    if not g.is_corporate:
        return api_success({'data': []})

    return api_success({'data': adapter.get_award_list()})


# ========================================
# 법인 관리자 프로필 라우트
# ========================================

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
    user = user_service.get_model_by_id(user_id)
    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        # 사진 업로드 처리 (중앙화된 서비스 사용)
        fallback_photo = request.form.get('photo', '').strip() or None
        photo_url, photo_error = file_storage.handle_photo_upload(
            request.files.get('photoFile'),
            user_id,
            CATEGORY_ADMIN_PHOTO,
            fallback_photo
        )
        if photo_error:
            flash(photo_error, 'error')

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
                'domains/user/profile/admin_profile_form.html',
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
        'domains/user/profile/admin_profile_form.html',
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
        # 사진 업로드 처리 (중앙화된 서비스 사용)
        fallback_photo = request.form.get('photo', '').strip() or None
        photo_url, photo_error = file_storage.handle_photo_upload(
            request.files.get('photoFile'),
            admin_profile.id,
            CATEGORY_ADMIN_PHOTO,
            fallback_photo
        )
        if photo_error:
            flash(photo_error, 'error')

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
                'domains/user/profile/admin_profile_form.html',
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
        'domains/user/profile/admin_profile_form.html',
        mode='edit',
        adapter=adapter,
        form_data=adapter.get_basic_info()
    )


# ========================================
# 법인 관리자 프로필 API
# ========================================

@profile_bp.route('/api/admin/profile', methods=['GET', 'PUT', 'PATCH'])
@corporate_admin_only
def api_admin_profile():
    """법인 관리자 프로필 조회/수정 API

    GET: 프로필 조회
    PUT/PATCH: 프로필 수정 (전체/부분 업데이트 모두 지원)
    """
    adapter = g.profile

    # GET: 프로필 조회
    if request.method == 'GET':
        return api_success({'data': adapter.get_basic_info()})

    # PUT/PATCH: 프로필 수정
    user_id = session.get(SessionKeys.USER_ID)
    data = request.get_json()

    if not data:
        return api_error('요청 데이터가 없습니다.')

    # 필수 필드 검증
    if 'name' in data and not data['name'].strip():
        return api_error('이름은 필수 입력 항목입니다.')

    # 프로필 수정
    success, error = corporate_admin_profile_service.update_profile(
        user_id=user_id,
        data=data
    )

    if success:
        # 업데이트된 프로필 반환
        updated_adapter = corporate_admin_profile_service.get_adapter(user_id)
        return api_success({
            'data': updated_adapter.get_basic_info() if updated_adapter else None,
            'message': '프로필이 수정되었습니다.'
        })
    else:
        return api_server_error(error)


@profile_bp.route('/api/admin/company', methods=['GET'])
@corporate_admin_only
def api_admin_company_get():
    """법인 관리자 소속 회사 정보 조회 API"""
    adapter = g.profile

    return api_success({'data': adapter.get_organization_info()})


# ========================================
# 프로필 완성 라우트 (계정 발급 후)
# ========================================

@profile_bp.route('/complete', methods=['GET'])
@unified_profile_required
def complete_profile():
    """프로필 완성 페이지

    계정 발급(create_account_only) 후 pending_info 상태인 직원이
    로그인하면 이 페이지로 리다이렉션되어 정보를 완성합니다.

    인라인 편집 시스템 사용 (2026-01-16)
    레거시 edit.html 삭제 -> detail.html 사용
    """
    adapter = g.profile

    # pending_info 상태가 아니면 일반 프로필 페이지로
    if hasattr(adapter, 'get_status'):
        status = adapter.get_status()
        if status != 'pending_info':
            return redirect(url_for('profile.view'))

    # 기존 어댑터 패턴 활용 (DIP 원칙)
    context = adapter.to_template_context(variable_name='employee')
    context['sections'] = adapter.get_available_sections()

    # 프로필 완성 모드 표시 (인라인 편집 사용)
    context['page_mode'] = 'profile'
    context['is_completion_mode'] = True

    # 안내 메시지 (flash로 전달)
    flash('프로필 정보를 완성해주세요. 각 섹션의 수정 버튼을 클릭하여 정보를 입력할 수 있습니다.', 'info')

    # 첨부파일 목록 조회
    # owner_type: 법인 직원은 'employee', 개인은 'profile'
    profile_id = adapter.get_profile_id()
    account_type = adapter.get_account_type()
    owner_type = 'employee' if account_type == AccountType.CORPORATE else 'profile'

    if profile_id:
        context['attachment_list'] = attachment_service.get_by_owner(owner_type, profile_id)
    else:
        context['attachment_list'] = []
    context['is_readonly'] = False

    return render_template('domains/user/profile/detail.html', **context)
