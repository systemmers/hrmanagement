"""
Training SQLAlchemy 모델

직원 교육 이력 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Training(DictSerializableMixin, db.Model):
    """교육 이력 모델"""
    __tablename__ = 'trainings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    training_date = db.Column(db.String(20), nullable=True)
    training_name = db.Column(db.String(200), nullable=True)
    institution = db.Column(db.String(200), nullable=True)
    hours = db.Column(db.Integer, default=0)
    completion_status = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Training {self.id}: {self.training_name}>'
