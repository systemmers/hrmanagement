"""
MilitaryService SQLAlchemy 모델

직원 병역 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class MilitaryService(db.Model):
    """병역 모델 (1:1)"""
    __tablename__ = 'military_services'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    military_status = db.Column(db.String(50), nullable=True)
    service_type = db.Column(db.String(100), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    rank = db.Column(db.String(50), nullable=True)
    enlistment_date = db.Column(db.String(20), nullable=True)
    discharge_date = db.Column(db.String(20), nullable=True)
    discharge_reason = db.Column(db.String(200), nullable=True)
    exemption_reason = db.Column(db.String(500), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'status': self.military_status,  # 템플릿: military.status
            'military_status': self.military_status,
            'service_type': self.service_type,
            'branch': self.branch,
            'rank': self.rank,
            'start_date': self.enlistment_date,  # 템플릿: military.start_date
            'end_date': self.discharge_date,  # 템플릿: military.end_date
            'enlistment_date': self.enlistment_date,
            'discharge_date': self.discharge_date,
            'discharge_reason': self.discharge_reason,
            'exemption_reason': self.exemption_reason,
            'duty': self.service_type,  # 템플릿: military.duty (service_type 매핑)
            'specialty': None,  # 템플릿: military.specialty
            'discharge_type': self.discharge_reason,  # Personal 호환 alias
            'note': self.note,
            'notes': self.note,  # Personal 호환 alias
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            military_status=data.get('militaryStatus'),
            service_type=data.get('serviceType'),
            branch=data.get('branch'),
            rank=data.get('rank'),
            enlistment_date=data.get('enlistmentDate'),
            discharge_date=data.get('dischargeDate'),
            discharge_reason=data.get('dischargeReason'),
            exemption_reason=data.get('exemptionReason'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<MilitaryService {self.id}: {self.employee_id}>'
