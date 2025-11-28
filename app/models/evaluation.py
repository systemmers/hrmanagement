"""
Evaluation SQLAlchemy 모델

직원 인사평가 정보를 관리합니다.
"""
from app.database import db


class Evaluation(db.Model):
    """인사평가 모델"""
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    evaluation_period = db.Column(db.String(50), nullable=True)
    evaluation_date = db.Column(db.String(20), nullable=True)
    evaluator = db.Column(db.String(100), nullable=True)
    performance_score = db.Column(db.Float, default=0.0)
    competency_score = db.Column(db.Float, default=0.0)
    overall_score = db.Column(db.Float, default=0.0)
    grade = db.Column(db.String(10), nullable=True)
    strengths = db.Column(db.Text, nullable=True)
    improvements = db.Column(db.Text, nullable=True)
    goals = db.Column(db.Text, nullable=True)
    feedback = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'evaluationPeriod': self.evaluation_period,
            'evaluationDate': self.evaluation_date,
            'evaluator': self.evaluator,
            'performanceScore': self.performance_score,
            'competencyScore': self.competency_score,
            'overallScore': self.overall_score,
            'grade': self.grade,
            'strengths': self.strengths,
            'improvements': self.improvements,
            'goals': self.goals,
            'feedback': self.feedback,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            evaluation_period=data.get('evaluationPeriod'),
            evaluation_date=data.get('evaluationDate'),
            evaluator=data.get('evaluator'),
            performance_score=data.get('performanceScore', 0.0),
            competency_score=data.get('competencyScore', 0.0),
            overall_score=data.get('overallScore', 0.0),
            grade=data.get('grade'),
            strengths=data.get('strengths'),
            improvements=data.get('improvements'),
            goals=data.get('goals'),
            feedback=data.get('feedback'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Evaluation {self.id}: {self.employee_id}>'
