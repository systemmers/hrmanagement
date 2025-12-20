"""
Benefit SQLAlchemy 모델

직원 복리후생 정보를 관리합니다. (1:1 관계)
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Benefit(DictSerializableMixin, db.Model):
    """복리후생 모델 (1:1)"""
    __tablename__ = 'benefits'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'annual_leave_granted': ['annualLeaveGranted'],
        'annual_leave_used': ['annualLeaveUsed'],
        'annual_leave_remaining': ['annualLeaveRemaining'],
        'severance_type': ['severanceType'],
        'severance_method': ['severanceMethod'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    year = db.Column(db.Integer, nullable=True)
    annual_leave_granted = db.Column(db.Integer, default=0)
    annual_leave_used = db.Column(db.Integer, default=0)
    annual_leave_remaining = db.Column(db.Integer, default=0)
    severance_type = db.Column(db.String(50), nullable=True)
    severance_method = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Benefit {self.id}: {self.employee_id}>'
