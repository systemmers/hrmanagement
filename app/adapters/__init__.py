"""
Profile Adapters - 프로필 데이터 모델 통합 어댑터

법인 직원(Employee)과 개인 계정(PersonalProfile) 데이터 모델의
차이를 추상화하여 통합 인터페이스 제공
"""
from app.adapters.profile_adapter import (
    ProfileAdapter,
    EmployeeProfileAdapter,
    PersonalProfileAdapter
)

__all__ = [
    'ProfileAdapter',
    'EmployeeProfileAdapter',
    'PersonalProfileAdapter'
]
