"""
Promotion SQLAlchemy 모델

직원 발령/인사이동 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Promotion(DictSerializableMixin, db.Model):
    """발령/인사이동 모델"""
    __tablename__ = 'promotions'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'effective_date': ['effectiveDate'],
        'promotion_type': ['promotionType'],
        'from_department': ['fromDepartment'],
        'to_department': ['toDepartment'],
        'from_position': ['fromPosition'],
        'to_position': ['toPosition'],
        'job_role': ['jobRole'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    effective_date = db.Column(db.String(20), nullable=True)
    promotion_type = db.Column(db.String(50), nullable=True)
    from_department = db.Column(db.String(100), nullable=True)
    to_department = db.Column(db.String(100), nullable=True)
    from_position = db.Column(db.String(100), nullable=True)
    to_position = db.Column(db.String(100), nullable=True)
    job_role = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Promotion {self.id}: {self.employee_id}>'
