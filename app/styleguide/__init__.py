"""
Styleguide Module
독립적인 스타일가이드 모듈 - Living Documentation

이 모듈은 프로젝트의 디자인 시스템을 문서화하고
실제 CSS 컴포넌트와 동기화된 라이브 프리뷰를 제공합니다.
"""
from flask import Blueprint

styleguide_bp = Blueprint(
    'styleguide',
    __name__,
    url_prefix='/styleguide'
)

from . import routes  # noqa: E402, F401
