"""
법인 계정 Blueprint

법인 회원가입, 법인 정보 관리, 법인 대시보드를 처리합니다.
Phase 1: Company 모델 구현의 일부입니다.
Phase 6: 백엔드 리팩토링 - register() 헬퍼 분할
Phase 8: 상수 모듈 적용
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session, jsonify

from app.constants.session_keys import SessionKeys, AccountType
from app.database import db
from app.models.company import Company
from app.models.user import User
from app.models.corporate_admin_profile import CorporateAdminProfile
from app.repositories.company_repository import company_repository
from app.extensions import user_repo
from app.utils.decorators import corporate_login_required, corporate_admin_required
from app.utils.corporate_helpers import (
    extract_registration_data,
    validate_registration,
    create_company_entities
)

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
            return render_template('corporate/register.html', **data.to_template_context())

        # 엔티티 생성
        error_msg = create_company_entities(data)
        if error_msg:
            flash(error_msg, 'error')
            return render_template('corporate/register.html', **data.to_template_context())

        flash('법인 회원가입이 완료되었습니다. 로그인해주세요.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('corporate/register.html')


@corporate_bp.route('/dashboard')
@corporate_login_required
def dashboard():
    """법인 대시보드"""
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_repository.get_with_stats(company_id)
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

    company = company_repository.get_model_by_id(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 법인 정보 수정
        company.name = request.form.get('company_name', company.name).strip()
        company.representative = request.form.get('representative', company.representative).strip()
        company.business_type = request.form.get('business_type', '').strip() or None
        company.business_category = request.form.get('business_category', '').strip() or None
        company.phone = request.form.get('phone', '').strip() or None
        company.email = request.form.get('company_email', '').strip() or None
        company.website = request.form.get('website', '').strip() or None
        company.address = request.form.get('address', '').strip() or None
        company.address_detail = request.form.get('address_detail', '').strip() or None
        company.postal_code = request.form.get('postal_code', '').strip() or None

        try:
            db.session.commit()
            flash('법인 정보가 수정되었습니다.', 'success')
            return redirect(url_for('corporate.settings'))
        except Exception as e:
            db.session.rollback()
            flash(f'수정 중 오류가 발생했습니다: {str(e)}', 'error')

    return render_template('corporate/settings.html', company=company)


@corporate_bp.route('/users')
@corporate_admin_required
def users():
    """법인 계정관리 (employee_sub만 표시)

    21번 원칙: 법인 계정(employee_sub)만 표시
    personal 계정은 외부 사용자이므로 제외
    """
    company_id = session.get(SessionKeys.COMPANY_ID)
    if not company_id:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    company = company_repository.get_model_by_id(company_id)
    if not company:
        flash('법인 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 법인 계정(employee_sub)만 표시
    users = user_repo.get_by_company_and_account_type(
        company_id, User.ACCOUNT_EMPLOYEE_SUB
    )

    return render_template('corporate/users.html', company=company, users=users)


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
        return jsonify({'error': '사업자등록번호를 입력해주세요.'}), 400

    exists = company_repository.exists_by_business_number(business_number)
    return jsonify({'exists': exists, 'available': not exists})


@corporate_bp.route('/api/company/<int:company_id>')
@corporate_login_required
def get_company(company_id):
    """법인 정보 조회 API"""
    # 자신의 법인 정보만 조회 가능
    if session.get(SessionKeys.COMPANY_ID) != company_id:
        return jsonify({'error': '접근 권한이 없습니다.'}), 403

    company = company_repository.get_with_stats(company_id)
    if not company:
        return jsonify({'error': '법인 정보를 찾을 수 없습니다.'}), 404

    return jsonify(company)
