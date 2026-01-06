"""
CompanySettings SQLAlchemy 모델 (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.company.models import CompanySettings

Phase 2 Migration: 도메인으로 이동, 이 파일은 호환성 래퍼로 유지
"""

# 도메인에서 re-export (Phase 2 Migration)
from app.domains.company.models import CompanySettings

__all__ = ['CompanySettings']
