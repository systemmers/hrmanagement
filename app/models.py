"""
데이터베이스 모델 정의
User, Employee, Department, Position
"""
from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import db


class User(UserMixin, db.Model):
    """관리자 계정 모델"""

    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(255), nullable=False)
    name = db.Column(db.String(50), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    def set_password(self, password):
        """비밀번호 해싱"""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        """비밀번호 검증"""
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Department(db.Model):
    """부서 마스터 모델"""

    __tablename__ = 'departments'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    code = db.Column(db.String(20), unique=True, nullable=True)
    parent_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 관계 설정
    parent = db.relationship('Department', remote_side=[id], backref='children')
    employees = db.relationship('Employee', backref='department', lazy='dynamic')

    def __repr__(self):
        return f'<Department {self.name}>'


class Position(db.Model):
    """직급 마스터 모델"""

    __tablename__ = 'positions'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=False, index=True)
    level = db.Column(db.Integer, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    # 관계 설정
    employees = db.relationship('Employee', backref='position', lazy='dynamic')

    def __repr__(self):
        return f'<Position {self.name}>'


class Employee(db.Model):
    """직원 기본정보 모델"""

    __tablename__ = 'employees'

    id = db.Column(db.Integer, primary_key=True)

    # 기본 정보
    photo = db.Column(db.String(255), nullable=True)
    name = db.Column(db.String(50), nullable=False, index=True)
    phone = db.Column(db.String(20), nullable=True)
    email = db.Column(db.String(100), nullable=True, index=True)
    address = db.Column(db.String(255), nullable=True)

    # 소속 정보
    department_id = db.Column(db.Integer, db.ForeignKey('departments.id'), nullable=True)
    position_id = db.Column(db.Integer, db.ForeignKey('positions.id'), nullable=True)
    hire_date = db.Column(db.Date, nullable=True)
    employment_type = db.Column(db.String(20), nullable=True)  # 정규직, 계약직, 인턴 등
    workplace = db.Column(db.String(100), nullable=True)

    # 상태
    status = db.Column(db.String(20), nullable=False, default='active')  # active, warning, expired

    # 타임스탬프
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow, onupdate=datetime.utcnow)

    @property
    def status_display(self):
        """상태를 한글로 표시"""
        status_map = {
            'active': '정상',
            'warning': '주의',
            'expired': '만료'
        }
        return status_map.get(self.status, '알 수 없음')

    @property
    def status_class(self):
        """상태에 따른 CSS 클래스"""
        return self.status

    @property
    def get_work_duration(self):
        """근무 기간을 일수로 계산"""
        if not self.hire_date:
            return 0
        today = datetime.utcnow().date()
        delta = today - self.hire_date
        return delta.days

    @property
    def get_work_duration_display(self):
        """근무 기간을 년/월/일로 표시"""
        if not self.hire_date:
            return '-'

        today = datetime.utcnow().date()
        delta = today - self.hire_date
        days = delta.days

        years = days // 365
        months = (days % 365) // 30
        remaining_days = (days % 365) % 30

        parts = []
        if years > 0:
            parts.append(f'{years}년')
        if months > 0:
            parts.append(f'{months}개월')
        if remaining_days > 0 or not parts:
            parts.append(f'{remaining_days}일')

        return ' '.join(parts)

    def __repr__(self):
        return f'<Employee {self.name}>'

    def to_dict(self):
        """JSON 직렬화를 위한 딕셔너리 변환"""
        return {
            'id': self.id,
            'photo': self.photo,
            'name': self.name,
            'phone': self.phone,
            'email': self.email,
            'address': self.address,
            'department': self.department.name if self.department else None,
            'department_id': self.department_id,
            'position': self.position.name if self.position else None,
            'position_id': self.position_id,
            'hire_date': self.hire_date.isoformat() if self.hire_date else None,
            'employment_type': self.employment_type,
            'workplace': self.workplace,
            'status': self.status,
            'created_at': self.created_at.isoformat(),
            'updated_at': self.updated_at.isoformat()
        }
