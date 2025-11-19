"""
인증 라우트
로그인/로그아웃 처리
"""
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, current_user
from app.auth import auth_bp
from app.auth.forms import LoginForm
from app.models import User


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    """로그인 페이지 및 처리"""
    # 이미 로그인한 경우 대시보드로 리다이렉트
    if current_user.is_authenticated:
        return redirect(url_for('employee.index'))

    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember_me.data)
            flash(f'{user.name}님, 환영합니다!', 'success')

            # 로그인 전 접근하려던 페이지로 리다이렉트
            next_page = request.args.get('next')
            if next_page:
                return redirect(next_page)
            return redirect(url_for('employee.index'))
        else:
            flash('아이디 또는 비밀번호가 올바르지 않습니다.', 'danger')

    return render_template('auth/login.html', form=form)


@auth_bp.route('/logout')
def logout():
    """로그아웃"""
    logout_user()
    flash('로그아웃되었습니다.', 'info')
    return redirect(url_for('auth.login'))
