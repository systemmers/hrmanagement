"""
PersonalCertificate SQLAlchemy 모델

개인 자격증 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalCertificate(db.Model):
    """개인 자격증 정보"""
    __tablename__ = 'personal_certificates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(200), nullable=True)
    issue_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    certificate_number = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(50), nullable=True)  # 등급/급수
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'issuing_organization': self.issuing_organization,
            'issuer': self.issuing_organization,  # 템플릿 호환 필드
            'issue_date': self.issue_date,
            'acquired_date': self.issue_date,  # 템플릿 호환 필드
            'acquisition_date': self.issue_date,  # 템플릿 호환 필드
            'expiry_date': self.expiry_date,
            'certificate_number': self.certificate_number,
            'grade': self.grade,
            'notes': self.notes,
            'note': self.notes,  # Employee 호환 alias
            'certificate_name': self.name,  # Employee 호환 alias
        }

    def __repr__(self):
        return f'<PersonalCertificate {self.id}: {self.name}>'
