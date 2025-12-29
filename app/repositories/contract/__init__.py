"""
Contract Repositories Package

개인-법인 계약 관련 Repository 모듈입니다.

Phase 3 구조화: repositories/contract/ 폴더로 분리
기존 import 경로 100% 호환:
    from app.repositories.person_contract_repository import PersonContractRepository
"""
from .person_contract_repository import PersonContractRepository

__all__ = ['PersonContractRepository']
