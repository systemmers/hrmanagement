"""
IpRange SQLAlchemy 모델

IP 범위를 관리합니다.
법인별 IP 대역과 부서 라벨을 저장합니다.
"""
from datetime import datetime
from app.database import db


class IpRange(db.Model):
    """IP 범위 모델"""
    __tablename__ = 'ip_ranges'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id', ondelete='CASCADE'), nullable=False)
    range_start = db.Column(db.String(15), nullable=False)  # 192.168.1.1
    range_end = db.Column(db.String(15), nullable=False)    # 192.168.1.100
    subnet = db.Column(db.String(15), nullable=True)        # 255.255.255.0
    gateway = db.Column(db.String(15), nullable=True)       # 192.168.1.1
    label = db.Column(db.String(100), nullable=True)        # 부서 라벨
    ip_count = db.Column(db.Integer, nullable=True)         # 자동 계산된 IP 개수
    description = db.Column(db.Text, nullable=True)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    company = db.relationship('Company', backref=db.backref('ip_ranges', lazy='dynamic'))
    assignments = db.relationship('IpAssignment', back_populates='ip_range', cascade='all, delete-orphan')

    __table_args__ = (
        db.Index('idx_ip_ranges_company', 'company_id'),
    )

    @staticmethod
    def ip_to_int(ip):
        """IP 문자열을 정수로 변환"""
        parts = ip.split('.')
        if len(parts) != 4:
            return 0
        return (int(parts[0]) << 24) + (int(parts[1]) << 16) + (int(parts[2]) << 8) + int(parts[3])

    @staticmethod
    def int_to_ip(num):
        """정수를 IP 문자열로 변환"""
        return f"{(num >> 24) & 255}.{(num >> 16) & 255}.{(num >> 8) & 255}.{num & 255}"

    def calculate_ip_count(self):
        """IP 개수 계산"""
        start_int = self.ip_to_int(self.range_start)
        end_int = self.ip_to_int(self.range_end)
        if end_int >= start_int:
            self.ip_count = end_int - start_int + 1
        else:
            self.ip_count = 0
        return self.ip_count

    def get_all_ips(self):
        """범위 내 모든 IP 목록 반환"""
        start_int = self.ip_to_int(self.range_start)
        end_int = self.ip_to_int(self.range_end)
        return [self.int_to_ip(i) for i in range(start_int, end_int + 1)]

    def is_valid_ip(self, ip):
        """IP가 범위 내에 있는지 확인"""
        ip_int = self.ip_to_int(ip)
        start_int = self.ip_to_int(self.range_start)
        end_int = self.ip_to_int(self.range_end)
        return start_int <= ip_int <= end_int

    def get_usage_stats(self):
        """사용 통계 반환"""
        in_use = sum(1 for a in self.assignments if a.status == 'in_use')
        retired = sum(1 for a in self.assignments if a.status == 'retired')
        available = (self.ip_count or 0) - in_use - retired
        return {
            'total': self.ip_count or 0,
            'inUse': in_use,
            'retired': retired,
            'available': max(0, available),
        }

    def to_dict(self, include_stats=False):
        """딕셔너리 반환"""
        data = {
            'id': self.id,
            'companyId': self.company_id,
            'rangeStart': self.range_start,
            'rangeEnd': self.range_end,
            'subnet': self.subnet,
            'gateway': self.gateway,
            'label': self.label,
            'ipCount': self.ip_count,
            'description': self.description,
            'isActive': self.is_active,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }
        if include_stats:
            data['stats'] = self.get_usage_stats()
        return data

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        instance = cls(
            company_id=data.get('companyId'),
            range_start=data.get('rangeStart'),
            range_end=data.get('rangeEnd'),
            subnet=data.get('subnet'),
            gateway=data.get('gateway'),
            label=data.get('label'),
            description=data.get('description'),
            is_active=data.get('isActive', True),
        )
        instance.calculate_ip_count()
        return instance

    def __repr__(self):
        return f'<IpRange {self.range_start}-{self.range_end} ({self.label})>'
