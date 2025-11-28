"""
Award SQLAlchemy 모델

직원 수상 정보를 관리합니다.
"""
from app.database import db


class Award(db.Model):
    """수상 모델"""
    __tablename__ = 'awards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    award_date = db.Column(db.String(20), nullable=True)
    award_name = db.Column(db.String(200), nullable=True)
    institution = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'awardDate': self.award_date,
            'awardName': self.award_name,
            'institution': self.institution,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            award_date=data.get('award_date') or data.get('awardDate'),
            award_name=data.get('award_name') or data.get('awardName'),
            institution=data.get('institution'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Award {self.id}: {self.award_name}>'
