"""
PersonalProfile SQLAlchemy 모델

개인 계정의 프로필 정보를 관리합니다.
Phase 2: 개인-법인 분리 아키텍처의 일부입니다.
"""
from datetime import datetime
from app.database import db


class PersonalProfile(db.Model):
    """
    개인 프로필 모델

    개인 계정(account_type='personal')에 연결되는 프로필 정보입니다.
    Employee 모델의 개인정보 부분을 분리한 것입니다.
    """
    __tablename__ = 'personal_profiles'

    # 기본 키
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User 연결 (1:1 관계)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), unique=True, nullable=False)

    # 기본 개인정보
    name = db.Column(db.String(100), nullable=False)
    english_name = db.Column(db.String(100), nullable=True)
    chinese_name = db.Column(db.String(100), nullable=True)
    photo = db.Column(db.String(500), nullable=True)

    # 생년월일 정보
    birth_date = db.Column(db.String(20), nullable=True)
    lunar_birth = db.Column(db.Boolean, default=False)
    gender = db.Column(db.String(10), nullable=True)

    # 연락처 정보
    mobile_phone = db.Column(db.String(50), nullable=True)
    home_phone = db.Column(db.String(50), nullable=True)
    email = db.Column(db.String(200), nullable=True)

    # 주소 정보
    postal_code = db.Column(db.String(20), nullable=True)
    address = db.Column(db.String(500), nullable=True)
    detailed_address = db.Column(db.String(500), nullable=True)

    # 신분 정보
    resident_number = db.Column(db.String(20), nullable=True)  # 암호화 필요
    nationality = db.Column(db.String(50), nullable=True)

    # 기타 개인정보
    blood_type = db.Column(db.String(10), nullable=True)
    religion = db.Column(db.String(50), nullable=True)
    hobby = db.Column(db.String(200), nullable=True)
    specialty = db.Column(db.String(200), nullable=True)
    disability_info = db.Column(db.Text, nullable=True)
    marital_status = db.Column(db.String(20), nullable=True)  # 결혼여부: single, married, divorced, widowed

    # 실제 거주 주소 (주민등록상 주소와 분리)
    actual_postal_code = db.Column(db.String(20), nullable=True)
    actual_address = db.Column(db.String(500), nullable=True)
    actual_detailed_address = db.Column(db.String(500), nullable=True)

    # 비상연락처
    emergency_contact = db.Column(db.String(50), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)

    # 메타 정보
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 프로필 공개 설정
    is_public = db.Column(db.Boolean, default=False)  # 구직 활동 시 공개 여부

    # User 관계 설정
    user = db.relationship(
        'User',
        backref=db.backref('personal_profile', uselist=False, lazy='joined'),
        foreign_keys=[user_id]
    )

    # 1:N 관계 - 개인이 관리하는 이력 정보
    educations = db.relationship(
        'PersonalEducation',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    careers = db.relationship(
        'PersonalCareer',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    certificates = db.relationship(
        'PersonalCertificate',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    languages = db.relationship(
        'PersonalLanguage',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    awards = db.relationship(
        'PersonalAward',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    families = db.relationship(
        'PersonalFamily',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )
    project_participations = db.relationship(
        'PersonalProjectParticipation',
        backref='profile',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    # 1:1 관계
    military_service = db.relationship(
        'PersonalMilitaryService',
        backref='profile',
        uselist=False,
        cascade='all, delete-orphan'
    )

    @property
    def full_address(self):
        """전체 주소 반환 (주민등록상)"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.detailed_address:
            parts.append(self.detailed_address)
        return ' '.join(parts) if parts else None

    @property
    def actual_full_address(self):
        """전체 실제 거주 주소 반환"""
        parts = []
        if self.actual_address:
            parts.append(self.actual_address)
        if self.actual_detailed_address:
            parts.append(self.actual_detailed_address)
        return ' '.join(parts) if parts else None

    @property
    def age(self):
        """나이 계산"""
        if not self.birth_date:
            return None
        try:
            birth = datetime.strptime(self.birth_date, '%Y-%m-%d')
            today = datetime.today()
            age = today.year - birth.year
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1
            return age
        except ValueError:
            return None

    def to_dict(self):
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'name': self.name,
            'english_name': self.english_name,
            'chinese_name': self.chinese_name,
            'photo': self.photo,
            'birth_date': self.birth_date,
            'lunar_birth': self.lunar_birth,
            'gender': self.gender,
            'age': self.age,
            'mobile_phone': self.mobile_phone,
            'home_phone': self.home_phone,
            'email': self.email,
            'postal_code': self.postal_code,
            'address': self.address,
            'detailed_address': self.detailed_address,
            'full_address': self.full_address,
            'nationality': self.nationality,
            'resident_number': self.resident_number,
            'blood_type': self.blood_type,
            'religion': self.religion,
            'hobby': self.hobby,
            'specialty': self.specialty,
            'disability_info': self.disability_info,
            'marital_status': self.marital_status,
            # 실제 거주 주소
            'actual_postal_code': self.actual_postal_code,
            'actual_address': self.actual_address,
            'actual_detailed_address': self.actual_detailed_address,
            'actual_full_address': self.actual_full_address,
            # 비상연락처
            'emergency_contact': self.emergency_contact,
            'emergency_relation': self.emergency_relation,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<PersonalProfile {self.id}: {self.name}>'
