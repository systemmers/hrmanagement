"""
인증 Blueprint

로그인/로그아웃 및 세션 관리를 처리합니다.
Phase 2: Service 계층 표준화
Phase 24: EmployeeStatus 상수 일관성 적용
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ..shared.constants.session_keys import SessionKeys
from ..shared.constants.messages import FlashMessages
from ..shared.constants.status import EmployeeStatus
from ..services.user_service import user_service
from app.domains.employee.services import employee_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 및 처리"""
    # 이미 로그인된 경우 대시보드로
    if session.get(SessionKeys.USER_ID):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # 필수 입력 검증
        if not username or not password:
            flash(FlashMessages.ENTER_USERNAME_PASSWORD, 'error')
            return render_template('auth/login.html')

        # 인증 시도
        user = user_service.authenticate(username, password)
        if user:
            # 세션에 사용자 정보 저장
            session[SessionKeys.USER_ID] = user.id
            session[SessionKeys.USERNAME] = user.username
            session[SessionKeys.USER_ROLE] = user.role
            session[SessionKeys.EMPLOYEE_ID] = user.employee_id
            # Phase 1: 계정 유형 및 법인 정보 추가
            session[SessionKeys.ACCOUNT_TYPE] = user.account_type
            session[SessionKeys.COMPANY_ID] = user.company_id
            # Platform Admin: 슈퍼관리자 여부
            session[SessionKeys.IS_SUPERADMIN] = user.is_superadmin

            flash(FlashMessages.WELCOME_TEMPLATE.format(user.username), 'success')

            # 슈퍼관리자인 경우 플랫폼 대시보드로
            if user.is_superadmin:
                return redirect(url_for('platform.dashboard'))

            # 계정 발급 후 직원 상태별 분기 (pending_info, pending_contract)
            if user.employee_id and user.account_type == 'employee_sub':
                employee = employee_service.get_employee_model_by_id(user.employee_id)
                if employee:
                    if employee.status == EmployeeStatus.PENDING_INFO:
                        flash('프로필 정보를 완성해주세요.', 'info')
                        return redirect(url_for('profile.complete_profile'))
                    elif employee.status == EmployeeStatus.PENDING_CONTRACT:
                        flash('계약 요청을 기다리고 있습니다.', 'info')
                        return redirect(url_for('mypage.company_info'))

            # next 파라미터가 있으면 해당 페이지로, 없으면 대시보드로
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash(FlashMessages.INVALID_CREDENTIALS, 'error')
            return render_template('auth/login.html', username=username)

    return render_template('auth/login.html')


@auth_bp.route('/register')
def register():
    """회원가입 유형 선택 페이지"""
    # 이미 로그인된 경우 대시보드로
    if session.get(SessionKeys.USER_ID):
        return redirect(url_for('main.index'))

    return render_template('auth/register_select.html')


@auth_bp.route('/logout')
def logout():
    """로그아웃 처리"""
    username = session.get(SessionKeys.USERNAME, '사용자')

    # 세션 클리어
    session.clear()

    flash(FlashMessages.LOGGED_OUT_TEMPLATE.format(username), 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """비밀번호 변경"""
    # 로그인 필요
    if not session.get(SessionKeys.USER_ID):
        flash(FlashMessages.LOGIN_REQUIRED, 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 필수 입력 검증
        if not all([current_password, new_password, confirm_password]):
            flash(FlashMessages.FILL_ALL_FIELDS, 'error')
            return render_template('auth/change_password.html')

        # 새 비밀번호 확인
        if new_password != confirm_password:
            flash(FlashMessages.PASSWORD_MISMATCH, 'error')
            return render_template('auth/change_password.html')

        # 비밀번호 길이 검증
        if len(new_password) < 8:
            flash(FlashMessages.PASSWORD_TOO_SHORT, 'error')
            return render_template('auth/change_password.html')

        # 현재 비밀번호 확인
        user = user_service.authenticate(session[SessionKeys.USERNAME], current_password)
        if not user:
            flash(FlashMessages.INVALID_CURRENT_PASSWORD, 'error')
            return render_template('auth/change_password.html')

        # 비밀번호 변경
        if user_service.update_password(session[SessionKeys.USER_ID], new_password):
            flash(FlashMessages.PASSWORD_CHANGED, 'success')
            return redirect(url_for('main.index'))
        else:
            flash(FlashMessages.PASSWORD_CHANGE_FAILED, 'error')

    return render_template('auth/change_password.html')
