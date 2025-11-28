"""
Project SQLAlchemy 모델

직원 프로젝트 참여 정보를 관리합니다.
"""
from app.database import db


class Project(db.Model):
    """프로젝트 모델"""
    __tablename__ = 'projects'

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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'project_name': self.project_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'duration': self.duration,
            'role': self.role,
            'duty': self.duty,
            'client': self.client,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            project_name=data.get('project_name') or data.get('projectName'),
            start_date=data.get('start_date') or data.get('startDate'),
            end_date=data.get('end_date') or data.get('endDate'),
            duration=data.get('duration'),
            role=data.get('role'),
            duty=data.get('duty'),
            client=data.get('client'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Project {self.id}: {self.project_name}>'
