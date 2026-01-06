"""
MilitaryService SQLAlchemy 모델

직원 병역 정보를 관리합니다. (1:1 관계)

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from .mixins import DictSerializableMixin


class MilitaryService(DictSerializableMixin, db.Model):
    """병역 모델 (1:1)"""
    __tablename__ = 'military_services'

    # ====================================
    # Mixin 설정
    # ====================================

    __dict_aliases__ = {
        'status': 'military_status',           # 템플릿: military.status
        'start_date': 'enlistment_date',       # 템플릿: military.start_date
        'end_date': 'discharge_date',          # 템플릿: military.end_date
        'duty': 'service_type',                # 템플릿: military.duty
        'discharge_type': 'discharge_reason',  # Personal 호환 alias
        'notes': 'note',                       # Personal 호환 alias
    }

    # specialty 컬럼 추가됨 (2025-12-27) - computed 불필요


    # ====================================
    # 컬럼 정의
    # ====================================

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('profiles.id', ondelete='CASCADE'), nullable=True, index=True)
    military_status = db.Column(db.String(50), nullable=True)
    service_type = db.Column(db.String(100), nullable=True)
    branch = db.Column(db.String(100), nullable=True)
    rank = db.Column(db.String(50), nullable=True)
    enlistment_date = db.Column(db.String(20), nullable=True)
    discharge_date = db.Column(db.String(20), nullable=True)
    discharge_reason = db.Column(db.String(200), nullable=True)
    exemption_reason = db.Column(db.String(500), nullable=True)
    specialty = db.Column(db.String(100), nullable=True)  # 병과 (보병, 통신 등)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<MilitaryService {self.id}: {self.employee_id}>'
