"""
Shared Services

도메인에 종속되지 않는 공통 서비스들
- AI 서비스 (문서 분석)
- 파일 스토리지 서비스
- 이벤트 리스너
- Validation 서비스

Phase 7: 도메인 중심 마이그레이션 완료
Phase 9: Validation 서비스 추가
"""

from .ai_service import AIService
from .file_storage_service import FileStorageService, file_storage
from .event_listeners import (
    SyncEventManager,
    ContractEventManager,
    init_event_listeners,
    cleanup_event_listeners,
    get_model_changes,
    track_field_changes,
)
from .validation import (
    ProfileBasicInfoValidator,
    ValidationResult,
    ValidationError,
    validate_profile_basic_info,
)

# 상수들도 export
from .file_storage_service import (
    ALLOWED_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE,
    CATEGORY_ATTACHMENT,
    CATEGORY_PROFILE_PHOTO,
    CATEGORY_BUSINESS_CARD_FRONT,
    CATEGORY_BUSINESS_CARD_BACK,
    CATEGORY_COMPANY_DOCUMENT,
    CATEGORY_ADMIN_PHOTO,
    ALLOWED_DOCUMENT_EXTENSIONS,
)

__all__ = [
    # AI Service
    'AIService',
    # File Storage
    'FileStorageService',
    'file_storage',
    'ALLOWED_EXTENSIONS',
    'ALLOWED_IMAGE_EXTENSIONS',
    'MAX_FILE_SIZE',
    'MAX_IMAGE_SIZE',
    'CATEGORY_ATTACHMENT',
    'CATEGORY_PROFILE_PHOTO',
    'CATEGORY_BUSINESS_CARD_FRONT',
    'CATEGORY_BUSINESS_CARD_BACK',
    'CATEGORY_COMPANY_DOCUMENT',
    'CATEGORY_ADMIN_PHOTO',
    'ALLOWED_DOCUMENT_EXTENSIONS',
    # Event Listeners
    'SyncEventManager',
    'ContractEventManager',
    'init_event_listeners',
    'cleanup_event_listeners',
    'get_model_changes',
    'track_field_changes',
    # Validation
    'ProfileBasicInfoValidator',
    'ValidationResult',
    'ValidationError',
    'validate_profile_basic_info',
]
