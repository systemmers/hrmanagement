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
    year = db.Column(db.Integer, nullable=True)
    q1_grade = db.Column(db.String(10), nullable=True)
    q2_grade = db.Column(db.String(10), nullable=True)
    q3_grade = db.Column(db.String(10), nullable=True)
    q4_grade = db.Column(db.String(10), nullable=True)
    overall_grade = db.Column(db.String(10), nullable=True)
    salary_negotiation = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'q1_grade': self.q1_grade,
            'q2_grade': self.q2_grade,
            'q3_grade': self.q3_grade,
            'q4_grade': self.q4_grade,
            'overall_grade': self.overall_grade,
            'salary_negotiation': self.salary_negotiation,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            year=data.get('year'),
            q1_grade=data.get('q1_grade') or data.get('q1Grade'),
            q2_grade=data.get('q2_grade') or data.get('q2Grade'),
            q3_grade=data.get('q3_grade') or data.get('q3Grade'),
            q4_grade=data.get('q4_grade') or data.get('q4Grade'),
            overall_grade=data.get('overall_grade') or data.get('overallGrade'),
            salary_negotiation=data.get('salary_negotiation') or data.get('salaryNegotiation'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Evaluation {self.id}: {self.employee_id}>'
