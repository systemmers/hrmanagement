"""
Insurance SQLAlchemy 모델

직원 보험 정보를 관리합니다. (1:1 관계)
Phase 8: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Insurance(DictSerializableMixin, db.Model):
    """보험 모델 (1:1)"""
    __tablename__ = 'insurances'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'national_pension': ['nationalPension'],
        'health_insurance': ['healthInsurance'],
        'employment_insurance': ['employmentInsurance'],
        'industrial_accident': ['industrialAccident'],
        'national_pension_rate': ['nationalPensionRate'],
        'health_insurance_rate': ['healthInsuranceRate'],
        'long_term_care_rate': ['longTermCareRate'],
        'employment_insurance_rate': ['employmentInsuranceRate'],
    }

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

    def __repr__(self):
        return f'<Insurance {self.id}: {self.employee_id}>'
