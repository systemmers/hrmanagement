"""
BusinessCard Blueprints

명함 API Blueprint를 정의합니다.

URL Prefix: /api/businesscard
"""
from flask import Blueprint

from app.extensions import csrf

# Blueprint 정의
businesscard_bp = Blueprint(
    'businesscard',
    __name__,
    url_prefix='/api/businesscard'
)

# API Blueprint는 CSRF 보호 면제 (세션 기반 인증 사용)
csrf.exempt(businesscard_bp)

# Routes 등록
from app.domains.businesscard.blueprints import routes

__all__ = ['businesscard_bp']
