"""
NumberCategory SQLAlchemy 모델

번호 체계 분류코드를 관리합니다.
사번, 자산번호 등의 분류 코드와 현재 시퀀스를 저장합니다.
"""
from datetime import datetime
from app.database import db


class NumberCategory(db.Model):
    """번호 분류코드 모델"""
    __tablename__ = 'number_categories'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    type = db.Column(db.String(20), nullable=False)  # employee_number, asset_number
    code = db.Column(db.String(6), nullable=False)   # 분류코드 (NB, DT, DEPT 등)
    name = db.Column(db.String(100), nullable=False)  # 분류명
    description = db.Column(db.Text, nullable=True)
    current_sequence = db.Column(db.Integer, nullable=False, default=0)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('number_categories', lazy='dynamic'))
    registries = db.relationship('NumberRegistry', back_populates='category', cascade='all, delete-orphan')

    __table_args__ = (
        db.UniqueConstraint('company_id', 'type', 'code', name='uq_number_category'),
        db.Index('idx_number_categories_type', 'company_id', 'type'),
    )

    # Type constants
    TYPE_EMPLOYEE = 'employee_number'
    TYPE_ASSET = 'asset_number'

    VALID_TYPES = [TYPE_EMPLOYEE, TYPE_ASSET]

    TYPE_LABELS = {
        TYPE_EMPLOYEE: '사번',
        TYPE_ASSET: '자산번호',
    }

    # Default asset categories
    DEFAULT_ASSET_CATEGORIES = [
        ('NB', '노트북', '휴대용 컴퓨터'),
        ('DT', '데스크탑', '고정형 컴퓨터'),
        ('MON', '모니터', '디스플레이'),
        ('KB', '키보드', '입력장치'),
        ('MS', '마우스', '입력장치'),
        ('PR', '프린터', '출력장치'),
        ('PH', '전화기', '유선/무선 전화'),
        ('ETC', '기타', '기타 자산'),
    ]

    def get_next_sequence(self):
        """다음 시퀀스 번호 반환 (increment 포함)"""
        self.current_sequence += 1
        return self.current_sequence

    def peek_next_sequence(self):
        """다음 시퀀스 번호 조회 (increment 없음)"""
        return self.current_sequence + 1

    def generate_number(self, company_code, separator='-', digits=6):
        """전체 번호 생성"""
        seq = self.peek_next_sequence()
        seq_str = str(seq).zfill(digits)
        return f"{company_code}{separator}{self.code}{separator}{seq_str}"

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'companyId': self.company_id,
            'type': self.type,
            'typeLabel': self.TYPE_LABELS.get(self.type, self.type),
            'code': self.code,
            'name': self.name,
            'description': self.description,
            'currentSequence': self.current_sequence,
            'nextSequence': self.peek_next_sequence(),
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            company_id=data.get('companyId'),
            type=data.get('type'),
            code=data.get('code', '').upper()[:6],
            name=data.get('name'),
            description=data.get('description'),
            current_sequence=data.get('currentSequence', 0),
            is_active=data.get('isActive', True),
        )

    @classmethod
    def get_type_label(cls, type_code):
        """타입 한글명 반환"""
        return cls.TYPE_LABELS.get(type_code, type_code)

    def __repr__(self):
        return f'<NumberCategory {self.type}:{self.code}>'
