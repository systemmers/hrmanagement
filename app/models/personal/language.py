"""
PersonalLanguage SQLAlchemy 모델

개인 어학 능력 정보를 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalLanguage(db.Model):
    """개인 어학 능력 정보"""
    __tablename__ = 'personal_languages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    language = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(50), nullable=True)  # 초급, 중급, 고급, 원어민
    test_name = db.Column(db.String(100), nullable=True)  # TOEIC, JLPT 등
    score = db.Column(db.String(50), nullable=True)
    test_date = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'language': self.language,
            'language_name': self.language,  # Employee 호환 alias
            'proficiency': self.proficiency,
            'level': self.proficiency,  # 템플릿 호환 필드
            'test_name': self.test_name,
            'exam_name': self.test_name,  # Employee 호환 alias
            'score': self.score,
            'test_date': self.test_date,
            'acquisition_date': self.test_date,  # Employee 호환 alias
            'acquired_date': self.test_date,  # 템플릿 호환 필드
            'notes': self.notes,
            'note': self.notes,  # Employee 호환 alias
        }

    def __repr__(self):
        return f'<PersonalLanguage {self.id}: {self.language}>'
