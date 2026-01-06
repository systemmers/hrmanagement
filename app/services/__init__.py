"""
서비스 레이어

비즈니스 로직을 처리하는 서비스 모듈들

Phase 3: Employee 도메인 서비스는 app.domains.employee.services로 이동됨
"""

from .ai_service import AIService
from .sync_service import SyncService, sync_service
from .termination_service import TerminationService, termination_service
from .audit_service import AuditService, AuditLog, audit_service, audit_log
from .event_listeners import (
    SyncEventManager,
    ContractEventManager,
    init_event_listeners,
    cleanup_event_listeners
)
from .notification_service import NotificationService, notification_service
from .personal_service import PersonalService, personal_service
from .corporate_admin_profile_service import CorporateAdminProfileService, corporate_admin_profile_service
from .contract_service import ContractService, contract_service
from .contract_filter_service import ContractFilterService, contract_filter_service
from .file_storage_service import (
    FileStorageService, file_storage,
    ALLOWED_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE, MAX_IMAGE_SIZE,
    CATEGORY_ATTACHMENT, CATEGORY_PROFILE_PHOTO,
    CATEGORY_BUSINESS_CARD_FRONT, CATEGORY_BUSINESS_CARD_BACK
)

# Employee Domain Services (새 위치)
from app.domains.employee.services import (
    EmployeeService,
    EmployeeCoreService, employee_core_service,
    EmployeeRelationService, employee_relation_service,
)
from app.domains.employee.services.employee_account_service import EmployeeAccountService, employee_account_service
from app.domains.employee.services.profile_relation_service import ProfileRelationService, profile_relation_service
from app.domains.employee.services.attachment_service import AttachmentService, attachment_service

# Legacy singleton
employee_service = EmployeeService()


__all__ = [
    'AIService',
    'SyncService',
    'sync_service',
    'TerminationService',
    'termination_service',
    'AuditService',
    'AuditLog',
    'audit_service',
    'audit_log',
    'SyncEventManager',
    'ContractEventManager',
    'init_event_listeners',
    'cleanup_event_listeners',
    'NotificationService',
    'notification_service',
    'PersonalService',
    'personal_service',
    'CorporateAdminProfileService',
    'corporate_admin_profile_service',
    'ContractService',
    'contract_service',
    'ContractFilterService',
    'contract_filter_service',
    'FileStorageService',
    'file_storage',
    'ALLOWED_EXTENSIONS',
    'ALLOWED_IMAGE_EXTENSIONS',
    'MAX_FILE_SIZE',
    'MAX_IMAGE_SIZE',
    'CATEGORY_ATTACHMENT',
    'CATEGORY_PROFILE_PHOTO',
    'CATEGORY_BUSINESS_CARD_FRONT',
    'CATEGORY_BUSINESS_CARD_BACK',
    # Employee Domain
    'EmployeeService',
    'employee_service',
    'EmployeeCoreService',
    'employee_core_service',
    'EmployeeRelationService',
    'employee_relation_service',
    'EmployeeAccountService',
    'employee_account_service',
    'ProfileRelationService',
    'profile_relation_service',
    'AttachmentService',
    'attachment_service',
]
