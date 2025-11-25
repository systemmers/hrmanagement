"""
WTForms 폼 정의
"""
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField
from wtforms.validators import DataRequired, Email, Length


class EmployeeForm(FlaskForm):
    """직원 정보 입력 폼"""
    
    name = StringField('이름', validators=[
        DataRequired(message='이름은 필수 항목입니다.'),
        Length(min=2, max=50, message='이름은 2-50자 이내여야 합니다.')
    ])
    
    photo = StringField('사진 URL', validators=[
        Length(max=500, message='URL은 500자 이내여야 합니다.')
    ])
    
    department = StringField('부서', validators=[
        DataRequired(message='부서는 필수 항목입니다.'),
        Length(max=100, message='부서명은 100자 이내여야 합니다.')
    ])
    
    position = SelectField('직급', choices=[
        ('사원', '사원'),
        ('대리', '대리'),
        ('과장', '과장'),
        ('차장', '차장'),
        ('부장', '부장'),
        ('이사', '이사'),
        ('상무', '상무'),
        ('전무', '전무'),
        ('대표', '대표')
    ], validators=[DataRequired(message='직급은 필수 항목입니다.')])
    
    status = SelectField('재직 상태', choices=[
        ('active', '정상'),
        ('warning', '대기'),
        ('expired', '만료')
    ], validators=[DataRequired(message='재직 상태는 필수 항목입니다.')])
    
    hireDate = DateField('입사일', validators=[
        DataRequired(message='입사일은 필수 항목입니다.')
    ])
    
    phone = StringField('전화번호', validators=[
        DataRequired(message='전화번호는 필수 항목입니다.'),
        Length(min=10, max=20, message='전화번호 형식이 올바르지 않습니다.')
    ])
    
    email = StringField('이메일', validators=[
        DataRequired(message='이메일은 필수 항목입니다.'),
        Email(message='올바른 이메일 형식이 아닙니다.'),
        Length(max=100, message='이메일은 100자 이내여야 합니다.')
    ])

