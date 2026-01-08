"""
Account Management Routes

Account settings, password change, privacy settings, account deletion
Phase 1 Migration: domains/user/blueprints/account/routes.py
"""
from flask import render_template, request, redirect, url_for, flash, session

from . import account_bp
from .helpers import validate_password_change
from app.shared.constants.session_keys import SessionKeys
from app.shared.utils.decorators import login_required
from app.domains.user.services.user_service import user_service
from app.domains.employee.services import employee_service
from app.domains.user.services.personal_service import personal_service


@account_bp.route('/settings')
@login_required
def settings():
    """Account settings main page"""
    user_id = session.get(SessionKeys.USER_ID)
    user = user_service.get_model_by_id(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # Employee info (if linked)
    employee = None
    if user.employee_id:
        employee = employee_service.get_employee_by_id(user.employee_id)

    return render_template('domains/user/account/settings.html',
                           user=user,
                           employee=employee)


@account_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    """Password change"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # Validation using helper (DRY principle)
        is_valid, error = validate_password_change(
            current_password, new_password, confirm_password
        )
        if not is_valid:
            flash(error, 'error')
            return render_template('domains/user/account/password.html')

        # Verify current password
        user = user_service.authenticate(session['username'], current_password)
        if not user:
            flash('현재 비밀번호가 올바르지 않습니다.', 'error')
            return render_template('domains/user/account/password.html')

        # Change password
        if user_service.update_password(session[SessionKeys.USER_ID], new_password):
            flash('비밀번호가 변경되었습니다.', 'success')
            return redirect(url_for('account.settings'))
        else:
            flash('비밀번호 변경에 실패했습니다.', 'error')

    return render_template('domains/user/account/password.html')


@account_bp.route('/privacy', methods=['GET', 'POST'])
@login_required
def privacy():
    """Privacy settings"""
    user_id = session.get(SessionKeys.USER_ID)
    user = user_service.get_model_by_id(user_id)
    account_type = session.get(SessionKeys.ACCOUNT_TYPE)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # Get profile for personal account
    profile = None
    if account_type == 'personal':
        _, profile = personal_service.get_user_with_profile(user_id)

    if request.method == 'POST':
        # Save privacy settings
        privacy_settings = {
            'show_email': request.form.get('show_email') == 'on',
            'show_phone': request.form.get('show_phone') == 'on',
            'show_address': request.form.get('show_address') == 'on',
            'show_birth_date': request.form.get('show_birth_date') == 'on',
            'show_profile_photo': request.form.get('show_profile_photo') == 'on',
        }

        # Personal account: Profile public setting (job search activity)
        if account_type == 'personal' and profile:
            is_public = request.form.get('is_public') == 'on'
            personal_service.update_profile(user_id, {'is_public': is_public})

        # Update user privacy_settings
        if user_service.update_privacy_settings(user_id, privacy_settings):
            flash('공개 설정이 저장되었습니다.', 'success')
            return redirect(url_for('account.settings'))
        else:
            flash('공개 설정 저장에 실패했습니다.', 'error')

    # Get current privacy settings
    privacy_settings = user_service.get_privacy_settings(user_id) or {}

    return render_template('domains/user/account/privacy.html',
                           user=user,
                           privacy_settings=privacy_settings,
                           profile=profile,
                           account_type=account_type)


@account_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    """Account deletion"""
    user_id = session.get(SessionKeys.USER_ID)
    user = user_service.get_model_by_id(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_text = request.form.get('confirm_text', '')

        # Verify password
        authenticated = user_service.authenticate(session['username'], password)
        if not authenticated:
            flash('비밀번호가 올바르지 않습니다.', 'error')
            return render_template('domains/user/account/delete.html', user=user)

        # Verify confirmation text
        if confirm_text != '계정 탈퇴':
            flash('"계정 탈퇴"를 정확히 입력해주세요.', 'error')
            return render_template('domains/user/account/delete.html', user=user)

        # Deactivate account (soft delete)
        if user_service.deactivate(user_id):
            session.clear()
            flash('계정이 탈퇴 처리되었습니다.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('계정 탈퇴에 실패했습니다. 관리자에게 문의해주세요.', 'error')

    return render_template('domains/user/account/delete.html', user=user)
