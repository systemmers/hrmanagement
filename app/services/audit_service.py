"""
Audit Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/platform/services/audit_service.py 에 위치
"""
from app.domains.platform.services.audit_service import (
    AuditService,
    audit_service,
    audit_log,
)
# 하위 호환성: AuditLog 모델도 함께 re-export
from app.models.audit_log import AuditLog

__all__ = [
    'AuditService',
    'AuditLog',
    'audit_service',
    'audit_log',
]
