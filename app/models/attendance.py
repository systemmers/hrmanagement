"""
Attendance SQLAlchemy 모델

직원 근태 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Attendance(DictSerializableMixin, db.Model):
    """근태 모델 (월별 집계)"""
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    work_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    late_count = db.Column(db.Integer, default=0)
    early_leave_count = db.Column(db.Integer, default=0)
    annual_leave_used = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Attendance {self.id}: {self.employee_id} {self.year}-{self.month}>'
