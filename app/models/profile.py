"""
Profile SQLAlchemy 모델

통합 프로필 모델 - 개인/직원 공통 프로필 정보 관리
Phase 4: 통합 프로필 아키텍처
Phase 9: FieldRegistry 기반 to_dict() 정렬
"""
from collections import OrderedDict
from datetime import datetime
from typing import Optional

from app.database import db


class Profile(db.Model):
    """
    통합 프로필 모델

    개인 계정(personal)과 직원(employee)이 공유하는 프로필 정보입니다.
    - 개인 계정: user_id로 연결 (1:1)
    - 직원: employees.profile_id로 참조 (N:1 가능)
    """
    __tablename__ = 'profiles'

    # 기본 키
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # User 연결 (개인 계정의 경우)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

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
    marital_status = db.Column(db.String(20), nullable=True)

    # 실제 거주 주소
    actual_postal_code = db.Column(db.String(20), nullable=True)
    actual_address = db.Column(db.String(500), nullable=True)
    actual_detailed_address = db.Column(db.String(500), nullable=True)

    # 비상연락처
    emergency_contact = db.Column(db.String(50), nullable=True)
    emergency_relation = db.Column(db.String(50), nullable=True)

    # 메타 정보
    is_public = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # User 관계 설정
    user = db.relationship(
        'User',
        backref=db.backref('profile', uselist=False, lazy='joined'),
        foreign_keys=[user_id]
    )

    # Employee 역참조 (employees.profile_id -> profiles.id)
    # employees = db.relationship('Employee', backref='profile', lazy='dynamic')

    # 이력 관계 (profile_id 기반 통합 조회)
    educations = db.relationship(
        'Education',
        primaryjoin='Profile.id == Education.profile_id',
        foreign_keys='Education.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    careers = db.relationship(
        'Career',
        primaryjoin='Profile.id == Career.profile_id',
        foreign_keys='Career.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    certificates = db.relationship(
        'Certificate',
        primaryjoin='Profile.id == Certificate.profile_id',
        foreign_keys='Certificate.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    languages = db.relationship(
        'Language',
        primaryjoin='Profile.id == Language.profile_id',
        foreign_keys='Language.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    military_services = db.relationship(
        'MilitaryService',
        primaryjoin='Profile.id == MilitaryService.profile_id',
        foreign_keys='MilitaryService.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    family_members = db.relationship(
        'FamilyMember',
        primaryjoin='Profile.id == FamilyMember.profile_id',
        foreign_keys='FamilyMember.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    awards = db.relationship(
        'Award',
        primaryjoin='Profile.id == Award.profile_id',
        foreign_keys='Award.profile_id',
        backref='profile',
        lazy='dynamic'
    )
    project_participations = db.relationship(
        'ProjectParticipation',
        primaryjoin='Profile.id == ProjectParticipation.profile_id',
        foreign_keys='ProjectParticipation.profile_id',
        backref='profile',
        lazy='dynamic'
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

    @property
    def is_personal(self):
        """개인 계정 소유 프로필인지 확인"""
        return self.user_id is not None

    def _collect_raw_data(self) -> dict:
        """원시 필드 데이터 수집 (내부용)"""
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
            'is_personal': self.is_personal,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

    def to_dict(self, ordered: bool = False, account_type: Optional[str] = None) -> dict:
        """딕셔너리 변환 (Phase 9: FieldRegistry 기반 정렬 지원)

        Args:
            ordered: True면 FieldRegistry 순서 적용, False면 기존 방식
            account_type: 가시성 필터링용 계정 타입

        Returns:
            프로필 정보 딕셔너리
        """
        raw = self._collect_raw_data()

        # 기존 방식 (하위 호환성)
        if not ordered:
            return raw

        # Phase 9: FieldRegistry 기반 정렬
        from app.constants.field_registry import FieldRegistry

        result = OrderedDict()
        result['id'] = raw.pop('id')
        result['user_id'] = raw.pop('user_id')

        # 섹션별 정렬 적용 (profile 도메인)
        section_ids = ['personal_basic', 'contact', 'address', 'actual_address', 'personal_extended']
        for section_id in section_ids:
            section_data = FieldRegistry.to_ordered_dict(section_id, raw, account_type)
            for key, value in section_data.items():
                if key in raw:
                    result[key] = raw.pop(key)

        # 나머지 필드 추가 (정의되지 않은 필드들)
        for key, value in raw.items():
            result[key] = value

        return dict(result)

    def to_snapshot(self):
        """퇴사 시 스냅샷용 딕셔너리 (민감정보 포함)"""
        data = self.to_dict()
        # 스냅샷 메타데이터 추가
        data['snapshot_version'] = '1.0'
        data['snapshot_at'] = datetime.utcnow().isoformat()
        return data

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            user_id=data.get('user_id'),
            name=data.get('name'),
            english_name=data.get('english_name') or data.get('englishName'),
            chinese_name=data.get('chinese_name') or data.get('chineseName'),
            photo=data.get('photo'),
            birth_date=data.get('birth_date') or data.get('birthDate'),
            lunar_birth=data.get('lunar_birth') or data.get('lunarBirth', False),
            gender=data.get('gender'),
            mobile_phone=data.get('mobile_phone') or data.get('mobilePhone'),
            home_phone=data.get('home_phone') or data.get('homePhone'),
            email=data.get('email'),
            postal_code=data.get('postal_code') or data.get('postalCode'),
            address=data.get('address'),
            detailed_address=data.get('detailed_address') or data.get('detailedAddress'),
            resident_number=data.get('resident_number') or data.get('residentNumber'),
            nationality=data.get('nationality'),
            blood_type=data.get('blood_type') or data.get('bloodType'),
            religion=data.get('religion'),
            hobby=data.get('hobby'),
            specialty=data.get('specialty'),
            disability_info=data.get('disability_info') or data.get('disabilityInfo'),
            marital_status=data.get('marital_status') or data.get('maritalStatus'),
            actual_postal_code=data.get('actual_postal_code') or data.get('actualPostalCode'),
            actual_address=data.get('actual_address') or data.get('actualAddress'),
            actual_detailed_address=data.get('actual_detailed_address') or data.get('actualDetailedAddress'),
            emergency_contact=data.get('emergency_contact') or data.get('emergencyContact'),
            emergency_relation=data.get('emergency_relation') or data.get('emergencyRelation'),
            is_public=data.get('is_public') or data.get('isPublic', False),
        )

    def __repr__(self):
        return f'<Profile {self.id}: {self.name}>'
