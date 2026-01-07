"""
SQLAlchemy 모델 패키지

모든 데이터베이스 모델을 정의하고 export합니다.

Phase 7: 도메인 중심 마이그레이션 완료
- 모든 모델은 app/domains/에서 import
- 레거시 경로 (app/models/*.py)는 삭제됨
"""
# Employee Domain Models
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

# Company Domain Models
from app.domains.company.models import (
    ClassificationOption,
    Company,
    Organization,
    CompanySettings,
    CompanyDocument,
    CompanyVisibilitySettings,
    NumberCategory,
    NumberRegistry,
    IpRange,
    IpAssignment,
)

# User Domain Models
from app.domains.user.models import (
    User,
    CorporateAdminProfile,
    Notification,
    NotificationPreference,
    PersonalProfile,
)

# Contract Domain Models
from app.domains.contract.models import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog,
)

# Platform Domain Models
from app.domains.platform.models import (
    SystemSetting,
    AuditLog,
)


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
    'PersonalProfile',
    # Contract Domain
    'PersonCorporateContract',
    'DataSharingSettings',
    'SyncLog',
    # Platform Domain
    'SystemSetting',
    'AuditLog',
]
