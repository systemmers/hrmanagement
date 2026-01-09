"""
BusinessCard Domain

명함 관리 기능을 제공하는 도메인입니다.

Features:
- 명함 이미지 업로드 (앞면/뒷면)
- 명함 이미지 조회
- 명함 이미지 삭제

External Interface:
- businesscard_service: 명함 비즈니스 로직
- businesscard_bp: Flask Blueprint

Usage:
    from app.domains.businesscard import businesscard_service, businesscard_bp

    # 명함 조회
    result = businesscard_service.get_business_cards(employee_id)

    # 명함 업로드
    result = businesscard_service.upload_business_card(employee_id, file, 'front')

    # 명함 삭제
    result = businesscard_service.delete_business_card(employee_id, 'front')
"""

# Services
from app.domains.businesscard.services import businesscard_service

# Blueprints
from app.domains.businesscard.blueprints import businesscard_bp

# Repositories (내부 사용)
from app.domains.businesscard.repositories import businesscard_repository

__all__ = [
    # Services
    'businesscard_service',

    # Blueprints
    'businesscard_bp',

    # Repositories (내부 사용)
    'businesscard_repository',
]
