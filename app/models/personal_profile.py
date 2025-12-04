"""
PersonalProfile 모델 - 호환성 유지용 re-export

이 파일은 기존 import 경로와의 호환성을 위해 유지됩니다.
새 코드는 app.models.personal 패키지에서 직접 import하세요.

예시:
    # 기존 방식 (호환성 유지)
    from app.models.personal_profile import PersonalProfile

    # 권장 방식 (새 패키지)
    from app.models.personal import PersonalProfile
"""
from .personal import (
    PersonalProfile,
    PersonalEducation,
    PersonalCareer,
    PersonalCertificate,
    PersonalLanguage,
    PersonalMilitaryService,
)

__all__ = [
    'PersonalProfile',
    'PersonalEducation',
    'PersonalCareer',
    'PersonalCertificate',
    'PersonalLanguage',
    'PersonalMilitaryService',
]
