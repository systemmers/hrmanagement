"""
PersonCorporateContract SQLAlchemy Model

개인-법인 간 계약 관계를 관리하는 모델입니다.
계약 요청, 승인/거절, 데이터 공유 설정 등을 처리합니다.

Phase 5: 구조화 - contract/ 폴더로 분리
Phase 2 Migration: app/domains/contract/models/로 이동
SSOT: FieldOptions.CONTRACT_TYPE 참조
"""
from datetime import datetime
from app.database import db
from app.shared.constants.field_options import FieldOptions
from app.shared.constants.status import ContractStatus


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
    cancellation_reason = db.Column(db.Text, nullable=True)
    termination_reason = db.Column(db.Text, nullable=True)

    # 타임스탬프
    requested_at = db.Column(db.DateTime, default=datetime.utcnow)
    approved_at = db.Column(db.DateTime, nullable=True)
    rejected_at = db.Column(db.DateTime, nullable=True)
    cancelled_at = db.Column(db.DateTime, nullable=True)
    terminated_at = db.Column(db.DateTime, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 승인/거절/취소/종료 처리자
    approved_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    cancelled_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    terminated_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 양측 동의 종료 요청 관련 필드 (Phase 5.3)
    termination_requested_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    termination_requested_at = db.Column(db.DateTime, nullable=True)
    termination_rejected_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    termination_rejected_at = db.Column(db.DateTime, nullable=True)
    termination_rejection_reason = db.Column(db.Text, nullable=True)

    # 상태 상수 (Deprecated: ContractStatus 사용 권장)
    # 하위 호환용 별칭 - SSOT는 app.constants.status.ContractStatus
    STATUS_REQUESTED = ContractStatus.REQUESTED
    STATUS_APPROVED = ContractStatus.APPROVED
    STATUS_REJECTED = ContractStatus.REJECTED
    STATUS_CANCELLED = ContractStatus.CANCELLED
    STATUS_TERMINATED = ContractStatus.TERMINATED
    STATUS_EXPIRED = ContractStatus.EXPIRED
    STATUS_TERMINATION_REQUESTED = ContractStatus.TERMINATION_REQUESTED

    # 계약 유형 상수 (하위 호환용)
    TYPE_EMPLOYMENT = 'employment'
    TYPE_CONTRACT = 'contract'
    TYPE_FREELANCE = 'freelance'
    TYPE_INTERN = 'intern'

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
            'contract_type_label': FieldOptions.get_label_with_legacy(
                FieldOptions.CONTRACT_TYPE, self.contract_type
            ),
            'contract_start_date': self.contract_start_date.isoformat() if self.contract_start_date else None,
            'contract_end_date': self.contract_end_date.isoformat() if self.contract_end_date else None,
            'position': self.position,
            'department': self.department,
            'employee_number': self.employee_number,
            'requested_by': self.requested_by,
            'notes': self.notes,
            'rejection_reason': self.rejection_reason,
            'cancellation_reason': self.cancellation_reason,
            'termination_reason': self.termination_reason,
            'requested_at': self.requested_at.isoformat() if self.requested_at else None,
            'approved_at': self.approved_at.isoformat() if self.approved_at else None,
            'rejected_at': self.rejected_at.isoformat() if self.rejected_at else None,
            'cancelled_at': self.cancelled_at.isoformat() if self.cancelled_at else None,
            'terminated_at': self.terminated_at.isoformat() if self.terminated_at else None,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'updated_at': self.updated_at.isoformat() if self.updated_at else None,
            # 양측 동의 종료 요청 관련 필드
            'termination_requested_by': self.termination_requested_by,
            'termination_requested_at': self.termination_requested_at.isoformat() if self.termination_requested_at else None,
            'termination_rejected_by': self.termination_rejected_by,
            'termination_rejected_at': self.termination_rejected_at.isoformat() if self.termination_rejected_at else None,
            'termination_rejection_reason': self.termination_rejection_reason,
        }

        if include_relations:
            if self.person_user:
                # 계정 유형별 이름/전화번호 조회
                # - 개인 계정 (personal): PersonalProfile (user_id로 연결)
                # - 직원 계정 (employee_sub): Employee (User.employee_id로 연결)
                from app.domains.user.models import PersonalProfile
                from app.domains.employee.models import Employee

                actual_name = None
                phone = None

                # 1. PersonalProfile (개인 계정) 조회
                personal_profile = PersonalProfile.query.filter_by(user_id=self.person_user.id).first()
                if personal_profile and personal_profile.name:
                    actual_name = personal_profile.name
                    phone = personal_profile.mobile_phone

                # 2. Employee (직원 계정) 조회 - User.employee_id 사용
                if not actual_name and self.person_user.employee_id:
                    employee = Employee.query.get(self.person_user.employee_id)
                    if employee and employee.name:
                        actual_name = employee.name
                        phone = employee.phone

                # 3. fallback
                if not actual_name:
                    actual_name = '이름 없음'

                data['person_name'] = actual_name
                data['username'] = self.person_user.username
                data['person_email'] = self.person_user.email
                data['person_phone'] = phone

                # 계정유형 레이블 (SSOT: User.get_account_type_label() 사용)
                data['account_type_label'] = self.person_user.get_account_type_label()

                # employee_id: User.employee_id 우선, 없으면 employee_number로 조회
                employee_id = self.person_user.employee_id
                if not employee_id and self.employee_number:
                    from app.domains.employee.models import Employee
                    emp = Employee.query.filter_by(
                        employee_number=self.employee_number
                    ).first()
                    if emp:
                        employee_id = emp.id
                data['employee_id'] = employee_id
            if self.company:
                data['company_name'] = self.company.name

        return data

    def approve(self, user_id=None):
        """
        계약 승인

        상태 전이 검증 포함 (Phase 30)
        유효한 전이: requested -> approved, termination_requested -> approved

        Args:
            user_id: 승인 처리 사용자 ID

        Raises:
            ValueError: 유효하지 않은 상태 전이
        """
        valid, msg = ContractStatus.validate_transition(self.status, ContractStatus.APPROVED)
        if not valid:
            raise ValueError(msg)

        self.status = self.STATUS_APPROVED
        self.approved_at = datetime.utcnow()
        self.approved_by = user_id
        self.updated_at = datetime.utcnow()

    def reject(self, user_id=None, reason=None):
        """
        계약 거절

        상태 전이 검증 포함 (Phase 30)
        유효한 전이: requested -> rejected

        Args:
            user_id: 거절 처리 사용자 ID
            reason: 거절 사유

        Raises:
            ValueError: 유효하지 않은 상태 전이
        """
        valid, msg = ContractStatus.validate_transition(self.status, ContractStatus.REJECTED)
        if not valid:
            raise ValueError(msg)

        self.status = self.STATUS_REJECTED
        self.rejected_at = datetime.utcnow()
        self.rejected_by = user_id
        self.rejection_reason = reason
        self.updated_at = datetime.utcnow()

    def cancel(self, user_id=None, reason=None):
        """
        계약 요청 취소 (요청자가 직접 취소)

        상태 전이 검증 포함
        유효한 전이: requested -> cancelled

        Args:
            user_id: 취소 처리 사용자 ID (요청자)
            reason: 취소 사유

        Raises:
            ValueError: 유효하지 않은 상태 전이
        """
        valid, msg = ContractStatus.validate_transition(self.status, ContractStatus.CANCELLED)
        if not valid:
            raise ValueError(msg)

        self.status = self.STATUS_CANCELLED
        self.cancelled_at = datetime.utcnow()
        self.cancelled_by = user_id
        self.cancellation_reason = reason
        self.updated_at = datetime.utcnow()

    def terminate(self, user_id=None, reason=None):
        """
        계약 종료

        상태 전이 검증 포함 (Phase 30)
        유효한 전이: approved -> terminated, termination_requested -> terminated

        Args:
            user_id: 종료 처리 사용자 ID
            reason: 종료 사유

        Raises:
            ValueError: 유효하지 않은 상태 전이
        """
        valid, msg = ContractStatus.validate_transition(self.status, ContractStatus.TERMINATED)
        if not valid:
            raise ValueError(msg)

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
