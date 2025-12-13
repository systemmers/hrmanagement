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
    gpa = db.Column(db.String(20), nullable=True)
    location = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def to_dict(self):
        """템플릿 호환성을 위한 딕셔너리 반환 (snake_case)"""
        # graduation_date에서 연도 추출
        graduation_year = None
        if self.graduation_date:
            graduation_year = self.graduation_date[:4] if len(self.graduation_date) >= 4 else self.graduation_date
        return {
            'id': self.id,
            'employee_id': self.employee_id,
            'school_type': self.school_type,
            'school_name': self.school_name,
            'school': self.school_name,  # 템플릿: edu.school
            'major': self.major,
            'degree': self.degree,
            'admission_date': self.admission_date,
            'graduation_date': self.graduation_date,
            'graduation_year': graduation_year,  # 템플릿: edu.graduation_year
            'graduation_status': self.graduation_status,
            'location': self.location,
            'gpa': self.gpa,
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
