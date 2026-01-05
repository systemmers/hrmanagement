"""
AuditLog SQLAlchemy 모델

감사 로그 정보를 저장합니다.
Phase 6: 백엔드 리팩토링 - 모델 분리
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from datetime import datetime
from app.database import db
from app.models.mixins import DictSerializableMixin


class AuditLog(DictSerializableMixin, db.Model):
    """감사 로그 모델"""
    __tablename__ = 'audit_logs'

    # JSON 필드 (자동 파싱)
    __dict_json_fields__ = ['details']

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 사용자 정보
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True, index=True)
    account_type = db.Column(db.String(20), nullable=True)
    company_id = db.Column(db.Integer, db.ForeignKey('companies.id'), nullable=True, index=True)

    # 접근 정보
    action = db.Column(db.String(50), nullable=False, index=True)
    resource_type = db.Column(db.String(50), nullable=False, index=True)
    resource_id = db.Column(db.Integer, nullable=True)

    # 세부 정보
    details = db.Column(db.Text, nullable=True)
    ip_address = db.Column(db.String(50), nullable=True)
    user_agent = db.Column(db.String(500), nullable=True)
    endpoint = db.Column(db.String(200), nullable=True)
    method = db.Column(db.String(10), nullable=True)

    # 결과
    status = db.Column(db.String(20), default='success')
    error_message = db.Column(db.Text, nullable=True)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    # 액션 상수
    ACTION_VIEW = 'view'
    ACTION_CREATE = 'create'
    ACTION_UPDATE = 'update'
    ACTION_DELETE = 'delete'
    ACTION_EXPORT = 'export'
    ACTION_SYNC = 'sync'
    ACTION_LOGIN = 'login'
    ACTION_LOGOUT = 'logout'
    ACTION_ACCESS_DENIED = 'access_denied'

    # 상태 상수
    STATUS_SUCCESS = 'success'
    STATUS_FAILURE = 'failure'
    STATUS_DENIED = 'denied'

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} {self.resource_type}>'
