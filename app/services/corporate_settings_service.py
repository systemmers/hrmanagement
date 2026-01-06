"""
Corporate Settings Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/services/corporate_settings_service.py 에 위치
"""
from app.domains.company.services.corporate_settings_service import (
    CorporateSettingsService,
    corporate_settings_service,
)

__all__ = [
    'CorporateSettingsService',
    'corporate_settings_service',
]
