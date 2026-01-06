"""
Constants Module

애플리케이션 전역 상수 정의
"""
from .session_keys import SessionKeys, AccountType, UserRole
from .messages import FlashMessages, ErrorMessages
from .field_registry import (
    FieldRegistry,
    FieldDefinition,
    SectionDefinition,
    FieldType,
    Visibility,
)
from .field_options import FieldOptions
from .system_config import FileConfig, PaginationConfig, SessionConfig
from .status import ContractStatus, EmployeeStatus, AccountStatus
from .sync_fields import (
    SyncFieldMapping,
    SYNC_MAPPINGS,
    BASIC_FIELD_MAPPING,
    CONTACT_FIELD_MAPPING,
    EXTRA_FIELD_MAPPING,
    RELATION_FIELD_MAPPING,
    SHARING_FIELD_GROUPS,
    SYNCABLE_RELATION_TYPES,
)

__all__ = [
    'SessionKeys',
    'AccountType',
    'UserRole',
    'FlashMessages',
    'ErrorMessages',
    # Field Registry
    'FieldRegistry',
    'FieldDefinition',
    'SectionDefinition',
    'FieldType',
    'Visibility',
    # Field Options (SSOT)
    'FieldOptions',
    # System Config
    'FileConfig',
    'PaginationConfig',
    'SessionConfig',
    # Status Constants (SSOT)
    'ContractStatus',
    'EmployeeStatus',
    'AccountStatus',
    # Sync Field Mappings (SSOT)
    'SyncFieldMapping',
    'SYNC_MAPPINGS',
    'BASIC_FIELD_MAPPING',
    'CONTACT_FIELD_MAPPING',
    'EXTRA_FIELD_MAPPING',
    'RELATION_FIELD_MAPPING',
    'SHARING_FIELD_GROUPS',
    'SYNCABLE_RELATION_TYPES',
]
