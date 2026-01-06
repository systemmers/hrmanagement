"""
Contract Domain

계약 관련 모든 기능을 포함합니다:
- Models: PersonCorporateContract, DataSharingSettings, SyncLog
- Repositories: PersonContractRepository
- Services: ContractCoreService, ContractWorkflowService, ContractSettingsService, ContractFilterService
- Blueprints: contracts_bp

Phase 4: 도메인 중심 마이그레이션
"""

# Repository 인스턴스 (지연 초기화)
_person_contract_repo = None


def init_repositories():
    """도메인 Repository 초기화

    extensions.py에서 호출됩니다.
    """
    global _person_contract_repo
    from .repositories import PersonContractRepository
    _person_contract_repo = PersonContractRepository()


def get_person_contract_repo():
    """PersonContractRepository 인스턴스 반환"""
    return _person_contract_repo


# 외부 인터페이스
__all__ = [
    # Functions
    'init_repositories',
    'get_person_contract_repo',
]
