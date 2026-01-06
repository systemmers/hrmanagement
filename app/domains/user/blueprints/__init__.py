"""
User Domain Blueprints

Phase 6: 도메인 중심 마이그레이션
기존 Blueprint를 re-export하여 점진적 마이그레이션 지원
"""

# 기존 Blueprint에서 re-export
from app.blueprints.auth import auth_bp
from app.blueprints.mypage import mypage_bp
from app.blueprints.account import account_bp

__all__ = [
    'auth_bp',
    'mypage_bp',
    'account_bp',
]
