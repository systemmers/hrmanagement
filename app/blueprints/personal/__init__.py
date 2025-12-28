"""
개인 계정 Blueprint 패키지

개인 회원가입, 프로필 관리, 개인 대시보드를 처리합니다.
Phase 2: 개인-법인 분리 아키텍처

모듈 구조:
- routes.py: 라우트 정의 (SRP 적용)
- form_extractors.py: 폼 데이터 추출 (FieldRegistry 기반, SSOT)
- relation_updaters.py: 관계형 데이터 업데이트 (DRY 원칙)
"""
from flask import Blueprint

from .routes import register_routes

# Blueprint 생성
personal_bp = Blueprint('personal', __name__, url_prefix='/personal')

# 라우트 등록
register_routes(personal_bp)

# 외부에서 사용할 수 있도록 export
__all__ = ['personal_bp']
