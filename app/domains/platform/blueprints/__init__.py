"""
Platform Domain Blueprints

Phase 7: 도메인 중심 마이그레이션
기존 Blueprint를 re-export하여 점진적 마이그레이션 지원
"""

# 기존 Blueprint에서 re-export
from app.blueprints.platform import platform_bp

__all__ = [
    'platform_bp',
]
