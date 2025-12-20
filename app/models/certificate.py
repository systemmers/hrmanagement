"""
Certificate SQLAlchemy 모델

직원 자격증 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Certificate(DictSerializableMixin, db.Model):
    """자격증 모델"""
    __tablename__ = 'certificates'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'name': 'certificate_name',            # 템플릿: cert.name
        'issuer': 'issuing_organization',      # 템플릿: cert.issuer
        'acquired_date': 'acquisition_date',   # 템플릿: cert.acquired_date
        'notes': 'note',                       # Personal 호환
        'issue_date': 'acquisition_date',      # Personal 호환
    }

    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'profile_id': ['profileId'],
        'certificate_name': ['certificateName'],
        'issuing_organization': ['issuingOrganization'],
        'certificate_number': ['certificateNumber'],
        'acquisition_date': ['acquisitionDate'],
        'expiry_date': ['expiryDate'],
    }

    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    certificate_name = db.Column(db.String(200), nullable=True)
    issuing_organization = db.Column(db.String(200), nullable=True)
    certificate_number = db.Column(db.String(100), nullable=True)
    acquisition_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Certificate {self.id}: {self.certificate_name}>'
