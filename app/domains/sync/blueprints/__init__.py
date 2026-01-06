"""
Sync Domain Blueprints

동기화 API Blueprint 패키지
개인-법인 데이터 동기화 API를 제공합니다.

Phase 4: 데이터 동기화 및 퇴사 처리
Phase 7: 도메인 중심 마이그레이션 완료
Phase 8: 상수 모듈 적용
Phase 24: 트랜잭션 SSOT 적용
Phase 25: 패키지 분할
"""
from flask import Blueprint

sync_bp = Blueprint('sync', __name__, url_prefix='/api/sync')

# 라우트 등록
from app.domains.sync.blueprints import sync_routes
from app.domains.sync.blueprints import contract_routes
from app.domains.sync.blueprints import termination_routes

__all__ = ['sync_bp']
