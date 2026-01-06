"""
Company Settings Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/company/repositories/company_settings_repository.py 에 위치
"""
from app.domains.company.repositories.company_settings_repository import (
    CompanySettingsRepository,
    company_settings_repository,
)

__all__ = [
    'CompanySettingsRepository',
    'company_settings_repository',
]
