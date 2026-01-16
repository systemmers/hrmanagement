"""
User Domain Blueprints

Phase 1 Migration: Domain-first architecture
All user-related blueprints are now in domain
Legacy paths re-export from here for backward compatibility
Phase 9: profile_bp 추가 (통합 프로필)
"""

# Auth blueprint
from .auth import auth_bp

# MyPage blueprint
from .mypage import mypage_bp

# Notifications API blueprint
from .notifications import notifications_bp

# Account management blueprint
from .account import account_bp

# Personal account blueprint
from .personal import personal_bp

# Phase 9: 마이그레이션된 Blueprint
from .profile import profile_bp

# Phase 1: 개인 계정 인라인 편집 API
from .profile.profile_section_api import profile_section_api_bp

__all__ = [
    'auth_bp',
    'mypage_bp',
    'notifications_bp',
    'account_bp',
    'personal_bp',
    'profile_bp',
    'profile_section_api_bp',
]
