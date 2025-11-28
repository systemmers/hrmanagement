"""
Insurance SQLAlchemy 모델

직원 보험 정보를 관리합니다. (1:1 관계)
"""
from app.database import db


class Insurance(db.Model):
    """보험 모델 (1:1)"""
    __tablename__ = 'insurances'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, unique=True, index=True)
    national_pension = db.Column(db.Boolean, default=True)
    health_insurance = db.Column(db.Boolean, default=True)
    employment_insurance = db.Column(db.Boolean, default=True)
    industrial_accident = db.Column(db.Boolean, default=True)
    national_pension_rate = db.Column(db.Float, default=4.5)
    health_insurance_rate = db.Column(db.Float, default=3.545)
    long_term_care_rate = db.Column(db.Float, default=0.9182)
    employment_insurance_rate = db.Column(db.Float, default=0.9)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'national_pension': self.national_pension,
            'health_insurance': self.health_insurance,
            'employment_insurance': self.employment_insurance,
            'industrial_accident': self.industrial_accident,
            'national_pension_rate': self.national_pension_rate,
            'health_insurance_rate': self.health_insurance_rate,
            'long_term_care_rate': self.long_term_care_rate,
            'employment_insurance_rate': self.employment_insurance_rate,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성 (snake_case 지원)"""
        return cls(
            employee_id=data.get('employee_id') or data.get('employeeId'),
            national_pension=data.get('national_pension', True) if 'national_pension' in data else data.get('nationalPension', True),
            health_insurance=data.get('health_insurance', True) if 'health_insurance' in data else data.get('healthInsurance', True),
            employment_insurance=data.get('employment_insurance', True) if 'employment_insurance' in data else data.get('employmentInsurance', True),
            industrial_accident=data.get('industrial_accident', True) if 'industrial_accident' in data else data.get('industrialAccident', True),
            national_pension_rate=data.get('national_pension_rate') or data.get('nationalPensionRate', 4.5),
            health_insurance_rate=data.get('health_insurance_rate') or data.get('healthInsuranceRate', 3.545),
            long_term_care_rate=data.get('long_term_care_rate') or data.get('longTermCareRate', 0.9182),
            employment_insurance_rate=data.get('employment_insurance_rate') or data.get('employmentInsuranceRate', 0.9),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Insurance {self.id}: {self.employee_id}>'
