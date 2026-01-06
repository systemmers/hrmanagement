"""
Platform Blueprint (Compatibility Wrapper)

[DEPRECATED] 레거시 경로 호환성 유지용
권장: from app.domains.platform.blueprints import platform_bp

Phase 7: 도메인 중심 마이그레이션
"""

from app.domains.platform.blueprints import platform_bp

__all__ = ['platform_bp']
