"""
SalaryHistory SQLAlchemy 모델

직원 연봉 계약 이력을 관리합니다.
"""
from app.database import db


class SalaryHistory(db.Model):
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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'contract_year': self.contract_year,
            'annual_salary': self.annual_salary,
            'bonus': self.bonus,
            'total_amount': self.total_amount,
            'contract_period': self.contract_period,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            contract_year=data.get('contract_year') or data.get('contractYear'),
            annual_salary=data.get('annual_salary') or data.get('annualSalary', 0),
            bonus=data.get('bonus', 0),
            total_amount=data.get('total_amount') or data.get('totalAmount', 0),
            contract_period=data.get('contract_period') or data.get('contractPeriod'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<SalaryHistory {self.id}: {self.employee_id}>'
