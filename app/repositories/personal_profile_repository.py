"""
PersonalProfile Repository - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/domains/user/repositories/personal_profile_repository.py 에 위치

하위 호환성을 위해 기존 import 경로를 유지합니다.
"""

# 도메인에서 re-export
from app.domains.user.repositories.personal_profile_repository import (
    PersonalProfileRepository,
    personal_profile_repository,
)

__all__ = [
    'PersonalProfileRepository',
    'personal_profile_repository',
]
