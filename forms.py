"""
WTForms 폼 정의 - SSOT 기반 동적 옵션 로딩
"""
import json
import os
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, DateField, TextAreaField
from wtforms.validators import DataRequired, Email, Length, Optional, Regexp


def load_classification_options():
    """classification_options.json에서 선택 옵션 로드 (SSOT)"""
    options_path = os.path.join(os.path.dirname(__file__), 'data', 'classification_options.json')
    with open(options_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_position_choices():
    """직급 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(p, p) for p in options.get('positions', [])]


def get_status_choices():
    """재직 상태 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(s['value'], s['label']) for s in options.get('statuses', [])]


def get_gender_choices():
    """성별 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(g['value'], g['label']) for g in options.get('genders', [])]


def get_employment_type_choices():
    """고용 형태 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(e['value'], e['label']) for e in options.get('employment_types', [])]


def get_work_location_choices():
    """근무지 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(w, w) for w in options.get('work_locations', [])]


def get_emergency_relation_choices():
    """비상연락처 관계 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(r, r) for r in options.get('emergency_relations', [])]


def get_team_choices():
    """팀 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(t, t) for t in options.get('teams', [])]


def get_department_choices():
    """부서 선택 옵션 반환"""
    options = load_classification_options()
    return [('', '선택하세요')] + [(d, d) for d in options.get('departments', [])]


class EmployeeForm(FlaskForm):
    """직원 정보 입력 폼 - 확장 필드 포함"""

    # ===== 기본 필드 =====
    name = StringField('이름', validators=[
        DataRequired(message='이름은 필수 항목입니다.'),
        Length(min=2, max=50, message='이름은 2-50자 이내여야 합니다.')
    ])

    photo = StringField('사진 URL', validators=[
        Length(max=500, message='URL은 500자 이내여야 합니다.')
    ])

    department = SelectField('부서', validators=[
        DataRequired(message='부서는 필수 항목입니다.')
    ])

    position = SelectField('직급', validators=[
        DataRequired(message='직급은 필수 항목입니다.')
    ])

    status = SelectField('재직 상태', validators=[
        DataRequired(message='재직 상태는 필수 항목입니다.')
    ])

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

    # ===== 확장 필드 - 개인정보 =====
    name_en = StringField('영문 이름', validators=[
        Optional(),
        Length(max=100, message='영문 이름은 100자 이내여야 합니다.')
    ])

    birth_date = DateField('생년월일', validators=[Optional()])

    gender = SelectField('성별', validators=[Optional()])

    address = TextAreaField('주소', validators=[
        Optional(),
        Length(max=200, message='주소는 200자 이내여야 합니다.')
    ])

    emergency_contact = StringField('비상연락처', validators=[
        Optional(),
        Length(max=20, message='비상연락처는 20자 이내여야 합니다.')
    ])

    emergency_relation = SelectField('비상연락처 관계', validators=[Optional()])

    rrn = StringField('주민등록번호', validators=[
        Optional(),
        Length(max=14, message='주민등록번호 형식이 올바르지 않습니다.'),
        Regexp(r'^\d{6}-\d\*{6}$', message='주민등록번호 형식: 850520-1****** (마스킹)')
    ])

    # ===== 확장 필드 - 소속정보 =====
    employee_number = StringField('사번', validators=[
        Optional(),
        Length(max=50, message='사번은 50자 이내여야 합니다.')
    ])

    team = SelectField('팀', validators=[Optional()])

    job_title = StringField('직책', validators=[
        Optional(),
        Length(max=100, message='직책은 100자 이내여야 합니다.')
    ])

    work_location = SelectField('근무지', validators=[Optional()])

    internal_phone = StringField('내선번호', validators=[
        Optional(),
        Length(max=20, message='내선번호는 20자 이내여야 합니다.')
    ])

    company_email = StringField('회사 이메일', validators=[
        Optional(),
        Email(message='올바른 이메일 형식이 아닙니다.'),
        Length(max=100, message='회사 이메일은 100자 이내여야 합니다.')
    ])

    # ===== 확장 필드 - 계약정보 =====
    employment_type = SelectField('고용 형태', validators=[Optional()])

    contract_period = StringField('계약 기간', validators=[
        Optional(),
        Length(max=100, message='계약 기간은 100자 이내여야 합니다.')
    ])

    probation_end = DateField('수습 종료일', validators=[Optional()])

    resignation_date = DateField('퇴사일', validators=[Optional()])

    def __init__(self, *args, **kwargs):
        """동적으로 선택 옵션 로딩"""
        super().__init__(*args, **kwargs)

        # 동적 옵션 설정 (SSOT: classification_options.json)
        self.department.choices = get_department_choices()
        self.position.choices = get_position_choices()
        self.status.choices = get_status_choices()
        self.gender.choices = get_gender_choices()
        self.employment_type.choices = get_employment_type_choices()
        self.work_location.choices = get_work_location_choices()
        self.emergency_relation.choices = get_emergency_relation_choices()
        self.team.choices = get_team_choices()
