"""
PersonalProfile 모델 - 호환성 유지용 re-export

이 파일은 기존 import 경로와의 호환성을 위해 유지됩니다.
새 코드는 app.models.personal 패키지에서 직접 import하세요.

Phase 7: 이력 모델들은 통합 테이블로 마이그레이션됨
- Education, Career, Certificate, Language, MilitaryService 등 사용

예시:
    # 기존 방식 (호환성 유지)
    from app.models.personal_profile import PersonalProfile

    # 권장 방식 (새 패키지)
    from app.models.personal import PersonalProfile
"""
from .personal import PersonalProfile

__all__ = [
    'PersonalProfile',
]
