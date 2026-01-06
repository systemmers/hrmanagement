"""
File Storage Service - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/shared/services/file_storage_service.py 에 위치
"""
from app.shared.services.file_storage_service import (
    FileStorageService,
    file_storage,
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
]
