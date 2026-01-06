"""
AuditLog Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/platform/repositories/audit_log_repository.py 에 위치
"""
from app.domains.platform.repositories.audit_log_repository import (
    AuditLogRepository,
    audit_log_repository,
)

__all__ = [
    'AuditLogRepository',
    'audit_log_repository',
]
