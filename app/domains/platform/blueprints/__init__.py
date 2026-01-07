"""
Platform Domain Blueprints

플랫폼 마스터 관리자(Superadmin) 전용 Blueprint입니다.
법인 관리, 사용자 관리, 시스템 설정 등 플랫폼 전체 관리 기능을 제공합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Phase 9: main_bp, ai_test_bp, audit_bp 추가
"""
from flask import Blueprint

platform_bp = Blueprint('platform', __name__, url_prefix='/platform')

from . import dashboard, companies, users, settings

# Phase 9: 마이그레이션된 Blueprint
from .main import main_bp
from .ai_test import ai_test_bp
from .audit_api import audit_bp

__all__ = ['platform_bp', 'main_bp', 'ai_test_bp', 'audit_bp']
