"""
User SQLAlchemy 모델

사용자 인증 및 권한 관리를 위한 모델입니다.
플랫폼 멀티테넌시를 위해 계정 유형(account_type)과 법인 연결(company_id)을 지원합니다.
Phase 2 Migration: 도메인으로 이동
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from app.database import db


class User(db.Model):
    """사용자 모델"""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    username = db.Column(db.String(80), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    role = db.Column(db.String(20), default='employee', nullable=False)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_superadmin = db.Column(db.Boolean, default=False, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login_at = db.Column(db.DateTime, nullable=True)  # Phase 0.7: last_login -> last_login_at

    # 플랫폼 계정 유형 (Phase 1: Company 모델)
    account_type = db.Column(
        db.String(20),
        default='corporate',
        nullable=False,
        index=True
    )
    # 법인 계정 연결 (corporate, employee_sub 계정일 때)
    company_id = db.Column(
        db.Integer,
        db.ForeignKey('companies.id'),
        nullable=True,
        index=True
    )
    # 하위 직원 계정의 부모 사용자 (employee_sub일 때)
    parent_user_id = db.Column(
        db.Integer,
        db.ForeignKey('users.id'),
        nullable=True
    )
    # 개인정보 공개 설정 (JSON)
    privacy_settings = db.Column(db.JSON, nullable=True, default=dict)

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('user', uselist=False))
    company = db.relationship(
        'Company',
        foreign_keys=[company_id],
        backref=db.backref('users', lazy='dynamic')
    )
    parent_user = db.relationship(
        'User',
        remote_side=[id],
        foreign_keys=[parent_user_id],
        backref=db.backref('sub_users', lazy='dynamic')
    )

    # Role constants (기존 호환성 유지)
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_EMPLOYEE = 'employee'

    VALID_ROLES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_EMPLOYEE]

    # Account type constants (Phase 1)
    ACCOUNT_PERSONAL = 'personal'
    ACCOUNT_CORPORATE = 'corporate'
    ACCOUNT_EMPLOYEE_SUB = 'employee_sub'
    ACCOUNT_PLATFORM = 'platform'  # 플랫폼 마스터 관리자

    VALID_ACCOUNT_TYPES = [ACCOUNT_PERSONAL, ACCOUNT_CORPORATE, ACCOUNT_EMPLOYEE_SUB, ACCOUNT_PLATFORM]

    ACCOUNT_TYPE_LABELS = {
        ACCOUNT_PERSONAL: '개인계정',
        ACCOUNT_CORPORATE: '법인계정',
        ACCOUNT_EMPLOYEE_SUB: '직원계정',
        ACCOUNT_PLATFORM: '플랫폼관리자',
    }

    def set_password(self, password):
        """비밀번호 해싱 및 저장"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호 검증"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login_at = datetime.utcnow()
        db.session.commit()

    def is_admin(self):
        """관리자 여부 확인"""
        return self.role == self.ROLE_ADMIN

    def is_manager(self):
        """매니저 여부 확인"""
        return self.role == self.ROLE_MANAGER

    def has_role(self, role):
        """특정 역할 보유 여부 확인"""
        return self.role == role

    def can_access_employee(self, employee_id):
        """특정 직원 정보 접근 권한 확인"""
        if self.is_admin():
            return True
        if self.is_manager():
            # 매니저의 소속 부서 직원인지 확인
            if self.employee_id:
                from app.domains.employee.models import Employee
                manager_employee = Employee.query.get(self.employee_id)
                target_employee = Employee.query.get(employee_id)
                if manager_employee and target_employee:
                    return manager_employee.department == target_employee.department
            return False
        if self.employee_id == employee_id:
            return True
        return False

    # Account type methods (Phase 1)
    def is_personal_account(self):
        """개인 계정 여부"""
        return self.account_type == self.ACCOUNT_PERSONAL

    def is_corporate_account(self):
        """법인 계정 여부"""
        return self.account_type == self.ACCOUNT_CORPORATE

    def is_employee_sub_account(self):
        """법인 하위 직원 계정 여부"""
        return self.account_type == self.ACCOUNT_EMPLOYEE_SUB

    def is_platform_admin(self):
        """플랫폼 마스터 관리자 여부"""
        return self.is_superadmin

    def get_account_type_label(self):
        """계정 유형 한글 라벨"""
        return self.ACCOUNT_TYPE_LABELS.get(self.account_type, self.account_type)

    def get_company(self):
        """연결된 법인 정보 반환"""
        if self.company_id:
            return self.company
        if self.parent_user_id and self.parent_user:
            return self.parent_user.company
        return None

    def can_manage_company(self):
        """법인 관리 권한 확인 (corporate 계정의 admin/manager)"""
        if self.account_type != self.ACCOUNT_CORPORATE:
            return False
        return self.role in [self.ROLE_ADMIN, self.ROLE_MANAGER]

    def to_dict(self):
        """딕셔너리 변환 (비밀번호 제외)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'is_superadmin': self.is_superadmin,
            'account_type': self.account_type,
            'account_type_label': self.get_account_type_label(),
            'company_id': self.company_id,
            'parent_user_id': self.parent_user_id,
            'privacy_settings': self.privacy_settings or {},
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login_at': self.last_login_at.isoformat() if self.last_login_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        user = cls(
            username=data.get('username'),
            email=data.get('email'),
            role=data.get('role', cls.ROLE_EMPLOYEE),
            employee_id=data.get('employee_id'),
            is_active=data.get('is_active', True),
            is_superadmin=data.get('is_superadmin', False),
            account_type=data.get('account_type', cls.ACCOUNT_CORPORATE),
            company_id=data.get('company_id'),
            parent_user_id=data.get('parent_user_id'),
        )
        if data.get('password'):
            user.set_password(data['password'])
        return user

    def __repr__(self):
        return f'<User {self.username} ({self.role}/{self.account_type})>'
