"""
Attachment Repository 패키지
"""
from .attachment_repository import AttachmentRepository
from .required_document_repository import RequiredDocumentRepository, required_document_repository

# 싱글톤 인스턴스
attachment_repository = AttachmentRepository()

__all__ = [
    'AttachmentRepository',
    'attachment_repository',
    'RequiredDocumentRepository',
    'required_document_repository'
]
