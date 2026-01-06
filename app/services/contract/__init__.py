"""
Contract Service Package (Facade)

개인-법인 계약 관련 비즈니스 로직을 처리합니다.

기존 API 100% 호환성 유지:
    from app.services.contract_service import contract_service
    contract_service.approve_contract(id, user_id)

새로운 방식 (서브서비스 직접 사용):
    from app.services.contract import contract_core_service
    contract_core_service.get_contract_by_id(id)

Phase 2: 구조화 - contract/ 폴더로 분리 (Facade 패턴)
"""
from typing import Dict, Optional, List, Any

from .contract_core_service import ContractCoreService, contract_core_service
from .contract_workflow_service import ContractWorkflowService, contract_workflow_service
from .contract_settings_service import ContractSettingsService, contract_settings_service
from app.shared.base import ServiceResult


class ContractService:
    """계약 관리 서비스 - Facade

    기존 ContractService API 100% 유지하면서
    내부적으로 서브서비스에 위임합니다.
    """

    @property
    def _core(self) -> ContractCoreService:
        """Core 서비스 (조회)"""
        return contract_core_service

    @property
    def _workflow(self) -> ContractWorkflowService:
        """Workflow 서비스 (상태 변경)"""
        return contract_workflow_service

    @property
    def _settings(self) -> ContractSettingsService:
        """Settings 서비스 (공유 설정)"""
        return contract_settings_service

    # ========================================
    # 레거시 property 유지 (Repository 접근)
    # ========================================

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        return self._core.contract_repo

    @property
    def user_repo(self):
        """지연 초기화된 사용자 Repository"""
        from ...extensions import user_repo
        return user_repo

    # ========================================
    # Core Service 위임 (조회)
    # ========================================

    def get_personal_contracts(self, user_id: int) -> List[Dict]:
        return self._core.get_personal_contracts(user_id)

    def get_personal_pending_contracts(self, user_id: int) -> List[Dict]:
        return self._core.get_personal_pending_contracts(user_id)

    def get_personal_statistics(self, user_id: int) -> Dict:
        return self._core.get_personal_statistics(user_id)

    def get_company_contracts(self, company_id: int) -> List[Dict]:
        return self._core.get_company_contracts(company_id)

    def get_company_pending_contracts(self, company_id: int) -> List[Dict]:
        return self._core.get_company_pending_contracts(company_id)

    def get_company_statistics(self, company_id: int) -> Dict:
        return self._core.get_company_statistics(company_id)

    def search_contracts(self, company_id: int, status: str = None,
                         contract_type: str = None, search_term: str = None) -> List[Dict]:
        return self._core.search_contracts(company_id, status, contract_type, search_term)

    def get_contract_eligible_targets(self, company_id: int) -> Dict[str, List[Dict]]:
        return self._core.get_contract_eligible_targets(company_id)

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        return self._core.get_contract_by_id(contract_id)

    def get_contract_model_by_id(self, contract_id: int):
        return self._core.get_contract_model_by_id(contract_id)

    def find_contract_with_history(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        return self._core.find_contract_with_history(employee_number, company_id)

    def find_approved_contract(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        return self._core.find_approved_contract(employee_number, company_id)

    def get_employee_contract_status(
        self, employee_user_id: int, company_id: int
    ) -> Optional[str]:
        return self._core.get_employee_contract_status(employee_user_id, company_id)

    # ========================================
    # Workflow Service 위임 (상태 변경)
    # ========================================

    def create_contract_request(
        self,
        person_email: str,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> ServiceResult[Dict]:
        return self._workflow.create_contract_request(
            person_email, company_id, contract_type, position, department, notes
        )

    def create_employee_contract_request(
        self,
        employee_user_id: int,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> ServiceResult[Dict]:
        return self._workflow.create_employee_contract_request(
            employee_user_id, company_id, contract_type, position, department, notes
        )

    def approve_contract(self, contract_id: int, user_id: int) -> ServiceResult[Dict]:
        return self._workflow.approve_contract(contract_id, user_id)

    def reject_contract(self, contract_id: int, user_id: int, reason: str = None) -> ServiceResult[Dict]:
        return self._workflow.reject_contract(contract_id, user_id, reason)

    def terminate_contract(self, contract_id: int, user_id: int, reason: str = None) -> ServiceResult[Dict]:
        return self._workflow.terminate_contract(contract_id, user_id, reason)

    def request_termination(
        self, contract_id: int, requester_user_id: int, reason: str = None
    ) -> ServiceResult[Dict]:
        return self._workflow.request_termination(contract_id, requester_user_id, reason)

    def approve_termination(
        self, contract_id: int, approver_user_id: int
    ) -> ServiceResult[Dict]:
        return self._workflow.approve_termination(contract_id, approver_user_id)

    def reject_termination(
        self, contract_id: int, rejector_user_id: int, reason: str = None
    ) -> ServiceResult[Dict]:
        return self._workflow.reject_termination(contract_id, rejector_user_id, reason)

    def get_termination_pending_contracts(self, user_id: int) -> List[Dict]:
        return self._workflow.get_termination_pending_contracts(user_id)

    # ========================================
    # Settings Service 위임 (공유 설정)
    # ========================================

    def get_sharing_settings(self, contract_id: int) -> Dict:
        return self._settings.get_sharing_settings(contract_id)

    def get_sharing_settings_model(self, contract_id: int) -> Optional[Any]:
        return self._settings.get_sharing_settings_model(contract_id)

    def update_or_create_sharing_settings(
        self, contract_id: int, commit: bool = True, **kwargs
    ) -> Any:
        return self._settings.update_or_create_sharing_settings(contract_id, commit, **kwargs)

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> ServiceResult[Dict]:
        return self._settings.update_sharing_settings(contract_id, settings)

    def get_sync_logs_filtered(
        self, contract_id: int, sync_type: str = None, limit: int = 50
    ) -> List[Dict]:
        return self._settings.get_sync_logs_filtered(contract_id, sync_type, limit)

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        return self._settings.get_sync_logs(contract_id, limit)

    # ========================================
    # 내부 헬퍼 메서드 (Workflow에서 사용)
    # ========================================

    def _create_default_sharing_settings(self, contract_id: int):
        """기본 데이터 공유 설정 생성 (내부용)"""
        return self._workflow._create_default_sharing_settings(contract_id)


# 싱글톤 인스턴스
contract_service = ContractService()

__all__ = [
    'ContractService',
    'ContractCoreService',
    'ContractWorkflowService',
    'ContractSettingsService',
    'contract_service',
    'contract_core_service',
    'contract_workflow_service',
    'contract_settings_service',
]
