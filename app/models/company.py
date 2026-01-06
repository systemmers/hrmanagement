"""
Company SQLAlchemy 모델

법인(기업) 정보를 관리하는 모델입니다.
플랫폼 멀티테넌시 구현을 위한 핵심 모델입니다.
"""
from datetime import datetime
from app.database import db


class Company(db.Model):
    """법인(기업) 모델"""
    __tablename__ = 'companies'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 법인 기본 정보
    name = db.Column(db.String(200), nullable=False, index=True)
    business_number = db.Column(db.String(20), unique=True, nullable=False, index=True)
    corporate_number = db.Column(db.String(20), nullable=True)
    representative = db.Column(db.String(100), nullable=False)

    # 사업 정보
    business_type = db.Column(db.String(100), nullable=True)
    business_category = db.Column(db.String(100), nullable=True)
    establishment_date = db.Column(db.Date, nullable=True)

    # 연락처 정보
    phone = db.Column(db.String(20), nullable=True)
    fax = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(120), nullable=True)
    website = db.Column(db.String(200), nullable=True)

    # 주소 정보
    postal_code = db.Column(db.String(10), nullable=True)
    address = db.Column(db.String(300), nullable=True)
    address_detail = db.Column(db.String(200), nullable=True)

    # 조직 연결 (해당 법인의 조직트리 루트)
    root_organization_id = db.Column(
        db.Integer,
        db.ForeignKey('organizations.id'),
        nullable=True
    )

    # 상태 정보
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_verified = db.Column(db.Boolean, default=False, nullable=False)
    verified_at = db.Column(db.DateTime, nullable=True)

    # 플랜/구독 정보 (향후 확장)
    plan_type = db.Column(db.String(50), default='free', nullable=False)
    plan_expires_at = db.Column(db.DateTime, nullable=True)
    max_employees = db.Column(db.Integer, default=10, nullable=False)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # Relationships
    root_organization = db.relationship(
        'Organization',
        foreign_keys=[root_organization_id],
        backref=db.backref('company', uselist=False)
    )

    # Plan constants
    PLAN_FREE = 'free'
    PLAN_BASIC = 'basic'
    PLAN_PREMIUM = 'premium'
    PLAN_ENTERPRISE = 'enterprise'

    VALID_PLANS = [PLAN_FREE, PLAN_BASIC, PLAN_PREMIUM, PLAN_ENTERPRISE]

    PLAN_LABELS = {
        PLAN_FREE: '무료',
        PLAN_BASIC: '베이직',
        PLAN_PREMIUM: '프리미엄',
        PLAN_ENTERPRISE: '엔터프라이즈',
    }

    PLAN_MAX_EMPLOYEES = {
        PLAN_FREE: 10,
        PLAN_BASIC: 50,
        PLAN_PREMIUM: 200,
        PLAN_ENTERPRISE: 9999,
    }

    def get_plan_label(self):
        """플랜 유형 한글 라벨"""
        return self.PLAN_LABELS.get(self.plan_type, self.plan_type)

    def can_add_employee(self):
        """직원 추가 가능 여부 (플랜 제한 확인)"""
        from app.domains.employee.models import Employee
        current_count = Employee.query.filter_by(
            organization_id=self.root_organization_id
        ).count() if self.root_organization_id else 0
        return current_count < self.max_employees

    def get_employee_count(self):
        """현재 직원 수"""
        from app.domains.employee.models import Employee
        if not self.root_organization_id:
            return 0
        return Employee.query.filter_by(
            organization_id=self.root_organization_id
        ).count()

    def format_business_number(self):
        """사업자등록번호 포맷팅 (XXX-XX-XXXXX)"""
        bn = self.business_number.replace('-', '')
        if len(bn) == 10:
            return f"{bn[:3]}-{bn[3:5]}-{bn[5:]}"
        return self.business_number

    def verify(self):
        """법인 인증 처리"""
        self.is_verified = True
        self.verified_at = datetime.utcnow()

    def to_dict(self, include_stats=False):
        """딕셔너리 변환"""
        data = {
            'id': self.id,
            'name': self.name,
            'business_number': self.business_number,
            'business_number_formatted': self.format_business_number(),
            'corporate_number': self.corporate_number,
            'representative': self.representative,
            'business_type': self.business_type,
            'business_category': self.business_category,
            'establishment_date': self.establishment_date.isoformat() if self.establishment_date else None,
            'phone': self.phone,
            'fax': self.fax,
            'email': self.email,
            'website': self.website,
            'postal_code': self.postal_code,
            'address': self.address,
            'address_detail': self.address_detail,
            'full_address': f"{self.address or ''} {self.address_detail or ''}".strip(),
            'root_organization_id': self.root_organization_id,
            'is_active': self.is_active,
            'is_verified': self.is_verified,
            'verified_at': self.verified_at.isoformat() if self.verified_at else None,
            'plan_type': self.plan_type,
            'plan_label': self.get_plan_label(),
            'plan_expires_at': self.plan_expires_at.isoformat() if self.plan_expires_at else None,
            'max_employees': self.max_employees,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_stats:
            data['employee_count'] = self.get_employee_count()
            data['can_add_employee'] = self.can_add_employee()

        return data

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            name=data.get('name'),
            business_number=data.get('business_number', '').replace('-', ''),
            corporate_number=data.get('corporate_number'),
            representative=data.get('representative'),
            business_type=data.get('business_type'),
            business_category=data.get('business_category'),
            establishment_date=data.get('establishment_date'),
            phone=data.get('phone'),
            fax=data.get('fax'),
            email=data.get('email'),
            website=data.get('website'),
            postal_code=data.get('postal_code'),
            address=data.get('address'),
            address_detail=data.get('address_detail'),
            root_organization_id=data.get('root_organization_id'),
            is_active=data.get('is_active', True),
            plan_type=data.get('plan_type', cls.PLAN_FREE),
            max_employees=data.get('max_employees', cls.PLAN_MAX_EMPLOYEES.get(cls.PLAN_FREE, 10)),
        )

    def __repr__(self):
        return f'<Company {self.name} ({self.business_number})>'
