"""
Promotion SQLAlchemy 모델

직원 발령/인사이동 정보를 관리합니다.
"""
from app.database import db


class Promotion(db.Model):
    """발령/인사이동 모델"""
    __tablename__ = 'promotions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    effective_date = db.Column(db.String(20), nullable=True)
    promotion_type = db.Column(db.String(50), nullable=True)
    from_department = db.Column(db.String(100), nullable=True)
    to_department = db.Column(db.String(100), nullable=True)
    from_position = db.Column(db.String(100), nullable=True)
    to_position = db.Column(db.String(100), nullable=True)
    job_role = db.Column(db.String(100), nullable=True)
    reason = db.Column(db.Text, nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'effective_date': self.effective_date,
            'promotion_type': self.promotion_type,
            'from_department': self.from_department,
            'to_department': self.to_department,
            'from_position': self.from_position,
            'to_position': self.to_position,
            'job_role': self.job_role,
            'reason': self.reason,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            effective_date=data.get('effective_date') or data.get('effectiveDate'),
            promotion_type=data.get('promotion_type') or data.get('promotionType'),
            from_department=data.get('from_department') or data.get('fromDepartment'),
            to_department=data.get('to_department') or data.get('toDepartment'),
            from_position=data.get('from_position') or data.get('fromPosition'),
            to_position=data.get('to_position') or data.get('toPosition'),
            job_role=data.get('job_role') or data.get('jobRole'),
            reason=data.get('reason'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Promotion {self.id}: {self.employee_id}>'
