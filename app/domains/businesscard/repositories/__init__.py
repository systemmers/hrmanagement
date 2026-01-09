"""
BusinessCard Repositories

명함 데이터 접근 계층을 제공합니다.
"""
from app.domains.businesscard.repositories.businesscard_repository import BusinessCardRepository

# 싱글톤 인스턴스 생성
businesscard_repository = BusinessCardRepository()

__all__ = [
    'BusinessCardRepository',
    'businesscard_repository',
]
