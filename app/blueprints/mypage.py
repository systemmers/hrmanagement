"""
MyPage Blueprint (Compatibility Wrapper)

[DEPRECATED] Legacy path compatibility
Use the following for new code:
    from app.domains.user.blueprints import mypage_bp

Phase 1 Migration: Moved to domain, this file is a compatibility wrapper
"""

# Re-export from domain (Phase 1 Migration)
from app.domains.user.blueprints import mypage_bp

__all__ = ['mypage_bp']
