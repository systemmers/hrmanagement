"""
Company Domain Blueprints

Phase 2 Migration: 도메인 내부에서 Blueprint 정의
기존 경로(app.blueprints.corporate, app.blueprints.corporate_settings)에서도 import 가능
"""

# 도메인 내부에서 import
from .corporate import corporate_bp
from .settings import corporate_settings_api_bp

__all__ = [
    'corporate_bp',
    'corporate_settings_api_bp',
]
