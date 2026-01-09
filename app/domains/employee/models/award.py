"""
Award SQLAlchemy 모델

직원 수상 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class Award(DictSerializableMixin, db.Model):
    """수상 모델"""
    __tablename__ = 'awards'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'notes': 'note',                       # Personal 호환
    }


    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    award_date = db.Column(db.String(20), nullable=True)
    award_name = db.Column(db.String(200), nullable=True)
    institution = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<Award {self.id}: {self.award_name}>'
