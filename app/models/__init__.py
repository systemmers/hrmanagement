"""
SQLAlchemy 모델 패키지

모든 데이터베이스 모델을 정의하고 export합니다.

Phase 3: Employee 도메인 모델은 app.domains.employee.models로 이동됨
"""
# Employee Domain Models (새 위치)
from app.domains.employee.models import (
    # Mixins
    DictSerializableMixin,
    TimestampMixin,
    SoftDeleteMixin,
    # Core
    Employee,
    Profile,
    # 1:N Relations
    Education,
    Career,
    Certificate,
    FamilyMember,
    Language,
    SalaryHistory,
    Promotion,
    Evaluation,
    Training,
    Attendance,
    HrProject,
    ProjectParticipation,
    Award,
    Asset,
    SalaryPayment,
    Attachment,
    # 1:1 Relations
    MilitaryService,
    Salary,
    Benefit,
    Contract,
    Insurance,
)

# Company Domain Models (추후 이동 예정)
from .classification_option import ClassificationOption
from .company import Company
from .organization import Organization
from .company_settings import CompanySettings
from .company_document import CompanyDocument
from .company_visibility_settings import CompanyVisibilitySettings
from .number_category import NumberCategory
from .number_registry import NumberRegistry
from .ip_range import IpRange
from .ip_assignment import IpAssignment

# User Domain Models (추후 이동 예정)
from .user import User
from .corporate_admin_profile import CorporateAdminProfile
from .notification import Notification, NotificationPreference

# Contract Domain Models (추후 이동 예정)
from .person_contract import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog
)

# Platform Domain Models (추후 이동 예정)
from .system_setting import SystemSetting
from .audit_log import AuditLog

# Project Models (Employee 도메인의 ProjectParticipation과 연관)
from .project import Project


__all__ = [
    # Mixins
    'DictSerializableMixin',
    'TimestampMixin',
    'SoftDeleteMixin',
    # Employee Domain
    'Employee',
    'Profile',
    'Education',
    'Career',
    'Certificate',
    'FamilyMember',
    'Language',
    'MilitaryService',
    'Salary',
    'Benefit',
    'Contract',
    'SalaryHistory',
    'Promotion',
    'Evaluation',
    'Training',
    'Attendance',
    'Insurance',
    'HrProject',
    'ProjectParticipation',
    'Award',
    'Asset',
    'SalaryPayment',
    'Attachment',
    # Company Domain
    'ClassificationOption',
    'Company',
    'Organization',
    'CompanySettings',
    'CompanyDocument',
    'CompanyVisibilitySettings',
    'NumberCategory',
    'NumberRegistry',
    'IpRange',
    'IpAssignment',
    # User Domain
    'User',
    'CorporateAdminProfile',
    'Notification',
    'NotificationPreference',
    # Contract Domain
    'PersonCorporateContract',
    'DataSharingSettings',
    'SyncLog',
    # Platform Domain
    'SystemSetting',
    'AuditLog',
    # Project
    'Project',
]
