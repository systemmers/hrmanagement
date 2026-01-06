"""
Authentication Blueprint (Compatibility Wrapper)

[DEPRECATED] Legacy path compatibility
Use the following for new code:
    from app.domains.user.blueprints import auth_bp

Phase 1 Migration: Moved to domain, this file is a compatibility wrapper
"""

# Re-export from domain (Phase 1 Migration)
from app.domains.user.blueprints import auth_bp

__all__ = ['auth_bp']
