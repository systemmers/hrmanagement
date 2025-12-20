"""
PersonalProjectParticipation SQLAlchemy 모델

개인 프로필의 프로젝트 참여이력을 관리합니다.
"""
from datetime import datetime
from app.database import db


class PersonalProjectParticipation(db.Model):
    """개인 프로젝트 참여이력"""
    __tablename__ = 'personal_project_participations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    project_name = db.Column(db.String(200), nullable=False)  # 사업/프로젝트명
    start_date = db.Column(db.String(20), nullable=True)  # 참여 시작일
    end_date = db.Column(db.String(20), nullable=True)  # 참여 종료일
    duration = db.Column(db.String(50), nullable=True)  # 기간
    role = db.Column(db.String(100), nullable=True)  # 역할/직책
    duty = db.Column(db.String(200), nullable=True)  # 담당업무
    client = db.Column(db.String(200), nullable=True)  # 발주처/고객사
    note = db.Column(db.Text, nullable=True)  # 비고

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'profile_id': self.profile_id,
            'project_name': self.project_name,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'duration': self.duration,
            'role': self.role,
            'duty': self.duty,
            'client': self.client,
            'note': self.note,
        }

    def __repr__(self):
        return f'<PersonalProjectParticipation {self.id}: {self.project_name}>'
