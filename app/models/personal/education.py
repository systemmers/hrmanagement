"""
PersonalEducation SQLAlchemy 모델

개인 학력 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalEducation(db.Model):
    """개인 학력 정보"""
    __tablename__ = 'personal_educations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    school_type = db.Column(db.String(50), nullable=True)  # 고등학교, 대학교, 대학원 등
    school_name = db.Column(db.String(200), nullable=False)
    major = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(50), nullable=True)  # 학사, 석사, 박사 등
    admission_date = db.Column(db.String(20), nullable=True)
    graduation_date = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)  # 졸업, 재학, 중퇴 등
    gpa = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'school_type': self.school_type,
            'school_name': self.school_name,
            'major': self.major,
            'degree': self.degree,
            'admission_date': self.admission_date,
            'graduation_date': self.graduation_date,
            'status': self.status,
            'gpa': self.gpa,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<PersonalEducation {self.id}: {self.school_name}>'
