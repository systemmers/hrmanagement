"""
Project SQLAlchemy 모델

직원 프로젝트 참여 정보를 관리합니다.
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Project(DictSerializableMixin, db.Model):
    """프로젝트 모델"""
    __tablename__ = 'projects'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'project_name': ['projectName'],
        'start_date': ['startDate'],
        'end_date': ['endDate'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    project_name = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    duty = db.Column(db.String(200), nullable=True)
    client = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Project {self.id}: {self.project_name}>'
