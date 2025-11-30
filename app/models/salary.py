"""
Salary SQLAlchemy 모델

직원 급여 정보를 관리합니다. (1:1 관계)
포괄임금제 급여 계산 지원
"""
from app.database import db


class Salary(db.Model):
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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'salary_type': self.salary_type,
            'base_salary': self.base_salary,
            'position_allowance': self.position_allowance,
            'meal_allowance': self.meal_allowance,
            'transportation_allowance': self.transportation_allowance,
            'total_salary': self.total_salary,
            'payment_day': self.payment_day,
            'payment_method': self.payment_method,
            'bank_account': self.bank_account,
            'note': self.note,
            # 포괄임금제 관련 필드
            'annual_salary': self.annual_salary,
            'monthly_salary': self.monthly_salary,
            'hourly_wage': self.hourly_wage,
            'overtime_hours': self.overtime_hours,
            'night_hours': self.night_hours,
            'holiday_days': self.holiday_days,
            'overtime_allowance': self.overtime_allowance,
            'night_allowance': self.night_allowance,
            'holiday_allowance': self.holiday_allowance,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성 (snake_case 지원)"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            salary_type=data.get('salary_type') or data.get('salaryType'),
            base_salary=data.get('base_salary') or data.get('baseSalary', 0),
            position_allowance=data.get('position_allowance') or data.get('positionAllowance', 0),
            meal_allowance=data.get('meal_allowance') or data.get('mealAllowance', 0),
            transportation_allowance=data.get('transportation_allowance') or data.get('transportationAllowance', 0),
            total_salary=data.get('total_salary') or data.get('totalSalary', 0),
            payment_day=data.get('payment_day') or data.get('paymentDay', 25),
            payment_method=data.get('payment_method') or data.get('paymentMethod'),
            bank_account=data.get('bank_account') or data.get('bankAccount'),
            note=data.get('note'),
            # 포괄임금제 관련 필드
            annual_salary=data.get('annual_salary') or data.get('annualSalary', 0),
            monthly_salary=data.get('monthly_salary') or data.get('monthlySalary', 0),
            hourly_wage=data.get('hourly_wage') or data.get('hourlyWage', 0),
            overtime_hours=data.get('overtime_hours') or data.get('overtimeHours', 0),
            night_hours=data.get('night_hours') or data.get('nightHours', 0),
            holiday_days=data.get('holiday_days') or data.get('holidayDays', 0),
            overtime_allowance=data.get('overtime_allowance') or data.get('overtimeAllowance', 0),
            night_allowance=data.get('night_allowance') or data.get('nightAllowance', 0),
            holiday_allowance=data.get('holiday_allowance') or data.get('holidayAllowance', 0),
        )

    def __repr__(self):
        return f'<Salary {self.id}: {self.employee_id}>'
