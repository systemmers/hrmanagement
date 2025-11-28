"""
Attendance SQLAlchemy 모델

직원 근태 정보를 관리합니다.
"""
from app.database import db


class Attendance(db.Model):
    """근태 모델"""
    __tablename__ = 'attendances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    date = db.Column(db.String(20), nullable=True, index=True)
    check_in = db.Column(db.String(20), nullable=True)
    check_out = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)
    work_hours = db.Column(db.Float, default=0.0)
    overtime_hours = db.Column(db.Float, default=0.0)
    late_minutes = db.Column(db.Integer, default=0)
    early_leave_minutes = db.Column(db.Integer, default=0)
    leave_type = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'date': self.date,
            'checkIn': self.check_in,
            'checkOut': self.check_out,
            'status': self.status,
            'workHours': self.work_hours,
            'overtimeHours': self.overtime_hours,
            'lateMinutes': self.late_minutes,
            'earlyLeaveMinutes': self.early_leave_minutes,
            'leaveType': self.leave_type,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            date=data.get('date'),
            check_in=data.get('checkIn'),
            check_out=data.get('checkOut'),
            status=data.get('status'),
            work_hours=data.get('workHours', 0.0),
            overtime_hours=data.get('overtimeHours', 0.0),
            late_minutes=data.get('lateMinutes', 0),
            early_leave_minutes=data.get('earlyLeaveMinutes', 0),
            leave_type=data.get('leaveType'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Attendance {self.id}: {self.employee_id} {self.date}>'
