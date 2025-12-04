"""
AuditLog SQLAlchemy 모델

감사 로그 정보를 저장합니다.
Phase 6: 백엔드 리팩토링 - 모델 분리
"""
from datetime import datetime
import json
from typing import Dict

from app.database import db


class AuditLog(db.Model):
    """감사 로그 모델"""
    __tablename__ = 'audit_logs'

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

    def to_dict(self) -> Dict:
        """딕셔너리 변환"""
        return {
            'id': self.id,
            'user_id': self.user_id,
            'account_type': self.account_type,
            'company_id': self.company_id,
            'action': self.action,
            'resource_type': self.resource_type,
            'resource_id': self.resource_id,
            'details': json.loads(self.details) if self.details else None,
            'ip_address': self.ip_address,
            'user_agent': self.user_agent,
            'endpoint': self.endpoint,
            'method': self.method,
            'status': self.status,
            'error_message': self.error_message,
            'created_at': self.created_at.isoformat() if self.created_at else None,
        }

    def __repr__(self):
        return f'<AuditLog {self.id}: {self.action} {self.resource_type}>'
