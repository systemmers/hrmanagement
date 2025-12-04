"""
PersonalMilitaryService SQLAlchemy 모델

개인 병역 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalMilitaryService(db.Model):
    """개인 병역 정보"""
    __tablename__ = 'personal_military_services'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), unique=True, nullable=False)

    service_type = db.Column(db.String(50), nullable=True)  # 현역, 보충역, 면제 등
    branch = db.Column(db.String(100), nullable=True)  # 육군, 해군, 공군 등
    rank = db.Column(db.String(50), nullable=True)  # 최종 계급
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    discharge_type = db.Column(db.String(50), nullable=True)  # 만기전역, 의가사 등
    specialty = db.Column(db.String(100), nullable=True)  # 병과/특기
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'branch': self.branch,
            'rank': self.rank,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'discharge_type': self.discharge_type,
            'specialty': self.specialty,
            'notes': self.notes,
        }

    def __repr__(self):
        return f'<PersonalMilitaryService {self.id}: {self.service_type}>'
