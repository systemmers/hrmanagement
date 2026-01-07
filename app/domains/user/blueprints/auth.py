"""
User Domain: Authentication Blueprint

Phase 1 Migration: domains/user/blueprints/auth.py
- Login/logout and session management
- Password change functionality
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from app.shared.constants.session_keys import SessionKeys
from app.shared.constants.messages import FlashMessages
from app.shared.constants.status import EmployeeStatus
from app.domains.user.services.user_service import user_service
from app.domains.employee.services import employee_service

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """Login page and authentication handler"""
    # Redirect to dashboard if already logged in
    if session.get(SessionKeys.USER_ID):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # Required field validation
        if not username or not password:
            flash(FlashMessages.ENTER_USERNAME_PASSWORD, 'error')
            return render_template('domains/user/auth/login.html')

        # Authentication attempt
        user = user_service.authenticate(username, password)
        if user:
            # Store user info in session
            session[SessionKeys.USER_ID] = user.id
            session[SessionKeys.USERNAME] = user.username
            session[SessionKeys.USER_ROLE] = user.role
            session[SessionKeys.EMPLOYEE_ID] = user.employee_id
            # Phase 1: Account type and company info
            session[SessionKeys.ACCOUNT_TYPE] = user.account_type
            session[SessionKeys.COMPANY_ID] = user.company_id
            # Platform Admin: Superadmin flag
            session[SessionKeys.IS_SUPERADMIN] = user.is_superadmin

            flash(FlashMessages.WELCOME_TEMPLATE.format(user.username), 'success')

            # Redirect superadmin to platform dashboard
            if user.is_superadmin:
                return redirect(url_for('platform.dashboard'))

            # Branch by employee status after account creation
            if user.employee_id and user.account_type == 'employee_sub':
                employee = employee_service.get_employee_model_by_id(user.employee_id)
                if employee:
                    if employee.status == EmployeeStatus.PENDING_INFO:
                        flash('프로필 정보를 완성해주세요.', 'info')
                        return redirect(url_for('profile.complete_profile'))
                    elif employee.status == EmployeeStatus.PENDING_CONTRACT:
                        flash('계약 요청을 기다리고 있습니다.', 'info')
                        return redirect(url_for('mypage.company_info'))

            # Redirect to next parameter or dashboard
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash(FlashMessages.INVALID_CREDENTIALS, 'error')
            return render_template('domains/user/auth/login.html', username=username)

    return render_template('domains/user/auth/login.html')


@auth_bp.route('/register')
def register():
    """Registration type selection page"""
    # Redirect to dashboard if already logged in
    if session.get(SessionKeys.USER_ID):
        return redirect(url_for('main.index'))

    return render_template('domains/user/auth/register_select.html')


@auth_bp.route('/logout')
def logout():
    """Logout handler"""
    username = session.get(SessionKeys.USERNAME, 'user')

    # Clear session
    session.clear()

    flash(FlashMessages.LOGGED_OUT_TEMPLATE.format(username), 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """Password change handler"""
    # Login required
    if not session.get(SessionKeys.USER_ID):
        flash(FlashMessages.LOGIN_REQUIRED, 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Required field validation
        if not all([current_password, new_password, confirm_password]):
            flash(FlashMessages.FILL_ALL_FIELDS, 'error')
            return render_template('domains/user/auth/change_password.html')

        # New password confirmation
        if new_password != confirm_password:
            flash(FlashMessages.PASSWORD_MISMATCH, 'error')
            return render_template('domains/user/auth/change_password.html')

        # Password length validation
        if len(new_password) < 8:
            flash(FlashMessages.PASSWORD_TOO_SHORT, 'error')
            return render_template('domains/user/auth/change_password.html')

        # Verify current password
        user = user_service.authenticate(session[SessionKeys.USERNAME], current_password)
        if not user:
            flash(FlashMessages.INVALID_CURRENT_PASSWORD, 'error')
            return render_template('domains/user/auth/change_password.html')

        # Change password
        if user_service.update_password(session[SessionKeys.USER_ID], new_password):
            flash(FlashMessages.PASSWORD_CHANGED, 'success')
            return redirect(url_for('main.index'))
        else:
            flash(FlashMessages.PASSWORD_CHANGE_FAILED, 'error')

    return render_template('domains/user/auth/change_password.html')
