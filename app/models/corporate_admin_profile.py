"""
CorporateAdminProfile SQLAlchemy 모델

법인 관리자의 프로필 정보를 관리하는 모델입니다.
법인 관리자(account_type='corporate', employee_id=None)를 위한 경량 프로필 시스템을 제공합니다.
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from datetime import datetime
from app.database import db
from app.models.mixins import DictSerializableMixin


class CorporateAdminProfile(DictSerializableMixin, db.Model):
    """법인 관리자 프로필 모델"""
    __tablename__ = 'corporate_admin_profiles'

    # 기본 키
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 연결 정보
    user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        unique=True,
        index=True
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False,
        index=True
    )

    # 기본 정보
    name = db.Column(db.String(100), nullable=False)
    english_name = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(50), nullable=True)  # 직책 (대표이사, CFO 등)

    # 연락처 정보
    mobile_phone = db.Column(db.String(20), nullable=True)
    office_phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)

    # 프로필 사진
    photo = db.Column(db.String(300), nullable=True)

    # 추가 정보
    department = db.Column(db.String(100), nullable=True)  # 소속 부서
    bio = db.Column(db.Text, nullable=True)  # 간략한 소개

    # 메타 정보
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    user = db.relationship(
        'User',
        backref=db.backref('admin_profile', uselist=False, lazy=True)
    )
    company = db.relationship(
        'Company',
        backref=db.backref('admin_profiles', lazy='dynamic')
    )

    def __repr__(self):
        return f'<CorporateAdminProfile {self.name} - Company {self.company_id}>'
