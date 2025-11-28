"""
Contract SQLAlchemy 모델

직원 계약 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class Contract(db.Model):
    """계약 모델 (1:1)"""
    __tablename__ = 'contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    contract_type = db.Column(db.String(50), nullable=True)
    contract_start = db.Column(db.String(20), nullable=True)
    contract_end = db.Column(db.String(20), nullable=True)
    probation_period = db.Column(db.Integer, default=0)
    probation_end = db.Column(db.String(20), nullable=True)
    working_hours = db.Column(db.String(100), nullable=True)
    work_location = db.Column(db.String(200), nullable=True)
    job_duties = db.Column(db.Text, nullable=True)
    special_conditions = db.Column(db.Text, nullable=True)
    renewal_count = db.Column(db.Integer, default=0)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'contractType': self.contract_type,
            'contractStart': self.contract_start,
            'contractEnd': self.contract_end,
            'probationPeriod': self.probation_period,
            'probationEnd': self.probation_end,
            'workingHours': self.working_hours,
            'workLocation': self.work_location,
            'jobDuties': self.job_duties,
            'specialConditions': self.special_conditions,
            'renewalCount': self.renewal_count,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            contract_type=data.get('contractType'),
            contract_start=data.get('contractStart'),
            contract_end=data.get('contractEnd'),
            probation_period=data.get('probationPeriod', 0),
            probation_end=data.get('probationEnd'),
            working_hours=data.get('workingHours'),
            work_location=data.get('workLocation'),
            job_duties=data.get('jobDuties'),
            special_conditions=data.get('specialConditions'),
            renewal_count=data.get('renewalCount', 0),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Contract {self.id}: {self.employee_id}>'
