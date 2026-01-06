"""
SalaryHistory SQLAlchemy 모델

직원 연봉 계약 이력을 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from .mixins import DictSerializableMixin


class SalaryHistory(DictSerializableMixin, db.Model):
    """연봉 계약 이력 모델"""
    __tablename__ = 'salary_histories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    contract_year = db.Column(db.Integer, nullable=True)
    annual_salary = db.Column(db.Integer, default=0)
    bonus = db.Column(db.Integer, default=0)
    total_amount = db.Column(db.Integer, default=0)
    contract_period = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<SalaryHistory {self.id}: {self.employee_id}>'
