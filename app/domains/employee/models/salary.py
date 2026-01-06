"""
Salary SQLAlchemy 모델

직원 급여 정보를 관리합니다. (1:1 관계)
포괄임금제 급여 계산 지원
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from .mixins import DictSerializableMixin


class Salary(DictSerializableMixin, db.Model):
    """급여 모델 (1:1)"""
    __tablename__ = 'salaries'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    salary_type = db.Column(db.String(50), nullable=True)
    base_salary = db.Column(db.Integer, default=0)
    position_allowance = db.Column(db.Integer, default=0)
    meal_allowance = db.Column(db.Integer, default=0)
    transportation_allowance = db.Column(db.Integer, default=0)
    total_salary = db.Column(db.Integer, default=0)
    payment_day = db.Column(db.Integer, default=25)
    payment_method = db.Column(db.String(50), nullable=True)
    bank_account = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    # 포괄임금제 관련 필드
    annual_salary = db.Column(db.Integer, default=0)           # 연봉
    monthly_salary = db.Column(db.Integer, default=0)          # 월급여
    hourly_wage = db.Column(db.Integer, default=0)             # 통상임금(시급)

    # 포괄임금 포함 근무시간
    overtime_hours = db.Column(db.Integer, default=0)          # 월 연장근로시간
    night_hours = db.Column(db.Integer, default=0)             # 월 야간근로시간
    holiday_days = db.Column(db.Integer, default=0)            # 월 휴일근로일수

    # 수당 상세
    overtime_allowance = db.Column(db.Integer, default=0)      # 연장근로수당
    night_allowance = db.Column(db.Integer, default=0)         # 야간근로수당
    holiday_allowance = db.Column(db.Integer, default=0)       # 휴일근로수당
    bonus_rate = db.Column(db.Integer, default=0)              # 상여금률 (%)

    def __repr__(self):
        return f'<Salary {self.id}: {self.employee_id}>'
