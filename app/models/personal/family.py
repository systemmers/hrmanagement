"""
PersonalFamily SQLAlchemy 모델

개인 가족 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalFamily(db.Model):
    """개인 가족 정보"""
    __tablename__ = 'personal_families'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id', ondelete='CASCADE'), nullable=False)

    relation = db.Column(db.String(50), nullable=False)  # 부, 모, 배우자, 자녀 등
    name = db.Column(db.String(100), nullable=False)
    birth_date = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    education = db.Column(db.String(100), nullable=True)
    is_cohabitant = db.Column(db.Boolean, default=False)  # 동거 여부
    is_dependent = db.Column(db.Boolean, default=False)  # 부양가족 여부
    contact = db.Column(db.String(50), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'relation': self.relation,
            'name': self.name,
            'birth_date': self.birth_date,
            'occupation': self.occupation,
            'education': self.education,
            'is_cohabitant': self.is_cohabitant,
            'is_dependent': self.is_dependent,
            'contact': self.contact,
            'phone': self.contact,  # 템플릿 호환 필드
            'notes': self.notes,
            'note': self.notes,  # Employee 호환 alias
            'living_together': self.is_cohabitant,  # Employee 호환 alias
        }

    def __repr__(self):
        return f'<PersonalFamily {self.id}: {self.relation} - {self.name}>'
