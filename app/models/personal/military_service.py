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
    duty = db.Column(db.String(100), nullable=True)  # 보직
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'military_status': self.service_type,  # Employee 호환 alias
            'status': self.service_type,  # 템플릿 호환 필드
            'branch': self.branch,
            'rank': self.rank,
            'start_date': self.start_date,
            'enlistment_date': self.start_date,  # Employee 호환 alias
            'end_date': self.end_date,
            'discharge_date': self.end_date,  # Employee 호환 alias
            'discharge_type': self.discharge_type,
            'discharge_reason': self.discharge_type,  # Employee 호환 alias
            'specialty': self.specialty,
            'duty': self.duty,  # 보직
            'exemption_reason': self.notes,  # 템플릿 호환 필드 (notes를 면제사유로 사용)
            'notes': self.notes,
            'note': self.notes,  # Employee 호환 alias
        }

    def __repr__(self):
        return f'<PersonalMilitaryService {self.id}: {self.service_type}>'
