"""
SalaryHistory SQLAlchemy 모델

직원 급여 변경 이력을 관리합니다.
"""
from app.database import db


class SalaryHistory(db.Model):
    """급여 이력 모델"""
    __tablename__ = 'salary_histories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    change_date = db.Column(db.String(20), nullable=True)
    change_type = db.Column(db.String(50), nullable=True)
    previous_salary = db.Column(db.Integer, default=0)
    new_salary = db.Column(db.Integer, default=0)
    change_amount = db.Column(db.Integer, default=0)
    change_rate = db.Column(db.Float, default=0.0)
    reason = db.Column(db.Text, nullable=True)
    approved_by = db.Column(db.String(100), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'changeDate': self.change_date,
            'changeType': self.change_type,
            'previousSalary': self.previous_salary,
            'newSalary': self.new_salary,
            'changeAmount': self.change_amount,
            'changeRate': self.change_rate,
            'reason': self.reason,
            'approvedBy': self.approved_by,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            change_date=data.get('changeDate'),
            change_type=data.get('changeType'),
            previous_salary=data.get('previousSalary', 0),
            new_salary=data.get('newSalary', 0),
            change_amount=data.get('changeAmount', 0),
            change_rate=data.get('changeRate', 0.0),
            reason=data.get('reason'),
            approved_by=data.get('approvedBy'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<SalaryHistory {self.id}: {self.employee_id}>'
