"""
계정 관리 라우트

계정 설정, 비밀번호 변경, 개인정보 공개 설정, 계정 탈퇴 기능을 제공합니다.
"""
from flask import render_template, request, redirect, url_for, flash, session

from . import account_bp
from ...utils.decorators import login_required
from ...extensions import user_repo, employee_repo


@account_bp.route('/settings')
@login_required
def settings():
    """계정 설정 메인 페이지"""
    user_id = session.get('user_id')
    user = user_repo.get_by_id(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    # 직원 정보 (연결된 경우)
    employee = None
    if user.employee_id:
        employee = employee_repo.get_by_id(user.employee_id)

    return render_template('account/settings.html',
                           user=user,
                           employee=employee)


@account_bp.route('/password', methods=['GET', 'POST'])
@login_required
def password():
    """비밀번호 변경"""
    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 필수 입력 검증
        if not all([current_password, new_password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('account/password.html')

        # 새 비밀번호 확인
        if new_password != confirm_password:
            flash('새 비밀번호가 일치하지 않습니다.', 'error')
            return render_template('account/password.html')

        # 비밀번호 길이 검증
        if len(new_password) < 8:
            flash('비밀번호는 최소 8자 이상이어야 합니다.', 'error')
            return render_template('account/password.html')

        # 현재 비밀번호 확인
        user = user_repo.authenticate(session['username'], current_password)
        if not user:
            flash('현재 비밀번호가 올바르지 않습니다.', 'error')
            return render_template('account/password.html')

        # 비밀번호 변경
        if user_repo.update_password(session['user_id'], new_password):
            flash('비밀번호가 변경되었습니다.', 'success')
            return redirect(url_for('account.settings'))
        else:
            flash('비밀번호 변경에 실패했습니다.', 'error')

    return render_template('account/password.html')


@account_bp.route('/privacy', methods=['GET', 'POST'])
@login_required
def privacy():
    """개인정보 공개 설정"""
    user_id = session.get('user_id')
    user = user_repo.get_by_id(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        # 공개 설정 저장
        privacy_settings = {
            'show_email': request.form.get('show_email') == 'on',
            'show_phone': request.form.get('show_phone') == 'on',
            'show_address': request.form.get('show_address') == 'on',
            'show_birth_date': request.form.get('show_birth_date') == 'on',
            'show_profile_photo': request.form.get('show_profile_photo') == 'on',
        }

        # 사용자 privacy_settings 업데이트
        if user_repo.update_privacy_settings(user_id, privacy_settings):
            flash('공개 설정이 저장되었습니다.', 'success')
            return redirect(url_for('account.settings'))
        else:
            flash('공개 설정 저장에 실패했습니다.', 'error')

    # 현재 공개 설정 조회
    privacy_settings = user_repo.get_privacy_settings(user_id) or {}

    return render_template('account/privacy.html',
                           user=user,
                           privacy_settings=privacy_settings)


@account_bp.route('/delete', methods=['GET', 'POST'])
@login_required
def delete():
    """계정 탈퇴"""
    user_id = session.get('user_id')
    user = user_repo.get_by_id(user_id)

    if not user:
        flash('사용자 정보를 찾을 수 없습니다.', 'error')
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        password = request.form.get('password', '')
        confirm_text = request.form.get('confirm_text', '')

        # 비밀번호 확인
        authenticated = user_repo.authenticate(session['username'], password)
        if not authenticated:
            flash('비밀번호가 올바르지 않습니다.', 'error')
            return render_template('account/delete.html', user=user)

        # 확인 텍스트 검증
        if confirm_text != '계정 탈퇴':
            flash('"계정 탈퇴"를 정확히 입력해주세요.', 'error')
            return render_template('account/delete.html', user=user)

        # 계정 비활성화 (soft delete)
        if user_repo.deactivate(user_id):
            session.clear()
            flash('계정이 탈퇴 처리되었습니다.', 'success')
            return redirect(url_for('auth.login'))
        else:
            flash('계정 탈퇴에 실패했습니다. 관리자에게 문의해주세요.', 'error')

    return render_template('account/delete.html', user=user)
