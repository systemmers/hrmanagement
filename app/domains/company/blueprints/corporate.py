"""
법인 계정 Blueprint

법인 회원가입, 법인 정보 관리, 법인 대시보드를 처리합니다.
Phase 1: Company 모델 구현의 일부입니다.
Phase 6: 백엔드 리팩토링 - register() 헬퍼 분할
Phase 8: 상수 모듈 적용
Phase 24: 트랜잭션 SSOT 적용 + CompanyService 경유 레이어 분리, 데이터 변환 로직 Service 이동
Phase 2 Migration: 도메인으로 이동
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.shared.constants.session_keys import SessionKeys, AccountType
from app.shared.utils.api_helpers import api_success, api_error, api_forbidden, api_not_found
from app.domains.user.models import User
from app.shared.utils.decorators import corporate_login_required, corporate_admin_required
from app.shared.utils.corporate_helpers import (
    extract_registration_data,
    validate_registration,
    create_company_entities
)
from app.domains.company.services.company_service import company_service
from app.domains.user.services.user_service import user_service

corporate_bp = Blueprint('corporate', __name__, url_prefix='/corporate')


@corporate_bp.route('/register', methods=['GET', 'POST'])
def register():
    """법인 회원가입"""
    if session.get(SessionKeys.USER_ID):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 데이터 추출
        data = extract_registration_data(request.form)

        # 유효성 검증
        errors = validate_registration(data)
        if errors:
            for error in errors:
                flash(error, 'error')
            return render_template('domains/company/register.html', **data.to_template_context())

        # 엔티티 생성
        error_msg = create_company_entities(data)
        if error_msg:
            flash(error_msg, 'error')
            return render_template('domains/company/register.html', **data.to_template_context())

        flash('법인 회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('domains/company/register.html')


@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    """법인 대시보드"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_service.get_with_stats(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    return render_template('dashboard/base_dashboard.html',
                           account_type=AccountType.CORPORATE,
                           company=company)


@corporate_bp.route('/settings', methods=['GET', 'POST'])
@corporate_admin_required
def settings():
    """법인 정보 설정"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_service.get_by_id(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        result = company_service.update_company_info(company_id, request.form)
        if result:
            flash('법인 정보가 수정되었습니다.', 'success')
            return redirect(url_for('corporate.settings'))
        else:
            flash(f'수정 중 오류가 발생했습니다: {result.message}', 'error')

    return render_template('domains/company/settings.html', company=company)


@corporate_bp.route('/users')
@corporate_admin_required
def users():
    """법인 계정관리 (employee_sub만 표시, 페이지네이션 지원)

    21번 원칙: 법인 계정(employee_sub)만 표시
    personal 계정은 외부 사용자이므로 제외

    BUG-1 수정: 계약 상태 표시 추가
    - N+1 방지: 벌크 조회 사용

    Phase 28: 페이지네이션 + ROW_NUMBER() 적용
    - company_sequence: 법인 내 가입 순서 표시
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_service.get_by_id(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 페이지네이션 파라미터
    page = request.args.get('page', 1, type=int)
    per_page = request.args.get('per_page', 20, type=int)

    # 법인 계정 목록 조회 (페이지네이션 + 법인 내 시퀀스)
    users, pagination = user_service.get_by_company_and_account_type_paginated(
        company_id=company_id,
        account_type=User.ACCOUNT_EMPLOYEE_SUB,
        page=page,
        per_page=per_page
    )

    # Phase 24: 데이터 변환 로직을 Service 레이어로 이동
    # 계약 상태 및 직원 이름 추가를 Service에서 처리
    users = user_service.get_users_with_contract_and_employee_details(users, company_id)

    return render_template(
        'domains/company/users.html',
        company=company,
        users=users,
        pagination=pagination
    )


@corporate_bp.route('/users/add', methods=['GET', 'POST'])
@corporate_admin_required
def add_user():
    """법인 하위 사용자 추가 (deprecated)

    계정 발급 기능으로 통합됨. 하위 호환성을 위해 리다이렉트 처리.
    """
    flash('계정 발급 기능이 "직원관리 > 계정 발급"으로 통합되었습니다.', 'info')
    return redirect(url_for('employees.employee_account_provision'))


# API 엔드포인트

@corporate_bp.route('/api/check-business-number')
def check_business_number():
    """사업자등록번호 중복 확인 API"""
    business_number = request.args.get('business_number', '')
    if not business_number:
        return api_error('사업자등록번호를 입력해주세요.')

    exists = company_service.exists_by_business_number(business_number)
    return api_success({'exists': exists, 'available': not exists})


@corporate_bp.route('/api/company/<int:company_id>')
@corporate_login_required
def get_company(company_id):
    """법인 정보 조회 API"""
    # 자신의 법인 정보만 조회 가능
    if session.get(SessionKeys.COMPANY_ID) != company_id:
        return api_forbidden('접근 권한이 없습니다.')

    company = company_service.get_with_stats(company_id)
    if not company:
        return api_not_found('법인 정보')

    return api_success(company)
