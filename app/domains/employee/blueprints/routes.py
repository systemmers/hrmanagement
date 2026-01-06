"""
직원 관리 라우트

직원 CRUD 및 상세 정보 관련 라우트를 제공합니다.

Phase 7: 모듈 분할 - 기능별 하위 모듈로 분리
- list_routes.py: 목록 조회 라우트
- detail_routes.py: 상세/폼 조회 라우트
- mutation_routes.py: 데이터 변경 라우트 (생성/수정/삭제)

이 파일은 하위 호환성을 위해 모든 라우트를 통합 등록합니다.
"""
from flask import Blueprint

from .list_routes import register_list_routes
from .detail_routes import register_detail_routes
from .mutation_routes import register_mutation_routes


def register_routes(bp: Blueprint):
    """모든 CRUD 라우트를 Blueprint에 등록 (통합 진입점)"""
    register_list_routes(bp)
    register_detail_routes(bp)
    register_mutation_routes(bp)


# __all__ 정의
__all__ = [
    'register_routes',
    'register_list_routes',
    'register_detail_routes',
    'register_mutation_routes',
]
