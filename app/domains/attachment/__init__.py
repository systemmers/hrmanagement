"""
Attachment 도메인 - 범용 첨부파일 관리

Phase 31: employee 도메인에서 분리된 독립 도메인
"""
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from .repositories import AttachmentRepository

# 지연 초기화 전역 변수
_attachment_repo = None


def init_repositories():
    """Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _attachment_repo
    from .repositories import AttachmentRepository
    _attachment_repo = AttachmentRepository()


def get_attachment_repo() -> 'AttachmentRepository':
    """Attachment Repository 인스턴스 반환"""
    global _attachment_repo
    if _attachment_repo is None:
        init_repositories()
    return _attachment_repo


# 편의성 export
from .models import Attachment
from .services import attachment_service
from .constants import AttachmentCategory, OwnerType

__all__ = [
    # 초기화
    'init_repositories',
    'get_attachment_repo',
    # 모델
    'Attachment',
    # 서비스
    'attachment_service',
    # 상수
    'AttachmentCategory',
    'OwnerType',
]
