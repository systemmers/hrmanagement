"""
Platform Domain Blueprints

플랫폼 마스터 관리자(Superadmin) 전용 Blueprint입니다.
법인 관리, 사용자 관리, 시스템 설정 등 플랫폼 전체 관리 기능을 제공합니다.

Phase 7: 도메인 중심 마이그레이션 완료
"""
from flask import Blueprint

platform_bp = Blueprint('platform', __name__, url_prefix='/platform')

from . import dashboard, companies, users, settings

__all__ = ['platform_bp']
