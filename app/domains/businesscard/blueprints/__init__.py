"""
BusinessCard Blueprints

명함 API Blueprint를 정의합니다.

URL Prefix: /api/businesscard
"""
from flask import Blueprint

# Blueprint 정의
businesscard_bp = Blueprint(
    'businesscard',
    __name__,
    url_prefix='/api/businesscard'
)

# Routes 등록
from app.domains.businesscard.blueprints import routes

__all__ = ['businesscard_bp']
