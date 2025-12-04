"""
직원 관리 Blueprint 패키지

직원 CRUD, 파일 업로드, 관련 기능을 제공합니다.
모듈 구조:
- routes.py: CRUD 라우트 (목록, 상세, 생성, 수정, 삭제)
- files.py: 파일 업로드/다운로드 (첨부파일, 프로필 사진, 명함)
- helpers.py: 헬퍼 함수 (폼 처리, 데이터 업데이트 등)
"""
from flask import Blueprint

from .routes import register_routes
from .files import register_file_routes

# Blueprint 생성
employees_bp = Blueprint('employees', __name__)

# 라우트 등록
register_routes(employees_bp)
register_file_routes(employees_bp)

# 외부에서 사용할 수 있도록 export
__all__ = ['employees_bp']
