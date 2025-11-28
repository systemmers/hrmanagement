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
    national_pension_number = db.Column(db.String(50), nullable=True)
    national_pension_start = db.Column(db.String(20), nullable=True)
    health_insurance_number = db.Column(db.String(50), nullable=True)
    health_insurance_start = db.Column(db.String(20), nullable=True)
    employment_insurance_number = db.Column(db.String(50), nullable=True)
    employment_insurance_start = db.Column(db.String(20), nullable=True)
    industrial_insurance_number = db.Column(db.String(50), nullable=True)
    industrial_insurance_start = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'nationalPensionNumber': self.national_pension_number,
            'nationalPensionStart': self.national_pension_start,
            'healthInsuranceNumber': self.health_insurance_number,
            'healthInsuranceStart': self.health_insurance_start,
            'employmentInsuranceNumber': self.employment_insurance_number,
            'employmentInsuranceStart': self.employment_insurance_start,
            'industrialInsuranceNumber': self.industrial_insurance_number,
            'industrialInsuranceStart': self.industrial_insurance_start,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            national_pension_number=data.get('nationalPensionNumber'),
            national_pension_start=data.get('nationalPensionStart'),
            health_insurance_number=data.get('healthInsuranceNumber'),
            health_insurance_start=data.get('healthInsuranceStart'),
            employment_insurance_number=data.get('employmentInsuranceNumber'),
            employment_insurance_start=data.get('employmentInsuranceStart'),
            industrial_insurance_number=data.get('industrialInsuranceNumber'),
            industrial_insurance_start=data.get('industrialInsuranceStart'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Insurance {self.id}: {self.employee_id}>'
