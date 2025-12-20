"""
개인 프로필 모델 패키지

개인 계정의 기본 프로필 정보를 관리하는 모델입니다.
Phase 7: 이력 데이터는 통합 테이블(educations, careers 등)로 마이그레이션됨

모듈 구조:
- profile.py: PersonalProfile (기본 프로필, 회원가입용)

Note: 이력 데이터(학력, 경력, 자격증 등)는 통합 모델 사용
- app/models/education.py (Education)
- app/models/career.py (Career)
- app/models/certificate.py (Certificate)
- app/models/language.py (Language)
- app/models/military_service.py (MilitaryService)
- app/models/family_member.py (FamilyMember)
- app/models/award.py (Award)
- app/models/project_participation.py (ProjectParticipation)
"""
from .profile import PersonalProfile

__all__ = [
    'PersonalProfile',
]
