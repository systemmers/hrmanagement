"""
User Domain Blueprints

Phase 1 Migration: Domain-first architecture
All user-related blueprints are now in domain
Legacy paths re-export from here for backward compatibility
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

__all__ = [
    'auth_bp',
    'mypage_bp',
    'notifications_bp',
    'account_bp',
    'personal_bp',
]
