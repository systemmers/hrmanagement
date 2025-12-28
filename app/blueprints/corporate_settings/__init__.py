"""
법인 세팅 API Blueprint 패키지

법인별 조직구조, 패턴규칙, 노출설정 API를 제공합니다.
Phase 2: Service 계층 표준화
Phase 25: 패키지 분할 (2025-12-29)
"""
from flask import Blueprint

corporate_settings_api_bp = Blueprint(
    'corporate_settings_api', __name__, url_prefix='/api/corporate'
)

# 라우트 등록
from app.blueprints.corporate_settings import classifications_api
from app.blueprints.corporate_settings import settings_api
from app.blueprints.corporate_settings import number_categories_api
from app.blueprints.corporate_settings import visibility_api
from app.blueprints.corporate_settings import documents_api
