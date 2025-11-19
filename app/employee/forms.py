"""
직원 관리 폼
직원 등록/수정 폼 정의
"""
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, SelectField, DateField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Email, Optional, Length


class EmployeeForm(FlaskForm):
    """직원 등록/수정 폼"""

    # 기본 정보
    photo = FileField(
        '사진',
        validators=[
            FileAllowed(['jpg', 'jpeg', 'png'], '이미지 파일만 업로드 가능합니다.')
        ]
    )

    name = StringField(
        '성명',
        validators=[
            DataRequired(message='성명을 입력하세요.'),
            Length(max=50, message='성명은 최대 50자까지 입력 가능합니다.')
        ]
    )

    phone = StringField(
        '전화번호',
        validators=[
            Optional(),
            Length(max=20, message='전화번호는 최대 20자까지 입력 가능합니다.')
        ]
    )

    email = StringField(
        '이메일',
        validators=[
            Optional(),
            Email(message='올바른 이메일 형식이 아닙니다.'),
            Length(max=100, message='이메일은 최대 100자까지 입력 가능합니다.')
        ]
    )

    address = TextAreaField(
        '주소',
        validators=[
            Optional(),
            Length(max=255, message='주소는 최대 255자까지 입력 가능합니다.')
        ]
    )

    # 소속 정보
    department_id = SelectField(
        '부서',
        coerce=int,
        validators=[Optional()]
    )

    position_id = SelectField(
        '직급',
        coerce=int,
        validators=[Optional()]
    )

    hire_date = DateField(
        '입사일',
        validators=[Optional()],
        format='%Y-%m-%d'
    )

    employment_type = SelectField(
        '고용형태',
        choices=[
            ('', '선택'),
            ('정규직', '정규직'),
            ('계약직', '계약직'),
            ('인턴', '인턴'),
            ('프리랜서', '프리랜서')
        ],
        validators=[Optional()]
    )

    workplace = StringField(
        '근무지',
        validators=[
            Optional(),
            Length(max=100, message='근무지는 최대 100자까지 입력 가능합니다.')
        ]
    )

    # 상태
    status = SelectField(
        '상태',
        choices=[
            ('active', '정상'),
            ('warning', '주의'),
            ('expired', '만료')
        ],
        default='active',
        validators=[DataRequired()]
    )

    submit = SubmitField('저장')
