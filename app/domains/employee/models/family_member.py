"""
FamilyMember SQLAlchemy 모델

직원 가족 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class FamilyMember(DictSerializableMixin, db.Model):
    """가족 모델"""
    __tablename__ = 'family_members'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'phone': 'contact',                    # 템플릿: family.phone
        'living_together': 'is_cohabitant',    # 템플릿: family.living_together
        'notes': 'note',                       # Personal 호환
    }

    __dict_computed__ = {
        'education': lambda self: None,        # Personal 호환 필드 (Employee에는 없음)
    }


    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    relation = db.Column(db.String(50), nullable=True)
    name = db.Column(db.String(100), nullable=True)
    birth_date = db.Column(db.String(20), nullable=True)
    occupation = db.Column(db.String(100), nullable=True)
    contact = db.Column(db.String(50), nullable=True)
    is_cohabitant = db.Column(db.Boolean, default=False)
    is_dependent = db.Column(db.Boolean, default=False)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<FamilyMember {self.id}: {self.name}>'
