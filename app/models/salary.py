"""
Salary SQLAlchemy 모델

직원 급여 정보를 관리합니다. (1:1 관계)
포괄임금제 급여 계산 지원
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Salary(DictSerializableMixin, db.Model):
    """급여 모델 (1:1)"""
    __tablename__ = 'salaries'

    # Alias 정의: 템플릿 호환성 (to_dict에서 추가 키로 포함)
    __dict_aliases__ = {
        'transport_allowance': 'transportation_allowance',
        'pay_type': 'salary_type',
    }

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'salary_type': ['salaryType', 'pay_type'],
        'base_salary': ['baseSalary'],
        'position_allowance': ['positionAllowance'],
        'meal_allowance': ['mealAllowance'],
        'transportation_allowance': ['transportationAllowance', 'transport_allowance'],
        'total_salary': ['totalSalary'],
        'payment_day': ['paymentDay'],
        'payment_method': ['paymentMethod'],
        'bank_account': ['bankAccount'],
        'annual_salary': ['annualSalary'],
        'monthly_salary': ['monthlySalary'],
        'hourly_wage': ['hourlyWage'],
        'overtime_hours': ['overtimeHours'],
        'night_hours': ['nightHours'],
        'holiday_days': ['holidayDays'],
        'overtime_allowance': ['overtimeAllowance'],
        'night_allowance': ['nightAllowance'],
        'holiday_allowance': ['holidayAllowance'],
    }

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

    # 템플릿 호환성 프로퍼티 (transport_allowance -> transportation_allowance)
    @property
    def transport_allowance(self):
        """템플릿 호환성: transport_allowance -> transportation_allowance"""
        return self.transportation_allowance

    @transport_allowance.setter
    def transport_allowance(self, value):
        self.transportation_allowance = value

    # 템플릿 호환성 프로퍼티 (pay_type -> salary_type)
    @property
    def pay_type(self):
        """템플릿 호환성: pay_type -> salary_type"""
        return self.salary_type

    @pay_type.setter
    def pay_type(self, value):
        self.salary_type = value

    def __repr__(self):
        return f'<Salary {self.id}: {self.employee_id}>'
