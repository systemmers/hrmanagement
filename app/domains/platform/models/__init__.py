"""
Platform Domain Models

Phase 7: 도메인 중심 마이그레이션
기존 모델을 re-export하여 점진적 마이그레이션 지원
"""

# 기존 모델에서 re-export (중복 정의 방지)
from app.models.system_setting import SystemSetting

__all__ = [
    'SystemSetting',
]
