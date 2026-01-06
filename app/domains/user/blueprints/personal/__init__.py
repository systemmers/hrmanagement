"""
User Domain: Personal Account Blueprint Package

Phase 1 Migration: domains/user/blueprints/personal/
- Personal registration, profile management, personal dashboard

Module structure:
- routes.py: Route definitions (SRP applied)
- form_extractors.py: Form data extraction (FieldRegistry based, SSOT)
- relation_updaters.py: Relation data updates (DRY principle)
"""
from flask import Blueprint

from .routes import register_routes

# Create Blueprint
personal_bp = Blueprint('personal', __name__, url_prefix='/personal')

# Register routes
register_routes(personal_bp)

# Export
__all__ = ['personal_bp']
