"""
Contract SQLAlchemy 모델

직원 계약 정보를 관리합니다. (1:1 관계)
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Contract(DictSerializableMixin, db.Model):
    """계약 모델 (1:1)"""
    __tablename__ = 'contracts'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'contract_date': ['contractDate'],
        'contract_type': ['contractType'],
        'contract_period': ['contractPeriod'],
        'employee_type': ['employeeType', 'employment_type'],
        'work_type': ['workType'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    contract_date = db.Column(db.String(20), nullable=True)
    contract_type = db.Column(db.String(50), nullable=True)
    contract_period = db.Column(db.String(50), nullable=True)
    employee_type = db.Column(db.String(50), nullable=True)
    work_type = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Contract {self.id}: {self.employee_id}>'
