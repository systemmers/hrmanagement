"""
Contract Domain Repositories

개인-법인 계약 관리 Repository입니다.

사용법:
    from app.domains.contract.repositories import PersonContractRepository

Phase 4: 도메인 중심 마이그레이션
"""

from .person_contract_repository import PersonContractRepository

__all__ = [
    'PersonContractRepository',
]
