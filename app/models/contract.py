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
    contract_date = db.Column(db.String(20), nullable=True)
    contract_type = db.Column(db.String(50), nullable=True)
    contract_period = db.Column(db.String(50), nullable=True)
    employee_type = db.Column(db.String(50), nullable=True)
    work_type = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'contractDate': self.contract_date,
            'contractType': self.contract_type,
            'contractPeriod': self.contract_period,
            'employeeType': self.employee_type,
            'workType': self.work_type,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성 (snake_case 지원)"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            contract_date=data.get('contract_date') or data.get('contractDate'),
            contract_type=data.get('contract_type') or data.get('contractType'),
            contract_period=data.get('contract_period') or data.get('contractPeriod'),
            employee_type=data.get('employee_type') or data.get('employeeType'),
            work_type=data.get('work_type') or data.get('workType'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Contract {self.id}: {self.employee_id}>'
