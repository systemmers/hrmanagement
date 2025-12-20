"""
PersonCorporateContract SQLAlchemy Model

개인-법인 간 계약 관계를 관리하는 모델입니다.
계약 요청, 승인/거절, 데이터 공유 설정 등을 처리합니다.
Phase 8: DictSerializableMixin 적용 (DataSharingSettings, SyncLog)
"""
from datetime import datetime
from app.database import db
from app.models.mixins import DictSerializableMixin


class PersonCorporateContract(db.Model):
    """개인-법인 계약 관계 모델"""
    __tablename__ = 'person_corporate_contracts'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 계약 당사자
    person_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=False,
        index=True
    )
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=False,
        index=True
    )

    # 계약 상태
    status = db.Column(
        db.String(20),
        default='requested',
        nullable=False,
        index=True
    )

    # 계약 유형
    contract_type = db.Column(
        db.String(30),
        default='employment',
        nullable=False
    )

    # 계약 기간
    contract_start_date = db.Column(db.Date, nullable=True)
    contract_end_date = db.Column(db.Date, nullable=True)

    # 직위/부서 정보
    position = db.Column(db.String(100), nullable=True)
    department = db.Column(db.String(100), nullable=True)
    employee_number = db.Column(db.String(50), nullable=True)

    # 요청자 정보
    requested_by = db.Column(
        db.String(20),
        default='company',
        nullable=False
    )

    # 메모
    notes = db.Column(db.Text, nullable=True)
    rejection_reason = db.Column(db.Text, nullable=True)
    termination_reason = db.Column(db.Text, nullable=True)

    # 타임스탬프
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    terminated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 승인/거절/종료 처리자
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    terminated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 상태 상수
    STATUS_REQUESTED = 'requested'
    STATUS_APPROVED = 'approved'
    STATUS_REJECTED = 'rejected'
    STATUS_TERMINATED = 'terminated'
    STATUS_EXPIRED = 'expired'

    # 계약 유형 상수
    TYPE_EMPLOYMENT = 'employment'
    TYPE_CONTRACT = 'contract'
    TYPE_FREELANCE = 'freelance'
    TYPE_INTERN = 'intern'

    # 계약 유형 레이블
    TYPE_LABELS = {
        'employment': '정규직',
        'contract': '계약직',
        'freelance': '프리랜서',
        'intern': '인턴'
    }

    # 관계 설정
    person_user = db.relationship(
        'User',
        foreign_keys=[person_user_id],
        backref=db.backref('person_contracts', lazy='dynamic')
    )
    company = db.relationship(
        'Company',
        backref=db.backref('person_contracts', lazy='dynamic')
    )
    data_sharing_settings = db.relationship(
        'DataSharingSettings',
        backref='contract',
        uselist=False,
        cascade='all, delete-orphan'
    )
    sync_logs = db.relationship(
        'SyncLog',
        backref='contract',
        lazy='dynamic',
        cascade='all, delete-orphan'
    )

    def __repr__(self):
        return f'<PersonCorporateContract {self.id}: {self.person_user_id} <-> {self.company_id}>'

    def to_dict(self, include_relations=False):
        """딕셔너리 변환"""
        data = {
            'id': self.id,
            'person_user_id': self.person_user_id,
            'company_id': self.company_id,
            'status': self.status,
            'contract_type': self.contract_type,
            'contract_type_label': self.TYPE_LABELS.get(self.contract_type, self.contract_type),
            'contract_start_date': self.contract_start_date.isoformat() if self.contract_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'position': self.position,
            'department': self.department,
            'employee_number': self.employee_number,
            'requested_by': self.requested_by,
            'notes': self.notes,
            'rejection_reason': self.rejection_reason,
            'termination_reason': self.termination_reason,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'terminated_at': self.terminated_at.isoformat() if self.terminated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
        }

        if include_relations:
            if self.person_user:
                data['person_name'] = self.person_user.username
                data['person_email'] = self.person_user.email
            if self.company:
                data['company_name'] = self.company.name

        return data

    def approve(self, user_id=None):
        """계약 승인"""
        self.status = self.STATUS_APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id
        self.updated_at = datetime.utcnow()

    def reject(self, user_id=None, reason=None):
        """계약 거절"""
        self.status = self.STATUS_REJECTED
        self.rejected_at = datetime.utcnow()
        self.rejected_by = user_id
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()

    def terminate(self, user_id=None, reason=None):
        """계약 종료"""
        self.status = self.STATUS_TERMINATED
        self.terminated_at = datetime.utcnow()
        self.terminated_by = user_id
        self.termination_reason = reason
        self.updated_at = datetime.utcnow()

    @property
    def is_active(self):
        """활성 계약 여부"""
        return self.status == self.STATUS_APPROVED

    @property
    def is_pending(self):
        """대기 중 여부"""
        return self.status == self.STATUS_REQUESTED


class DataSharingSettings(DictSerializableMixin, db.Model):
    """데이터 공유 설정 모델"""
    __tablename__ = 'data_sharing_settings'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'contract_id': ['contractId'],
        'share_basic_info': ['shareBasicInfo'],
        'share_contact': ['shareContact'],
        'share_education': ['shareEducation'],
        'share_career': ['shareCareer'],
        'share_certificates': ['shareCertificates'],
        'share_languages': ['shareLanguages'],
        'share_military': ['shareMilitary'],
        'is_realtime_sync': ['isRealtimeSync'],
        'created_at': ['createdAt'],
        'updated_at': ['updatedAt'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('person_corporate_contracts.id'),
        nullable=False,
        unique=True
    )

    # 공유 항목 설정
    share_basic_info = db.Column(db.Boolean, default=True)
    share_contact = db.Column(db.Boolean, default=True)
    share_education = db.Column(db.Boolean, default=False)
    share_career = db.Column(db.Boolean, default=False)
    share_certificates = db.Column(db.Boolean, default=False)
    share_languages = db.Column(db.Boolean, default=False)
    share_military = db.Column(db.Boolean, default=False)

    # 실시간 동기화 설정
    is_realtime_sync = db.Column(db.Boolean, default=False)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DataSharingSettings contract_id={self.contract_id}>'


class SyncLog(DictSerializableMixin, db.Model):
    """동기화 이력 모델"""
    __tablename__ = 'sync_logs'

    # camelCase 매핑 (from_dict용)
    __dict_camel_mapping__ = {
        'contract_id': ['contractId'],
        'sync_type': ['syncType'],
        'entity_type': ['entityType'],
        'field_name': ['fieldName'],
        'old_value': ['oldValue'],
        'new_value': ['newValue'],
        'executed_by': ['executedBy'],
        'executed_at': ['executedAt'],
    }

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('person_corporate_contracts.id'),
        nullable=False,
        index=True
    )

    # 동기화 정보
    sync_type = db.Column(db.String(30), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    field_name = db.Column(db.String(100), nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    direction = db.Column(db.String(20), nullable=True)

    # 실행 정보
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 동기화 유형 상수
    SYNC_TYPE_AUTO = 'auto'
    SYNC_TYPE_MANUAL = 'manual'
    SYNC_TYPE_INITIAL = 'initial'

    def __repr__(self):
        return f'<SyncLog {self.id}: {self.sync_type} {self.entity_type}>'

    @classmethod
    def create_log(cls, contract_id, sync_type, entity_type, **kwargs):
        """동기화 로그 생성"""
        return cls(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type=entity_type,
            field_name=kwargs.get('field_name'),
            old_value=kwargs.get('old_value'),
            new_value=kwargs.get('new_value'),
            direction=kwargs.get('direction'),
            executed_by=kwargs.get('user_id'),
        )
