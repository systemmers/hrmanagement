"""
Education SQLAlchemy 모델

직원 학력 정보를 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
- to_dict/from_dict 자동화
- 선언적 alias 정의
"""
from app.database import db
from app.models.mixins import DictSerializableMixin


class Education(DictSerializableMixin, db.Model):
    """학력 모델

    DictSerializableMixin 적용:
    - to_dict(): 자동 직렬화 + alias + computed
    - from_dict(): 자동 역직렬화 (camelCase/snake_case)
    """
    __tablename__ = 'educations'

    # ====================================
    # Mixin 설정 (선언적 정의)
    # ====================================

    # Alias: 템플릿 호환성을 위한 추가 키
    __dict_aliases__ = {
        'school': 'school_name',           # 템플릿: edu.school
        'status': 'graduation_status',     # Personal 호환
        'notes': 'note',                   # Personal 호환
    }

    # Computed: 런타임 계산 필드
    __dict_computed__ = {
        'graduation_year': lambda self: (
            self.graduation_date[:4]
            if self.graduation_date and len(self.graduation_date) >= 4
            else None
        ),
    }

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'employee_id': ['employeeId'],
        'profile_id': ['profileId'],
        'school_type': ['schoolType'],
        'school_name': ['schoolName'],
        'admission_date': ['admissionDate'],
        'graduation_date': ['graduationDate'],
        'graduation_status': ['graduationStatus'],
    }

    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
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

    # to_dict, from_dict는 DictSerializableMixin에서 자동 제공

    def __repr__(self):
        return f'<Education {self.id}: {self.school_name}>'
