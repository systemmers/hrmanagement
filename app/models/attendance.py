"""
Attendance SQLAlchemy 모델

직원 근태 정보를 관리합니다.
"""
from app.database import db


class Attendance(db.Model):
    """근태 모델 (월별 집계)"""
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    year = db.Column(db.Integer, nullable=True)
    month = db.Column(db.Integer, nullable=True)
    work_days = db.Column(db.Integer, default=0)
    absent_days = db.Column(db.Integer, default=0)
    late_count = db.Column(db.Integer, default=0)
    early_leave_count = db.Column(db.Integer, default=0)
    annual_leave_used = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'year': self.year,
            'month': self.month,
            'workDays': self.work_days,
            'absentDays': self.absent_days,
            'lateCount': self.late_count,
            'earlyLeaveCount': self.early_leave_count,
            'annualLeaveUsed': self.annual_leave_used,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            year=data.get('year'),
            month=data.get('month'),
            work_days=data.get('work_days') or data.get('workDays', 0),
            absent_days=data.get('absent_days') or data.get('absentDays', 0),
            late_count=data.get('late_count') or data.get('lateCount', 0),
            early_leave_count=data.get('early_leave_count') or data.get('earlyLeaveCount', 0),
            annual_leave_used=data.get('annual_leave_used') or data.get('annualLeaveUsed', 0),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Attendance {self.id}: {self.employee_id} {self.year}-{self.month}>'
