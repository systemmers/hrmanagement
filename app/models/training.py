"""
Training SQLAlchemy 모델

직원 교육 이력 정보를 관리합니다.
"""
from app.database import db


class Training(db.Model):
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

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'trainingDate': self.training_date,
            'trainingName': self.training_name,
            'institution': self.institution,
            'hours': self.hours,
            'completionStatus': self.completion_status,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            training_date=data.get('training_date') or data.get('trainingDate'),
            training_name=data.get('training_name') or data.get('trainingName'),
            institution=data.get('institution'),
            hours=data.get('hours', 0),
            completion_status=data.get('completion_status') or data.get('completionStatus'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Training {self.id}: {self.training_name}>'
