"""
Session Keys 상수 정의

세션 키 하드코딩 제거 및 오타 방지
"""


class SessionKeys:
    """Flask 세션 키 상수"""
    USER_ID = 'user_id'
    ACCOUNT_TYPE = 'account_type'
    EMPLOYEE_ID = 'employee_id'
    COMPANY_ID = 'company_id'
    USER_ROLE = 'user_role'
    PERSONAL_PROFILE_ID = 'personal_profile_id'
    ORG_ID = 'org_id'
    USERNAME = 'username'


class AccountType:
    """계정 타입 상수"""
    PERSONAL = 'personal'
    CORPORATE = 'corporate'
    EMPLOYEE_SUB = 'employee_sub'
    CORPORATE_ADMIN = 'corporate_admin'  # 법인 관리자 (employee_id 없는 corporate)

    @classmethod
    def all_types(cls):
        """모든 계정 타입 리스트"""
        return [cls.PERSONAL, cls.CORPORATE, cls.EMPLOYEE_SUB]

    @classmethod
    def personal_types(cls):
        """개인 관련 계정 타입 (개인/직원)"""
        return [cls.PERSONAL, cls.EMPLOYEE_SUB]


class UserRole:
    """사용자 역할 상수"""
    ADMIN = 'admin'
    MANAGER = 'manager'
    EMPLOYEE = 'employee'
    USER = 'user'
    VIEWER = 'viewer'

    @classmethod
    def admin_roles(cls):
        """관리자 권한 역할들"""
        return [cls.ADMIN, cls.MANAGER]
