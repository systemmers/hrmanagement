"""
Award SQLAlchemy 모델

직원 수상/징계 정보를 관리합니다.
"""
from app.database import db


class Award(db.Model):
    """수상/징계 모델"""
    __tablename__ = 'awards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    award_type = db.Column(db.String(50), nullable=True)
    award_name = db.Column(db.String(200), nullable=True)
    award_date = db.Column(db.String(20), nullable=True)
    issuer = db.Column(db.String(200), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    prize = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'awardType': self.award_type,
            'awardName': self.award_name,
            'awardDate': self.award_date,
            'issuer': self.issuer,
            'reason': self.reason,
            'prize': self.prize,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            award_type=data.get('awardType'),
            award_name=data.get('awardName'),
            award_date=data.get('awardDate'),
            issuer=data.get('issuer'),
            reason=data.get('reason'),
            prize=data.get('prize'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Award {self.id}: {self.award_name}>'
