"""
User Repository

사용자 데이터의 CRUD 및 인증 기능을 제공합니다.
"""
from typing import List, Optional, Dict
from app.database import db
from app.models import User
from .base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """사용자 저장소"""

    def __init__(self):
        super().__init__(User)

    def get_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 조회 (모델 객체 반환)"""
        return User.query.filter_by(username=username).first()

    def get_by_email(self, email: str) -> Optional[User]:
        """이메일로 조회 (모델 객체 반환)"""
        return User.query.filter_by(email=email).first()

    def find_by_employee_id(self, employee_id: int) -> Optional[User]:
        """직원 ID로 조회 (모델 객체 반환)

        Phase 24: 신규 표준 메서드 (Model 반환)
        """
        return User.query.filter_by(employee_id=employee_id).first()

    def get_by_employee_id(self, employee_id: int) -> Optional[User]:
        """@deprecated: Use find_by_employee_id() instead"""
        import warnings
        warnings.warn(
            "get_by_employee_id() is deprecated. Use find_by_employee_id() instead.",
            DeprecationWarning, stacklevel=2
        )
        return self.find_by_employee_id(employee_id)

    def authenticate(self, username: str, password: str) -> Optional[User]:
        """사용자 인증 (로그인)"""
        user = self.get_by_username(username)
        if user and user.is_active and user.check_password(password):
            user.update_last_login()
            return user
        return None

    def create_user(self, username: str, email: str, password: str,
                    role: str = User.ROLE_EMPLOYEE, employee_id: int = None) -> User:
        """새 사용자 생성"""
        user = User(
            username=username,
            email=email,
            role=role,
            employee_id=employee_id,
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()
        return user

    def update_password(self, user_id: int, new_password: str) -> bool:
        """비밀번호 변경"""
        user = User.query.get(user_id)
        if user:
            user.set_password(new_password)
            db.session.commit()
            return True
        return False

    def update_role(self, user_id: int, new_role: str) -> bool:
        """역할 변경"""
        if new_role not in User.VALID_ROLES:
            return False

        user = User.query.get(user_id)
        if user:
            user.role = new_role
            db.session.commit()
            return True
        return False

    def deactivate(self, user_id: int) -> bool:
        """사용자 비활성화"""
        user = User.query.get(user_id)
        if user:
            user.is_active = False
            db.session.commit()
            return True
        return False

    def activate(self, user_id: int) -> bool:
        """사용자 활성화"""
        user = User.query.get(user_id)
        if user:
            user.is_active = True
            db.session.commit()
            return True
        return False

    def get_active_users(self) -> List[Dict]:
        """활성 사용자 목록 조회"""
        users = User.query.filter_by(is_active=True).order_by(User.username).all()
        return [user.to_dict() for user in users]

    def get_by_role(self, role: str) -> List[Dict]:
        """역할별 사용자 조회"""
        users = User.query.filter_by(role=role, is_active=True).all()
        return [user.to_dict() for user in users]

    def get_by_company_and_account_type(self, company_id: int, account_type: str) -> List[User]:
        """법인 ID와 계정 타입으로 사용자 목록 조회"""
        return User.query.filter_by(
            company_id=company_id,
            account_type=account_type
        ).all()

    def get_employee_sub_users_with_employee(self, company_id: int) -> List[User]:
        """법인 소속 employee_sub 계정 중 employee_id가 있는 사용자 조회"""
        return User.query.filter(
            User.account_type == User.ACCOUNT_EMPLOYEE_SUB,
            User.company_id == company_id,
            User.employee_id.isnot(None)
        ).all()

    def get_admins(self) -> List[Dict]:
        """관리자 목록 조회"""
        return self.get_by_role(User.ROLE_ADMIN)

    def get_managers(self) -> List[Dict]:
        """매니저 목록 조회"""
        return self.get_by_role(User.ROLE_MANAGER)

    def username_exists(self, username: str) -> bool:
        """사용자명 중복 확인"""
        return User.query.filter_by(username=username).first() is not None

    def email_exists(self, email: str) -> bool:
        """이메일 중복 확인"""
        return User.query.filter_by(email=email).first() is not None

    def get_user_count(self) -> Dict[str, int]:
        """사용자 통계"""
        total = User.query.count()
        active = User.query.filter_by(is_active=True).count()
        admins = User.query.filter_by(role=User.ROLE_ADMIN, is_active=True).count()
        managers = User.query.filter_by(role=User.ROLE_MANAGER, is_active=True).count()
        employees = User.query.filter_by(role=User.ROLE_EMPLOYEE, is_active=True).count()

        return {
            'total': total,
            'active': active,
            'inactive': total - active,
            'admins': admins,
            'managers': managers,
            'employees': employees,
        }

    def get_privacy_settings(self, user_id: int) -> Optional[Dict]:
        """개인정보 공개 설정 조회"""
        user = User.query.get(user_id)
        if user:
            return user.privacy_settings or {
                'show_email': True,
                'show_phone': False,
                'show_address': False,
                'show_birth_date': False,
                'show_profile_photo': True,
            }
        return None

    def update_privacy_settings(self, user_id: int, settings: Dict) -> bool:
        """개인정보 공개 설정 업데이트"""
        user = User.query.get(user_id)
        if user:
            user.privacy_settings = settings
            db.session.commit()
            return True
        return False
