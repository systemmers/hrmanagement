"""
Education SQLAlchemy 모델

직원 학력 정보를 관리합니다.
"""
from app.database import db


class Education(db.Model):
    """학력 모델"""
    __tablename__ = 'educations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=False, index=True)
    school_type = db.Column(db.String(50), nullable=True)
    school_name = db.Column(db.String(200), nullable=True)
    major = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(50), nullable=True)
    admission_date = db.Column(db.String(20), nullable=True)
    graduation_date = db.Column(db.String(20), nullable=True)
    graduation_status = db.Column(db.String(50), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 camelCase 딕셔너리 반환"""
        return {
            'id': self.id,
            'employeeId': self.employee_id,
            'schoolType': self.school_type,
            'schoolName': self.school_name,
            'major': self.major,
            'degree': self.degree,
            'admissionDate': self.admission_date,
            'graduationDate': self.graduation_date,
            'graduationStatus': self.graduation_status,
            'location': self.location,
            'note': self.note,
        }

    @classmethod
    def from_dict(cls, data):
        """camelCase 딕셔너리에서 모델 생성"""
        return cls(
            employee_id=data.get('employeeId'),
            school_type=data.get('schoolType'),
            school_name=data.get('schoolName'),
            major=data.get('major'),
            degree=data.get('degree'),
            admission_date=data.get('admissionDate'),
            graduation_date=data.get('graduationDate'),
            graduation_status=data.get('graduationStatus'),
            location=data.get('location'),
            note=data.get('note'),
        )

    def __repr__(self):
        return f'<Education {self.id}: {self.school_name}>'
