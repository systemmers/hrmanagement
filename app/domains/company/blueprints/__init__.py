"""
Company Domain Blueprints

Phase 5: 도메인 중심 마이그레이션
기존 Blueprint를 re-export하여 점진적 마이그레이션 지원
"""

# 기존 Blueprint에서 re-export
from app.blueprints.corporate import corporate_bp
from app.blueprints.corporate_settings import corporate_settings_api_bp

__all__ = [
    'corporate_bp',
    'corporate_settings_api_bp',
]
