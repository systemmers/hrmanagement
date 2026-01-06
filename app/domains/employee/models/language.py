"""
Language SQLAlchemy 모델

직원 어학 능력 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from .mixins import DictSerializableMixin


class Language(DictSerializableMixin, db.Model):
    """어학 모델"""
    __tablename__ = 'languages'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'language': 'language_name',           # Personal 호환
        'test_name': 'exam_name',              # Personal 호환
        'proficiency': 'level',                # Personal 호환
        'test_date': 'acquisition_date',       # Personal 호환
        'acquired_date': 'acquisition_date',   # 템플릿 호환
        'notes': 'note',                       # Personal 호환
    }


    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    language_name = db.Column(db.String(100), nullable=True)
    exam_name = db.Column(db.String(100), nullable=True)
    score = db.Column(db.String(50), nullable=True)
    level = db.Column(db.String(50), nullable=True)
    acquisition_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Language {self.id}: {self.language_name}>'
