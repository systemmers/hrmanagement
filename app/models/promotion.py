"""
Promotion SQLAlchemy 모델

직원 승진 정보를 관리합니다.
"""
from app.database import db


class Promotion(db.Model):
    """승진 모델"""
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    promotion_date = db.Column(db.String(20), nullable=True)
    previous_position = db.Column(db.String(100), nullable=True)
    new_position = db.Column(db.String(100), nullable=True)
    previous_department = db.Column(db.String(100), nullable=True)
    new_department = db.Column(db.String(100), nullable=True)
    promotion_type = db.Column(db.String(50), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'promotionDate': self.promotion_date,
            'previousPosition': self.previous_position,
            'newPosition': self.new_position,
            'previousDepartment': self.previous_department,
            'newDepartment': self.new_department,
            'promotionType': self.promotion_type,
            'reason': self.reason,
            'approvedBy': self.approved_by,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            promotion_date=data.get('promotionDate'),
            previous_position=data.get('previousPosition'),
            new_position=data.get('newPosition'),
            previous_department=data.get('previousDepartment'),
            new_department=data.get('newDepartment'),
            promotion_type=data.get('promotionType'),
            reason=data.get('reason'),
            approved_by=data.get('approvedBy'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Promotion {self.id}: {self.employee_id}>'
