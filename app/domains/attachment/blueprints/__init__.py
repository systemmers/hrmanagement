"""
Attachment 도메인 Blueprint

첨부파일 관리 API 엔드포인트를 제공합니다.
"""
from flask import Blueprint

attachment_bp = Blueprint('attachments', __name__)

from . import routes  # noqa: F401, E402
