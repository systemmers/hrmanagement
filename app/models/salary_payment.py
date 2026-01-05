"""
SalaryPayment SQLAlchemy 모델

직원 급여 지급 이력을 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class SalaryPayment(DictSerializableMixin, db.Model):
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

    def __repr__(self):
        return f'<SalaryPayment {self.id}: {self.employee_id} {self.payment_date}>'
