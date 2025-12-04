"""
PersonalCareer SQLAlchemy 모델

개인 경력 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalCareer(db.Model):
    """개인 경력 정보"""
    __tablename__ = 'personal_careers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    company_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    responsibilities = db.Column(db.Text, nullable=True)
    achievements = db.Column(db.Text, nullable=True)
    reason_for_leaving = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'department': self.department,
            'position': self.position,
            'job_title': self.job_title,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_current': self.is_current,
            'responsibilities': self.responsibilities,
            'achievements': self.achievements,
            'reason_for_leaving': self.reason_for_leaving,
        }

    def __repr__(self):
        return f'<PersonalCareer {self.id}: {self.company_name}>'
