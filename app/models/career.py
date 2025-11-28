"""
Career SQLAlchemy 모델

직원 경력 정보를 관리합니다.
"""
from app.database import db


class Career(db.Model):
    """경력 모델"""
    __tablename__ = 'careers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    company_name = db.Column(db.String(200), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    job_description = db.Column(db.Text, nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    resignation_reason = db.Column(db.String(500), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'company_name': self.company_name,
            'company': self.company_name,  # 템플릿: career.company
            'department': self.department,
            'position': self.position,
            'job_description': self.job_description,
            'duty': self.job_description,  # 템플릿: career.duty
            'start_date': self.start_date,
            'end_date': self.end_date,
            'resignation_reason': self.resignation_reason,
            'is_current': self.is_current,
            'salary': None,  # 템플릿: career.salary (모델에 없음)
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            company_name=data.get('companyName'),
            department=data.get('department'),
            position=data.get('position'),
            job_description=data.get('jobDescription'),
            start_date=data.get('startDate'),
            end_date=data.get('endDate'),
            resignation_reason=data.get('resignationReason'),
            is_current=data.get('isCurrent', False),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Career {self.id}: {self.company_name}>'
