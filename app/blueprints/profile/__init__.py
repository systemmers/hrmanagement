"""
Profile Blueprint - 통합 프로필 블루프린트

법인 직원과 개인 계정의 프로필을 통합 관리하는 블루프린트
"""
from flask import Blueprint

profile_bp = Blueprint('profile', __name__, url_prefix='/profile')

from app.blueprints.profile import routes  # noqa: E402, F401
