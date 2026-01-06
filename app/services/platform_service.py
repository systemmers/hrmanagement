"""
Platform Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/platform/services/platform_service.py 에 위치
"""
from app.domains.platform.services.platform_service import (
    PlatformService,
    platform_service,
)

__all__ = [
    'PlatformService',
    'platform_service',
]
