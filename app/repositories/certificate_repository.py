"""
Certificate Repository

자격증 데이터의 CRUD 기능을 제공합니다.
"""
from app.models import Certificate
from .base_repository import BaseRelationRepository


class CertificateRepository(BaseRelationRepository[Certificate]):
    """자격증 저장소"""

    def __init__(self):
        super().__init__(Certificate)
