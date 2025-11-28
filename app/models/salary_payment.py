"""
SalaryPayment SQLAlchemy 모델

직원 급여 지급 이력을 관리합니다.
"""
from app.database import db


class SalaryPayment(db.Model):
    """급여 지급 모델"""
    __tablename__ = 'salary_payments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    payment_date = db.Column(db.String(20), nullable=True, index=True)
    payment_period = db.Column(db.String(50), nullable=True)
    base_salary = db.Column(db.Integer, default=0)
    allowances = db.Column(db.Integer, default=0)
    gross_pay = db.Column(db.Integer, default=0)
    insurance = db.Column(db.Integer, default=0)
    income_tax = db.Column(db.Integer, default=0)
    total_deduction = db.Column(db.Integer, default=0)
    net_pay = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'payment_date': self.payment_date,
            'payment_period': self.payment_period,
            'base_salary': self.base_salary,
            'allowances': self.allowances,
            'gross_pay': self.gross_pay,
            'insurance': self.insurance,
            'income_tax': self.income_tax,
            'total_deduction': self.total_deduction,
            'net_pay': self.net_pay,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            payment_date=data.get('payment_date') or data.get('paymentDate'),
            payment_period=data.get('payment_period') or data.get('paymentPeriod'),
            base_salary=data.get('base_salary') or data.get('baseSalary', 0),
            allowances=data.get('allowances', 0),
            gross_pay=data.get('gross_pay') or data.get('grossPay', 0),
            insurance=data.get('insurance', 0),
            income_tax=data.get('income_tax') or data.get('incomeTax', 0),
            total_deduction=data.get('total_deduction') or data.get('totalDeduction', 0),
            net_pay=data.get('net_pay') or data.get('netPay', 0),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<SalaryPayment {self.id}: {self.employee_id} {self.payment_date}>'
