"""
Contract SQLAlchemy 모델

직원 계약 정보를 관리합니다. (1:1 관계)
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Contract(DictSerializableMixin, db.Model):
    """계약 모델 (1:1)"""
    __tablename__ = 'contracts'

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
