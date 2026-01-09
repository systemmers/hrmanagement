"""
ProjectParticipation SQLAlchemy 모델

과거 경력에서 참여했던 프로젝트/사업 참여이력을 관리합니다.

Phase 8 리팩토링: DictSerializableMixin 적용
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class ProjectParticipation(DictSerializableMixin, db.Model):
    """프로젝트 참여이력 모델"""
    __tablename__ = 'project_participations'

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
    project_name = db.Column(db.String(200), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    duration = db.Column(db.String(50), nullable=True)
    role = db.Column(db.String(100), nullable=True)
    duty = db.Column(db.String(200), nullable=True)
    client = db.Column(db.String(200), nullable=True)
    note = db.Column(db.Text, nullable=True)

    def __repr__(self):
        return f'<ProjectParticipation {self.id}: {self.project_name}>'
