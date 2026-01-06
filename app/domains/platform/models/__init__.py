"""
Platform Domain Models

Phase 7: 도메인 중심 마이그레이션 완료
모든 모델이 도메인에 직접 정의됨
"""

from .system_setting import SystemSetting
from .audit_log import AuditLog

__all__ = [
    'SystemSetting',
    'AuditLog',
]
