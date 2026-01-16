"""
Profile Blueprint - 통합 프로필 블루프린트

법인 직원과 개인 계정의 프로필을 통합 관리하는 블루프린트
Phase 9: 도메인 마이그레이션 - app/domains/user/blueprints/profile/로 이동
Phase 1: 개인 계정 인라인 편집 API 추가 (profile_section_api)
"""
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

from app.domains.user.blueprints.profile import routes  # noqa: E402, F401
from app.domains.user.blueprints.profile.profile_section_api import profile_section_api_bp  # noqa: E402, F401
