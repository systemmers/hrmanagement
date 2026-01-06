"""
System Configuration Constants

시스템 설정 상수 (설정값만, 메시지 제외)
Phase 23: 클린업 - 하드코딩 값 중앙화
"""


class FileConfig:
    """파일 업로드 설정"""
    MAX_FILE_SIZE_MB = 10
    MAX_IMAGE_SIZE_MB = 5
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    MAX_IMAGE_SIZE_BYTES = MAX_IMAGE_SIZE_MB * 1024 * 1024

    ALLOWED_IMAGE_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'docx', 'xlsx', 'pptx', 'doc', 'xls', 'ppt'}
    ALLOWED_ALL_EXTENSIONS = ALLOWED_IMAGE_EXTENSIONS | ALLOWED_DOCUMENT_EXTENSIONS


class PaginationConfig:
    """페이지네이션 설정"""
    DEFAULT_PAGE_SIZE = 20
    MAX_PAGE_SIZE = 100


class SessionConfig:
    """세션 설정"""
    SESSION_LIFETIME_DAYS = 7
