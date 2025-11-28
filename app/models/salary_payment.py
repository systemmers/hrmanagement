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
    total_allowances = db.Column(db.Integer, default=0)
    total_deductions = db.Column(db.Integer, default=0)
    net_salary = db.Column(db.Integer, default=0)
    payment_method = db.Column(db.String(50), nullable=True)
    payment_status = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'paymentDate': self.payment_date,
            'paymentPeriod': self.payment_period,
            'baseSalary': self.base_salary,
            'totalAllowances': self.total_allowances,
            'totalDeductions': self.total_deductions,
            'netSalary': self.net_salary,
            'paymentMethod': self.payment_method,
            'paymentStatus': self.payment_status,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            payment_date=data.get('paymentDate'),
            payment_period=data.get('paymentPeriod'),
            base_salary=data.get('baseSalary', 0),
            total_allowances=data.get('totalAllowances', 0),
            total_deductions=data.get('totalDeductions', 0),
            net_salary=data.get('netSalary', 0),
            payment_method=data.get('paymentMethod'),
            payment_status=data.get('paymentStatus'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<SalaryPayment {self.id}: {self.employee_id} {self.payment_date}>'
