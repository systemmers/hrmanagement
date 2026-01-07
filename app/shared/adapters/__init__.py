"""
Profile Adapters - 프로필 데이터 모델 통합 어댑터

법인 직원(Employee), 개인 계정(PersonalProfile), 법인 관리자(CorporateAdminProfile)
데이터 모델의 차이를 추상화하여 통합 인터페이스 제공

사용법:
    from app.shared.adapters import create_profile_adapter

    # 자동 감지
    adapter = create_profile_adapter(employee)
    adapter = create_profile_adapter(profile)

    # 템플릿 컨텍스트 생성
    context = adapter.to_template_context(variable_name='employee')
"""
from app.shared.adapters.profile_adapter import (
    ProfileAdapter,
    EmployeeProfileAdapter,
    PersonalProfileAdapter,
    CorporateAdminProfileAdapter,
    create_profile_adapter
)

__all__ = [
    'ProfileAdapter',
    'EmployeeProfileAdapter',
    'PersonalProfileAdapter',
    'CorporateAdminProfileAdapter',
    'create_profile_adapter'
]
