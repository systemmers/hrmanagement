"""
Sync Blueprint (Compatibility Wrapper)

[DEPRECATED] 레거시 경로 호환성 유지용
권장: from app.domains.sync.blueprints import sync_bp

Phase 7: 도메인 중심 마이그레이션
"""

from app.domains.sync.blueprints import sync_bp

__all__ = ['sync_bp']
