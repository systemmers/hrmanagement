"""
BusinessCard Models

명함 도메인은 신규 모델을 생성하지 않고,
employee 도메인의 Attachment 모델을 재사용합니다.

Attachment 모델의 category 필드를 사용하여 명함을 구분합니다:
- business_card_front: 명함 앞면
- business_card_back: 명함 뒷면
"""

# Attachment 모델 참조 (employee 도메인에서 import)
from app.domains.employee.models import Attachment

__all__ = ['Attachment']
