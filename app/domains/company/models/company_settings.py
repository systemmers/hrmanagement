"""
CompanySettings SQLAlchemy 모델

법인별 설정 정보를 관리합니다.
패턴 규칙, 이메일 설정, 급여일 등을 저장합니다.

Phase 2 Migration: app/domains/company/models/로 이동
"""
from datetime import datetime
from app.database import db


class CompanySettings(db.Model):
    """법인 설정 모델"""
    __tablename__ = 'company_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    key = db.Column(db.String(100), nullable=False)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), nullable=False, default='string')
    description = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('settings', lazy='dynamic'))

    __table_args__ = (
        db.UniqueConstraint('company_id', 'key', name='uq_company_settings_key'),
        db.Index('idx_company_settings_category', 'company_id', 'category'),
    )

    # Value type constants
    TYPE_STRING = 'string'
    TYPE_INTEGER = 'integer'
    TYPE_BOOLEAN = 'boolean'
    TYPE_JSON = 'json'

    VALID_TYPES = [TYPE_STRING, TYPE_INTEGER, TYPE_BOOLEAN, TYPE_JSON]

    # Category constants
    CAT_EMPLOYEE_NUMBER = 'employee_number'
    CAT_COMPANY_NUMBER = 'company_number'
    CAT_ASSET_NUMBER = 'asset_number'
    CAT_EMAIL = 'email'
    CAT_INTERNAL_PHONE = 'internal_phone'
    CAT_IP_RANGE = 'ip_range'
    CAT_PAYROLL = 'payroll'

    # Setting keys
    KEY_COMPANY_CODE = 'company_code'
    KEY_EMP_NUM_SEPARATOR = 'employee_number.separator'
    KEY_EMP_NUM_DIGITS = 'employee_number.digits'
    KEY_ASSET_NUM_SEPARATOR = 'asset_number.separator'
    KEY_ASSET_NUM_DIGITS = 'asset_number.digits'
    KEY_EMAIL_DOMAIN = 'email.domain'
    KEY_EMAIL_AUTO_GENERATE = 'email.auto_generate'
    KEY_EMAIL_FORMAT = 'email.format'
    KEY_INT_PHONE_DIGITS = 'internal_phone.digits'
    KEY_INT_PHONE_RANGE_START = 'internal_phone.range_start'
    KEY_INT_PHONE_RANGE_END = 'internal_phone.range_end'
    KEY_PAYMENT_DAY = 'payroll.payment_day'

    # Default values
    DEFAULTS = {
        KEY_COMPANY_CODE: ('', TYPE_STRING, '회사코드 (영문 대문자, 최대 6자리)'),
        KEY_EMP_NUM_SEPARATOR: ('-', TYPE_STRING, '사번 구분자'),
        KEY_EMP_NUM_DIGITS: ('6', TYPE_INTEGER, '사번 순번 자릿수'),
        KEY_ASSET_NUM_SEPARATOR: ('-', TYPE_STRING, '자산번호 구분자'),
        KEY_ASSET_NUM_DIGITS: ('6', TYPE_INTEGER, '자산번호 순번 자릿수'),
        KEY_EMAIL_DOMAIN: ('', TYPE_STRING, '이메일 도메인'),
        KEY_EMAIL_AUTO_GENERATE: ('false', TYPE_BOOLEAN, '이메일 자동 생성'),
        KEY_EMAIL_FORMAT: ('{first}.{last}', TYPE_STRING, '이메일 포맷'),
        KEY_INT_PHONE_DIGITS: ('4', TYPE_INTEGER, '내선번호 자릿수'),
        KEY_INT_PHONE_RANGE_START: ('1000', TYPE_INTEGER, '내선번호 시작'),
        KEY_INT_PHONE_RANGE_END: ('9999', TYPE_INTEGER, '내선번호 종료'),
        KEY_PAYMENT_DAY: ('25', TYPE_INTEGER, '급여일'),
    }

    def get_typed_value(self):
        """타입에 맞게 변환된 값 반환"""
        if self.value is None:
            return None

        if self.value_type == self.TYPE_INTEGER:
            return int(self.value) if self.value else 0
        elif self.value_type == self.TYPE_BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == self.TYPE_JSON:
            import json
            return json.loads(self.value) if self.value else {}
        return self.value

    def set_typed_value(self, value):
        """타입에 맞게 값 저장"""
        if value is None:
            self.value = None
        elif self.value_type == self.TYPE_INTEGER:
            self.value = str(int(value))
        elif self.value_type == self.TYPE_BOOLEAN:
            self.value = 'true' if value else 'false'
        elif self.value_type == self.TYPE_JSON:
            import json
            self.value = json.dumps(value, ensure_ascii=False)
        else:
            self.value = str(value)

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'companyId': self.company_id,
            'key': self.key,
            'value': self.get_typed_value(),
            'valueType': self.value_type,
            'description': self.description,
            'category': self.category,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        instance = cls(
            company_id=data.get('companyId'),
            key=data.get('key'),
            value_type=data.get('valueType', cls.TYPE_STRING),
            description=data.get('description'),
            category=data.get('category'),
        )
        instance.set_typed_value(data.get('value'))
        return instance

    @classmethod
    def get_default(cls, key):
        """키에 대한 기본값 반환"""
        default = cls.DEFAULTS.get(key)
        if default:
            return default[0]
        return None

    def __repr__(self):
        return f'<CompanySettings {self.company_id}:{self.key}>'
