"""
관리자 Blueprint 패키지

조직 관리, 시스템 설정 등 관리자 기능을 제공합니다.
"""
from flask import Blueprint

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')

# Import and register sub-modules
from . import organization
from . import audit  # Phase 5: 감사 대시보드
