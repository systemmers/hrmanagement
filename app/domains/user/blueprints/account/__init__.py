"""
User Domain: Account Management Blueprint

Phase 1 Migration: domains/user/blueprints/account/
- Account settings, password change, privacy settings, account deletion
- Used by both personal and corporate employee accounts
"""
from flask import Blueprint

account_bp = Blueprint('account', __name__, url_prefix='/account')

from . import routes
