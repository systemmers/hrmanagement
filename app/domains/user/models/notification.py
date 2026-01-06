"""
알림 모델

Phase 5: 알림 시스템
- 계약 요청/승인/거절 알림
- 동기화 완료 알림
- 퇴사 처리 알림
- 시스템 알림
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
Phase 2 Migration: 도메인으로 이동
"""
from datetime import datetime
from app.database import db
from app.domains.employee.models import DictSerializableMixin


class Notification(DictSerializableMixin, db.Model):
    """
    알림 모델

    사용자에게 전송되는 모든 알림을 저장합니다.
    """
    __tablename__ = 'notifications'

    # JSON 필드 (자동 파싱)
    __dict_json_fields__ = ['extra_data']

    # ===== 알림 유형 상수 =====
    TYPE_CONTRACT_REQUEST = 'contract_request'      # 계약 요청 받음
    TYPE_CONTRACT_APPROVED = 'contract_approved'    # 계약 승인됨
    TYPE_CONTRACT_REJECTED = 'contract_rejected'    # 계약 거절됨
    TYPE_CONTRACT_TERMINATED = 'contract_terminated'  # 계약 종료됨
    TYPE_SYNC_COMPLETED = 'sync_completed'          # 동기화 완료
    TYPE_SYNC_FAILED = 'sync_failed'                # 동기화 실패
    TYPE_TERMINATION_PROCESSED = 'termination_processed'  # 퇴사 처리 완료
    TYPE_DATA_UPDATED = 'data_updated'              # 데이터 업데이트
    TYPE_SYSTEM = 'system'                          # 시스템 알림
    TYPE_INFO = 'info'                              # 일반 정보
    TYPE_WARNING = 'warning'                        # 경고

    # 알림 유형 선택지
    NOTIFICATION_TYPES = [
        (TYPE_CONTRACT_REQUEST, '계약 요청'),
        (TYPE_CONTRACT_APPROVED, '계약 승인'),
        (TYPE_CONTRACT_REJECTED, '계약 거절'),
        (TYPE_CONTRACT_TERMINATED, '계약 종료'),
        (TYPE_SYNC_COMPLETED, '동기화 완료'),
        (TYPE_SYNC_FAILED, '동기화 실패'),
        (TYPE_TERMINATION_PROCESSED, '퇴사 처리'),
        (TYPE_DATA_UPDATED, '데이터 업데이트'),
        (TYPE_SYSTEM, '시스템'),
        (TYPE_INFO, '정보'),
        (TYPE_WARNING, '경고'),
    ]

    # ===== 우선순위 상수 =====
    PRIORITY_LOW = 'low'
    PRIORITY_NORMAL = 'normal'
    PRIORITY_HIGH = 'high'
    PRIORITY_URGENT = 'urgent'

    PRIORITY_CHOICES = [
        (PRIORITY_LOW, '낮음'),
        (PRIORITY_NORMAL, '보통'),
        (PRIORITY_HIGH, '높음'),
        (PRIORITY_URGENT, '긴급'),
    ]

    # ===== 컬럼 정의 =====
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 수신자 정보
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, index=True)

    # 알림 내용
    notification_type = db.Column(db.String(50), nullable=False, index=True)
    title = db.Column(db.String(200), nullable=False)
    message = db.Column(db.Text, nullable=True)

    # 관련 리소스 (선택)
    resource_type = db.Column(db.String(50), nullable=True)  # contract, employee, sync 등
    resource_id = db.Column(db.Integer, nullable=True)

    # 발신자 정보 (선택)
    sender_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    # 상태
    is_read = db.Column(db.Boolean, default=False, nullable=False, index=True)
    read_at = db.Column(db.DateTime, nullable=True)

    # 우선순위
    priority = db.Column(db.String(20), default=PRIORITY_NORMAL, nullable=False)

    # 액션 링크 (선택)
    action_url = db.Column(db.String(500), nullable=True)
    action_label = db.Column(db.String(100), nullable=True)

    # 추가 데이터 (JSON)
    extra_data = db.Column(db.Text, nullable=True)  # JSON 형태로 저장

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)
    expires_at = db.Column(db.DateTime, nullable=True)  # 만료 시간 (선택)

    # ===== 관계 =====
    user = db.relationship('User', foreign_keys=[user_id], backref='notifications')
    sender = db.relationship('User', foreign_keys=[sender_id])

    def __repr__(self):
        return f'<Notification {self.id}: {self.notification_type} to User {self.user_id}>'

    def mark_as_read(self):
        """알림을 읽음으로 표시"""
        if not self.is_read:
            self.is_read = True
            self.read_at = datetime.utcnow()

    @classmethod
    def get_type_label(cls, notification_type):
        """알림 유형 라벨 조회"""
        for type_value, label in cls.NOTIFICATION_TYPES:
            if type_value == notification_type:
                return label
        return notification_type

    @classmethod
    def get_priority_label(cls, priority):
        """우선순위 라벨 조회"""
        for priority_value, label in cls.PRIORITY_CHOICES:
            if priority_value == priority:
                return label
        return priority


class NotificationPreference(DictSerializableMixin, db.Model):
    """
    알림 설정 모델

    사용자별 알림 수신 설정을 저장합니다.
    """
    __tablename__ = 'notification_preferences'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False, unique=True)

    # 알림 유형별 수신 설정
    receive_contract_notifications = db.Column(db.Boolean, default=True)
    receive_sync_notifications = db.Column(db.Boolean, default=True)
    receive_termination_notifications = db.Column(db.Boolean, default=True)
    receive_system_notifications = db.Column(db.Boolean, default=True)

    # 이메일 알림 설정
    email_notifications_enabled = db.Column(db.Boolean, default=False)
    email_digest_frequency = db.Column(db.String(20), default='none')  # none, daily, weekly

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    # 관계
    user = db.relationship('User', backref=db.backref('notification_preference', uselist=False))

    def __repr__(self):
        return f'<NotificationPreference for User {self.user_id}>'
