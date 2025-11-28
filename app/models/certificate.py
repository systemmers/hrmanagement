"""
Certificate SQLAlchemy 모델

직원 자격증 정보를 관리합니다.
"""
from app.database import db


class Certificate(db.Model):
    """자격증 모델"""
    __tablename__ = 'certificates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    certificate_name = db.Column(db.String(200), nullable=True)
    issuing_organization = db.Column(db.String(200), nullable=True)
    certificate_number = db.Column(db.String(100), nullable=True)
    acquisition_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    grade = db.Column(db.String(50), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'certificateName': self.certificate_name,
            'issuingOrganization': self.issuing_organization,
            'certificateNumber': self.certificate_number,
            'acquisitionDate': self.acquisition_date,
            'expiryDate': self.expiry_date,
            'grade': self.grade,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            certificate_name=data.get('certificateName'),
            issuing_organization=data.get('issuingOrganization'),
            certificate_number=data.get('certificateNumber'),
            acquisition_date=data.get('acquisitionDate'),
            expiry_date=data.get('expiryDate'),
            grade=data.get('grade'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Certificate {self.id}: {self.certificate_name}>'
