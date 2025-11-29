"""
User SQLAlchemy 모델

사용자 인증 및 권한 관리를 위한 모델입니다.
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
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    last_login = db.Column(db.DateTime, nullable=True)

    # Relationships
    employee = db.relationship('Employee', backref=db.backref('user', uselist=False))

    # Role constants
    ROLE_ADMIN = 'admin'
    ROLE_MANAGER = 'manager'
    ROLE_EMPLOYEE = 'employee'

    VALID_ROLES = [ROLE_ADMIN, ROLE_MANAGER, ROLE_EMPLOYEE]

    def set_password(self, password):
        """비밀번호 해싱 및 저장"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호 검증"""
        return check_password_hash(self.password_hash, password)

    def update_last_login(self):
        """마지막 로그인 시간 업데이트"""
        self.last_login = datetime.utcnow()
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
            # TODO: 매니저의 소속 부서 직원인지 확인
            return True
        if self.employee_id == employee_id:
            return True
        return False

    def to_dict(self):
        """딕셔너리 변환 (비밀번호 제외)"""
        return {
            'id': self.id,
            'username': self.username,
            'email': self.email,
            'role': self.role,
            'employee_id': self.employee_id,
            'is_active': self.is_active,
            'created_at': self.created_at.isoformat() if self.created_at else None,
            'last_login': self.last_login.isoformat() if self.last_login else None,
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
        )
        if data.get('password'):
            user.set_password(data['password'])
        return user

    def __repr__(self):
        return f'<User {self.username} ({self.role})>'
