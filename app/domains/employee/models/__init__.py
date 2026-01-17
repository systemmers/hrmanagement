# app/domains/employee/models/__init__.py
"""
Employee 도메인 모델 패키지

직원 관련 모든 SQLAlchemy 모델을 정의하고 export합니다.

Phase 31: Attachment는 독립 도메인으로 분리됨 (app/domains/attachment/)
"""
from app.shared.models.mixins import DictSerializableMixin, TimestampMixin, SoftDeleteMixin
from .employee import Employee
from .profile import Profile
from .education import Education
from .career import Career
from .certificate import Certificate
from .family_member import FamilyMember
from .language import Language
from .salary import Salary
from .benefit import Benefit
from .contract import Contract
from .salary_history import SalaryHistory
from .promotion import Promotion
from .evaluation import Evaluation
from .training import Training
from .attendance import Attendance
from .insurance import Insurance
from .hr_project import HrProject
from .project_participation import ProjectParticipation
from .award import Award
from .asset import Asset
from .salary_payment import SalaryPayment
from .employment_contract import EmploymentContract


__all__ = [
    # Mixins
    'DictSerializableMixin',
    'TimestampMixin',
    'SoftDeleteMixin',
    # Core Models
    'Employee',
    'Profile',
    # 1:N Relations
    'Education',
    'Career',
    'Certificate',
    'FamilyMember',
    'Language',
    'SalaryHistory',
    'Promotion',
    'Evaluation',
    'Training',
    'Attendance',
    'HrProject',
    'ProjectParticipation',
    'Award',
    'Asset',
    'SalaryPayment',
    'EmploymentContract',
    # 1:1 Relations
    'Salary',
    'Benefit',
    'Contract',
    'Insurance',
]
