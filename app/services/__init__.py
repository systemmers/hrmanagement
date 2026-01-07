"""
서비스 레이어

비즈니스 로직을 처리하는 서비스 모듈들

Phase 3: Employee 도메인 서비스는 app.domains.employee.services로 이동됨
Phase 8: 모든 도메인 서비스가 app.domains/로 마이그레이션됨
"""

# Shared Services (로컬 파일)
from .event_listeners import (
    SyncEventManager,
    ContractEventManager,
    init_event_listeners,
    cleanup_event_listeners
)
from .file_storage_service import (
    FileStorageService, file_storage,
    ALLOWED_EXTENSIONS, ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE, MAX_IMAGE_SIZE,
    CATEGORY_ATTACHMENT, CATEGORY_PROFILE_PHOTO,
    CATEGORY_BUSINESS_CARD_FRONT, CATEGORY_BUSINESS_CARD_BACK
)

# AI Services (shared domain)
from app.shared.services.ai_service import AIService

# Platform Domain Services
from app.domains.platform.services.audit_service import AuditService, AuditLog, audit_service, audit_log

# Sync Domain Services
from app.domains.sync.services.sync_service import SyncService
from app.domains.sync.services.termination_service import TerminationService, termination_service
from app.domains.sync.services import sync_service

# User Domain Services
from app.domains.user.services.notification_service import NotificationService, notification_service
from app.domains.user.services.personal_service import PersonalService, personal_service
from app.domains.user.services.corporate_admin_profile_service import CorporateAdminProfileService, corporate_admin_profile_service

# Contract Domain Services
from app.domains.contract.services.contract_service import ContractService
from app.domains.contract.services.contract_filter_service import ContractFilterService, contract_filter_service
from app.domains.contract.services import contract_service

# Employee Domain Services
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
    # Shared Services
    'SyncEventManager',
    'ContractEventManager',
    'init_event_listeners',
    'cleanup_event_listeners',
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
    # AI Services
    'AIService',
    # Platform Domain
    'AuditService',
    'AuditLog',
    'audit_service',
    'audit_log',
    # Sync Domain
    'SyncService',
    'sync_service',
    'TerminationService',
    'termination_service',
    # User Domain
    'NotificationService',
    'notification_service',
    'PersonalService',
    'personal_service',
    'CorporateAdminProfileService',
    'corporate_admin_profile_service',
    # Contract Domain
    'ContractService',
    'contract_service',
    'ContractFilterService',
    'contract_filter_service',
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
