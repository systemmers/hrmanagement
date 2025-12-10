"""
도메인별 모델 패키지

기존 app.models에서 도메인별로 모델을 그룹화합니다.
기존 import 문은 그대로 작동합니다: from app.models import User
도메인별 import도 가능합니다: from app.models.domains.user import User
"""
from . import user
from . import organization
from . import employee
from . import hr
from . import contract
from . import asset
from . import system
from . import personal

__all__ = [
    'user',
    'organization',
    'employee',
    'hr',
    'contract',
    'asset',
    'system',
    'personal',
]
