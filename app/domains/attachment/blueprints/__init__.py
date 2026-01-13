"""
Attachment 도메인 Blueprint

첨부파일 관리 API 엔드포인트를 제공합니다.

API 엔드포인트:
- /api/attachments/* - 첨부파일 CRUD
- /api/required-documents/* - 필수 서류 설정 (Phase 4.1)
"""
from flask import Blueprint

attachment_bp = Blueprint('attachments', __name__)

from . import routes  # noqa: F401, E402
from . import required_document_routes  # noqa: F401, E402
