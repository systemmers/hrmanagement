"""
NumberRegistry SQLAlchemy 모델

번호 레지스트리를 관리합니다.
사번, 자산번호의 할당 상태와 이력을 저장합니다.

Phase 2 Migration: app/domains/company/models/로 이동
"""
from datetime import datetime
from app.database import db


class NumberRegistry(db.Model):
    """번호 레지스트리 모델"""
    __tablename__ = 'number_registry'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    category_id = db.Column(db.Integer, db.ForeignKey('number_categories.id', ondelete='CASCADE'), nullable=False)
    full_number = db.Column(db.String(50), nullable=False)  # 전체 번호 (ABC-NB-000001)
    sequence = db.Column(db.Integer, nullable=False)  # 순번
    status = db.Column(db.String(20), nullable=False, default='available')  # available, in_use, retired
    assigned_to_type = db.Column(db.String(20), nullable=True)  # employee, asset
    assigned_to_id = db.Column(db.Integer, nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    retired_at = db.Column(db.DateTime, nullable=True)
    retired_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('number_registries', lazy='dynamic'))
    category = db.relationship('NumberCategory', back_populates='registries')

    __table_args__ = (
        db.UniqueConstraint('company_id', 'category_id', 'sequence', name='uq_number_registry_seq'),
        db.Index('idx_number_registry_status', 'company_id', 'category_id', 'status'),
        db.Index('idx_number_registry_full', 'company_id', 'full_number'),
    )

    # Status constants
    STATUS_AVAILABLE = 'available'
    STATUS_IN_USE = 'in_use'
    STATUS_RETIRED = 'retired'

    VALID_STATUSES = [STATUS_AVAILABLE, STATUS_IN_USE, STATUS_RETIRED]

    STATUS_LABELS = {
        STATUS_AVAILABLE: '사용 가능',
        STATUS_IN_USE: '사용중',
        STATUS_RETIRED: '폐기됨',
    }

    # Assignment type constants
    ASSIGN_TYPE_EMPLOYEE = 'employee'
    ASSIGN_TYPE_ASSET = 'asset'

    def assign(self, assign_type, assign_id):
        """번호 할당"""
        self.status = self.STATUS_IN_USE
        self.assigned_to_type = assign_type
        self.assigned_to_id = assign_id
        self.assigned_at = datetime.utcnow()

    def release(self):
        """번호 해제 (다시 사용 가능)"""
        self.status = self.STATUS_AVAILABLE
        self.assigned_to_type = None
        self.assigned_to_id = None
        self.assigned_at = None

    def retire(self, reason=None):
        """번호 폐기 (재사용 불가)"""
        self.status = self.STATUS_RETIRED
        self.retired_at = datetime.utcnow()
        self.retired_reason = reason

    def is_available(self):
        """사용 가능 여부"""
        return self.status == self.STATUS_AVAILABLE

    def is_in_use(self):
        """사용중 여부"""
        return self.status == self.STATUS_IN_USE

    def is_retired(self):
        """폐기 여부"""
        return self.status == self.STATUS_RETIRED

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'companyId': self.company_id,
            'categoryId': self.category_id,
            'fullNumber': self.full_number,
            'sequence': self.sequence,
            'status': self.status,
            'statusLabel': self.STATUS_LABELS.get(self.status, self.status),
            'assignedToType': self.assigned_to_type,
            'assignedToId': self.assigned_to_id,
            'assignedAt': self.assigned_at.isoformat() if self.assigned_at else None,
            'retiredAt': self.retired_at.isoformat() if self.retired_at else None,
            'retiredReason': self.retired_reason,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            company_id=data.get('companyId'),
            category_id=data.get('categoryId'),
            full_number=data.get('fullNumber'),
            sequence=data.get('sequence'),
            status=data.get('status', cls.STATUS_AVAILABLE),
            assigned_to_type=data.get('assignedToType'),
            assigned_to_id=data.get('assignedToId'),
        )

    @classmethod
    def get_status_label(cls, status):
        """상태 한글명 반환"""
        return cls.STATUS_LABELS.get(status, status)

    def __repr__(self):
        return f'<NumberRegistry {self.full_number} ({self.status})>'
