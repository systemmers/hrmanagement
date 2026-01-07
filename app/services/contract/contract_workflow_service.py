"""
Contract Workflow Service (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.domains.contract.services import ContractWorkflowService
"""
from app.domains.contract.services.contract_workflow_service import ContractWorkflowService

contract_workflow_service = ContractWorkflowService()

__all__ = ['ContractWorkflowService', 'contract_workflow_service']
