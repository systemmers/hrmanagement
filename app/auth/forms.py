"""
인증 폼
로그인 폼 정의
"""
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField
from wtforms.validators import DataRequired, Length


class LoginForm(FlaskForm):
    """로그인 폼"""

    username = StringField(
        '아이디',
        validators=[
            DataRequired(message='아이디를 입력하세요.'),
            Length(min=3, max=50, message='아이디는 3-50자여야 합니다.')
        ]
    )

    password = PasswordField(
        '비밀번호',
        validators=[
            DataRequired(message='비밀번호를 입력하세요.'),
            Length(min=6, message='비밀번호는 최소 6자 이상이어야 합니다.')
        ]
    )

    remember_me = BooleanField('로그인 상태 유지')

    submit = SubmitField('로그인')
