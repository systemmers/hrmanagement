"""
Training SQLAlchemy 모델

직원 교육 훈련 정보를 관리합니다.
"""
from app.database import db


class Training(db.Model):
    """교육 훈련 모델"""
    __tablename__ = 'trainings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    training_name = db.Column(db.String(200), nullable=True)
    training_type = db.Column(db.String(50), nullable=True)
    provider = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    duration_hours = db.Column(db.Integer, default=0)
    location = db.Column(db.String(200), nullable=True)
    cost = db.Column(db.Integer, default=0)
    status = db.Column(db.String(50), nullable=True)
    certificate_issued = db.Column(db.Boolean, default=False)
    score = db.Column(db.Float, default=0.0)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'trainingName': self.training_name,
            'trainingType': self.training_type,
            'provider': self.provider,
            'startDate': self.start_date,
            'endDate': self.end_date,
            'durationHours': self.duration_hours,
            'location': self.location,
            'cost': self.cost,
            'status': self.status,
            'certificateIssued': self.certificate_issued,
            'score': self.score,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            training_name=data.get('trainingName'),
            training_type=data.get('trainingType'),
            provider=data.get('provider'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            duration_hours=data.get('durationHours', 0),
            location=data.get('location'),
            cost=data.get('cost', 0),
            status=data.get('status'),
            certificate_issued=data.get('certificateIssued', False),
            score=data.get('score', 0.0),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Training {self.id}: {self.training_name}>'
