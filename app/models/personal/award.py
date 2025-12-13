"""
PersonalAward SQLAlchemy 모델

개인 수상 내역 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalAward(db.Model):
    """개인 수상 내역"""
    __tablename__ = 'personal_awards'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    award_name = db.Column(db.String(200), nullable=False)  # 수상명
    award_date = db.Column(db.String(20), nullable=True)  # 수상일
    institution = db.Column(db.String(200), nullable=True)  # 수여기관
    description = db.Column(db.Text, nullable=True)  # 수상 내용
    notes = db.Column(db.Text, nullable=True)  # 비고

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'award_name': self.award_name,
            'award_date': self.award_date,
            'institution': self.institution,
            'description': self.description,
            'notes': self.notes,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<PersonalAward {self.id}: {self.award_name}>'
