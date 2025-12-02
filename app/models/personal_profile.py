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

    # 1:1 관계
    military_service = db.relationship(
        'PersonalMilitaryService',
        backref='profile',
        uselist=False,
        cascade='all, delete-orphan'
    )

    @property
    def full_address(self):
        """전체 주소 반환"""
        parts = []
        if self.address:
            parts.append(self.address)
        if self.detailed_address:
            parts.append(self.detailed_address)
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
            'blood_type': self.blood_type,
            'religion': self.religion,
            'hobby': self.hobby,
            'specialty': self.specialty,
            'disability_info': self.disability_info,
            'is_public': self.is_public,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self):
        return f'<PersonalProfile {self.id}: {self.name}>'


# ============================================================
# 개인 이력 관련 모델 (Employee 이력과 분리)
# ============================================================

class PersonalEducation(db.Model):
    """개인 학력 정보"""
    __tablename__ = 'personal_educations'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    school_type = db.Column(db.String(50), nullable=True)  # 고등학교, 대학교, 대학원 등
    school_name = db.Column(db.String(200), nullable=False)
    major = db.Column(db.String(200), nullable=True)
    degree = db.Column(db.String(50), nullable=True)  # 학사, 석사, 박사 등
    admission_date = db.Column(db.String(20), nullable=True)
    graduation_date = db.Column(db.String(20), nullable=True)
    status = db.Column(db.String(50), nullable=True)  # 졸업, 재학, 중퇴 등
    gpa = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'school_type': self.school_type,
            'school_name': self.school_name,
            'major': self.major,
            'degree': self.degree,
            'admission_date': self.admission_date,
            'graduation_date': self.graduation_date,
            'status': self.status,
            'gpa': self.gpa,
            'notes': self.notes,
        }


class PersonalCareer(db.Model):
    """개인 경력 정보"""
    __tablename__ = 'personal_careers'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    company_name = db.Column(db.String(200), nullable=False)
    department = db.Column(db.String(100), nullable=True)
    position = db.Column(db.String(100), nullable=True)
    job_title = db.Column(db.String(100), nullable=True)
    start_date = db.Column(db.String(20), nullable=True)
    end_date = db.Column(db.String(20), nullable=True)
    is_current = db.Column(db.Boolean, default=False)
    responsibilities = db.Column(db.Text, nullable=True)
    achievements = db.Column(db.Text, nullable=True)
    reason_for_leaving = db.Column(db.String(500), nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'company_name': self.company_name,
            'department': self.department,
            'position': self.position,
            'job_title': self.job_title,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'is_current': self.is_current,
            'responsibilities': self.responsibilities,
            'achievements': self.achievements,
            'reason_for_leaving': self.reason_for_leaving,
        }


class PersonalCertificate(db.Model):
    """개인 자격증 정보"""
    __tablename__ = 'personal_certificates'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    name = db.Column(db.String(200), nullable=False)
    issuing_organization = db.Column(db.String(200), nullable=True)
    issue_date = db.Column(db.String(20), nullable=True)
    expiry_date = db.Column(db.String(20), nullable=True)
    certificate_number = db.Column(db.String(100), nullable=True)
    grade = db.Column(db.String(50), nullable=True)  # 등급/급수
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'name': self.name,
            'issuing_organization': self.issuing_organization,
            'issue_date': self.issue_date,
            'expiry_date': self.expiry_date,
            'certificate_number': self.certificate_number,
            'grade': self.grade,
            'notes': self.notes,
        }


class PersonalLanguage(db.Model):
    """개인 어학 능력 정보"""
    __tablename__ = 'personal_languages'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    profile_id = db.Column(db.Integer, db.ForeignKey('personal_profiles.id'), nullable=False)

    language = db.Column(db.String(100), nullable=False)
    proficiency = db.Column(db.String(50), nullable=True)  # 초급, 중급, 고급, 원어민
    test_name = db.Column(db.String(100), nullable=True)  # TOEIC, JLPT 등
    score = db.Column(db.String(50), nullable=True)
    test_date = db.Column(db.String(20), nullable=True)
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'language': self.language,
            'proficiency': self.proficiency,
            'test_name': self.test_name,
            'score': self.score,
            'test_date': self.test_date,
            'notes': self.notes,
        }


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
    notes = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'service_type': self.service_type,
            'branch': self.branch,
            'rank': self.rank,
            'start_date': self.start_date,
            'end_date': self.end_date,
            'discharge_type': self.discharge_type,
            'specialty': self.specialty,
            'notes': self.notes,
        }
