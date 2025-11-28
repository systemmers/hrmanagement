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
    project_code = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    client = db.Column(db.String(200), nullable=True)
    budget = db.Column(db.Integer, default=0)
    description = db.Column(db.Text, nullable=True)
    achievements = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'projectName': self.project_name,
            'projectCode': self.project_code,
            'role': self.role,
            'startDate': self.start_date,
            'endDate': self.end_date,
            'status': self.status,
            'client': self.client,
            'budget': self.budget,
            'description': self.description,
            'achievements': self.achievements,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            project_name=data.get('projectName'),
            project_code=data.get('projectCode'),
            role=data.get('role'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            status=data.get('status'),
            client=data.get('client'),
            budget=data.get('budget', 0),
            description=data.get('description'),
            achievements=data.get('achievements'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Project {self.id}: {self.project_name}>'
