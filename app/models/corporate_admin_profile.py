"""
CorporateAdminProfile SQLAlchemy 모델

법인 관리자의 프로필 정보를 관리하는 모델입니다.
법인 관리자(account_type='corporate', employee_id=None)를 위한 경량 프로필 시스템을 제공합니다.
"""
from datetime import datetime
from app.database import db


class CorporateAdminProfile(db.Model):
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

    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'company_id': self.company_id,
            'name': self.name,
            'english_name': self.english_name,
            'position': self.position,
            'mobile_phone': self.mobile_phone,
            'office_phone': self.office_phone,
            'email': self.email,
            'photo': self.photo,
            'department': self.department,
            'bio': self.bio,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            user_id=data.get('user_id'),
            company_id=data.get('company_id'),
            name=data.get('name'),
            english_name=data.get('english_name'),
            position=data.get('position'),
            mobile_phone=data.get('mobile_phone'),
            office_phone=data.get('office_phone'),
            email=data.get('email'),
            photo=data.get('photo'),
            department=data.get('department'),
            bio=data.get('bio'),
            is_active=data.get('is_active', True),
        )

    def __repr__(self):
        return f'<CorporateAdminProfile {self.name} - Company {self.company_id}>'
