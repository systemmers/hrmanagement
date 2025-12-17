"""
IpAssignment SQLAlchemy 모델

IP 할당 정보를 관리합니다.
개별 IP의 할당 상태와 이력을 저장합니다.
"""
from datetime import datetime
from app.database import db


class IpAssignment(db.Model):
    """IP 할당 모델"""
    __tablename__ = 'ip_assignments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    range_id = db.Column(db.Integer, db.ForeignKey('ip_ranges.id', ondelete='CASCADE'), nullable=False)
    ip_address = db.Column(db.String(15), nullable=False)  # 할당된 IP
    status = db.Column(db.String(20), nullable=False, default='available')  # available, in_use, retired
    assigned_to_type = db.Column(db.String(20), nullable=True)  # employee, asset
    assigned_to_id = db.Column(db.Integer, nullable=True)
    assigned_at = db.Column(db.DateTime, nullable=True)
    retired_at = db.Column(db.DateTime, nullable=True)
    retired_reason = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('ip_assignments', lazy='dynamic'))
    ip_range = db.relationship('IpRange', back_populates='assignments')

    __table_args__ = (
        db.UniqueConstraint('company_id', 'ip_address', name='uq_ip_assignments_address'),
        db.Index('idx_ip_assignments_status', 'company_id', 'range_id', 'status'),
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
        """IP 할당"""
        self.status = self.STATUS_IN_USE
        self.assigned_to_type = assign_type
        self.assigned_to_id = assign_id
        self.assigned_at = datetime.utcnow()

    def release(self):
        """IP 해제 (다시 사용 가능)"""
        self.status = self.STATUS_AVAILABLE
        self.assigned_to_type = None
        self.assigned_to_id = None
        self.assigned_at = None

    def retire(self, reason=None):
        """IP 폐기 (재사용 불가)"""
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
            'rangeId': self.range_id,
            'ipAddress': self.ip_address,
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
            range_id=data.get('rangeId'),
            ip_address=data.get('ipAddress'),
            status=data.get('status', cls.STATUS_AVAILABLE),
            assigned_to_type=data.get('assignedToType'),
            assigned_to_id=data.get('assignedToId'),
        )

    @classmethod
    def get_status_label(cls, status):
        """상태 한글명 반환"""
        return cls.STATUS_LABELS.get(status, status)

    def __repr__(self):
        return f'<IpAssignment {self.ip_address} ({self.status})>'
