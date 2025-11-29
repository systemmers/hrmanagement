"""
인증 Blueprint

로그인/로그아웃 및 세션 관리를 처리합니다.
"""
from flask import Blueprint, render_template, request, redirect, url_for, flash, session

from ..extensions import user_repo

auth_bp = Blueprint('auth', __name__, url_prefix='/auth')


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 및 처리"""
    # 이미 로그인된 경우 대시보드로
    if session.get('user_id'):
        return redirect(url_for('main.index'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        # 필수 입력 검증
        if not username or not password:
            flash('사용자명과 비밀번호를 입력해주세요.', 'error')
            return render_template('auth/login.html')

        # 인증 시도
        user = user_repo.authenticate(username, password)
        if user:
            # 세션에 사용자 정보 저장
            session['user_id'] = user.id
            session['username'] = user.username
            session['user_role'] = user.role
            session['employee_id'] = user.employee_id

            flash(f'{user.username}님, 환영합니다!', 'success')

            # next 파라미터가 있으면 해당 페이지로, 없으면 대시보드로
            next_page = request.args.get('next')
            if next_page and next_page.startswith('/'):
                return redirect(next_page)
            return redirect(url_for('main.index'))
        else:
            flash('사용자명 또는 비밀번호가 올바르지 않습니다.', 'error')
            return render_template('auth/login.html', username=username)

    return render_template('auth/login.html')


@auth_bp.route('/logout')
def logout():
    """로그아웃 처리"""
    username = session.get('username', '사용자')

    # 세션 클리어
    session.clear()

    flash(f'{username}님이 로그아웃되었습니다.', 'success')
    return redirect(url_for('auth.login'))


@auth_bp.route('/change-password', methods=['GET', 'POST'])
def change_password():
    """비밀번호 변경"""
    # 로그인 필요
    if not session.get('user_id'):
        flash('로그인이 필요합니다.', 'error')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        current_password = request.form.get('current_password', '')
        new_password = request.form.get('new_password', '')
        confirm_password = request.form.get('confirm_password', '')

        # 필수 입력 검증
        if not all([current_password, new_password, confirm_password]):
            flash('모든 필드를 입력해주세요.', 'error')
            return render_template('auth/change_password.html')

        # 새 비밀번호 확인
        if new_password != confirm_password:
            flash('새 비밀번호가 일치하지 않습니다.', 'error')
            return render_template('auth/change_password.html')

        # 비밀번호 길이 검증
        if len(new_password) < 8:
            flash('비밀번호는 최소 8자 이상이어야 합니다.', 'error')
            return render_template('auth/change_password.html')

        # 현재 비밀번호 확인
        user = user_repo.authenticate(session['username'], current_password)
        if not user:
            flash('현재 비밀번호가 올바르지 않습니다.', 'error')
            return render_template('auth/change_password.html')

        # 비밀번호 변경
        if user_repo.update_password(session['user_id'], new_password):
            flash('비밀번호가 변경되었습니다.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('비밀번호 변경에 실패했습니다.', 'error')

    return render_template('auth/change_password.html')
