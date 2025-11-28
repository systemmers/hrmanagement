"""
Benefit SQLAlchemy 모델

직원 복리후생 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class Benefit(db.Model):
    """복리후생 모델 (1:1)"""
    __tablename__ = 'benefits'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    year = db.Column(db.Integer, nullable=True)
    annual_leave_granted = db.Column(db.Integer, default=0)
    annual_leave_used = db.Column(db.Integer, default=0)
    annual_leave_remaining = db.Column(db.Integer, default=0)
    severance_type = db.Column(db.String(50), nullable=True)
    severance_method = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'year': self.year,
            'annual_leave_granted': self.annual_leave_granted,
            'annual_leave_used': self.annual_leave_used,
            'annual_leave_remaining': self.annual_leave_remaining,
            'severance_type': self.severance_type,
            'severance_method': self.severance_method,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성 (snake_case 지원)"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            year=data.get('year'),
            annual_leave_granted=data.get('annual_leave_granted') or data.get('annualLeaveGranted', 0),
            annual_leave_used=data.get('annual_leave_used') or data.get('annualLeaveUsed', 0),
            annual_leave_remaining=data.get('annual_leave_remaining') or data.get('annualLeaveRemaining', 0),
            severance_type=data.get('severance_type') or data.get('severanceType'),
            severance_method=data.get('severance_method') or data.get('severanceMethod'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Benefit {self.id}: {self.employee_id}>'
