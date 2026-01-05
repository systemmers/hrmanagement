"""
Evaluation SQLAlchemy 모델

직원 인사평가 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Evaluation(DictSerializableMixin, db.Model):
    """인사평가 모델"""
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=True)
    q1_grade = db.Column(db.String(10), nullable=True)
    q2_grade = db.Column(db.String(10), nullable=True)
    q3_grade = db.Column(db.String(10), nullable=True)
    q4_grade = db.Column(db.String(10), nullable=True)
    overall_grade = db.Column(db.String(10), nullable=True)
    salary_negotiation = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Evaluation {self.id}: {self.employee_id}>'
