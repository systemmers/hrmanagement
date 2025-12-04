"""
개인 프로필 모델 패키지

개인 계정의 프로필 및 이력 정보를 관리하는 모델입니다.
Phase 2: 개인-법인 분리 아키텍처의 일부입니다.

모듈 구조:
- profile.py: PersonalProfile (기본 프로필)
- education.py: PersonalEducation (학력)
- career.py: PersonalCareer (경력)
- certificate.py: PersonalCertificate (자격증)
- language.py: PersonalLanguage (어학)
- military_service.py: PersonalMilitaryService (병역)
"""
from .profile import PersonalProfile
from .education import PersonalEducation
from .career import PersonalCareer
from .certificate import PersonalCertificate
from .language import PersonalLanguage
from .military_service import PersonalMilitaryService

__all__ = [
    'PersonalProfile',
    'PersonalEducation',
    'PersonalCareer',
    'PersonalCertificate',
    'PersonalLanguage',
    'PersonalMilitaryService',
]
