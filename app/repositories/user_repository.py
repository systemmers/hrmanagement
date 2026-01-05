"""
User Repository

사용자 데이터의 CRUD 및 인증 기능을 제공합니다.
"""
from typing import List, Optional, Dict, Tuple
from sqlalchemy import func
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
        """법인 ID와 계정 타입으로 사용자 목록 조회 (가입순 정렬)"""
        return User.query.filter_by(
            company_id=company_id,
            account_type=account_type
        ).order_by(User.id.asc()).all()

    def get_by_company_and_account_type_paginated(
        self,
        company_id: int,
        account_type: str,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict], object]:
        """법인 ID와 계정 타입으로 사용자 목록 조회 (페이지네이션 + 법인 내 시퀀스)

        Args:
            company_id: 법인 ID
            account_type: 계정 타입
            page: 페이지 번호
            per_page: 페이지당 항목 수

        Returns:
            Tuple[사용자 목록 (Dict with company_sequence), 페이지네이션 객체]
        """
        # 1. 법인 내 시퀀스 계산을 위한 서브쿼리
        subquery = db.session.query(
            User.id,
            func.row_number().over(
                partition_by=User.company_id,
                order_by=User.id.asc()
            ).label('company_sequence')
        ).filter_by(
            company_id=company_id,
            account_type=account_type
        ).subquery()

        # 2. 메인 쿼리 (시퀀스 포함)
        query = db.session.query(
            User,
            subquery.c.company_sequence
        ).join(
            subquery, User.id == subquery.c.id
        ).order_by(User.id.asc())

        # 3. 페이지네이션
        pagination = query.paginate(page=page, per_page=per_page, error_out=False)

        # 4. 결과 변환 (Dict with company_sequence)
        users = []
        for user, company_sequence in pagination.items:
            user_dict = user.to_dict() if hasattr(user, 'to_dict') else {
                'id': user.id,
                'username': user.username,
                'email': user.email,
                'role': user.role,
                'is_active': user.is_active,
                'created_at': user.created_at,
            }
            user_dict['company_sequence'] = company_sequence
            users.append(user_dict)

        return users, pagination

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

    # ========================================
    # Phase 30: 레이어 분리용 추가 메서드
    # ========================================

    def count_all(self) -> int:
        """전체 사용자 수 조회

        Returns:
            전체 사용자 수
        """
        return User.query.count()

    def count_by_is_active(self, is_active: bool) -> int:
        """활성화 상태별 사용자 수 조회

        Args:
            is_active: 활성화 상태

        Returns:
            사용자 수
        """
        return User.query.filter_by(is_active=is_active).count()

    def count_superadmins(self) -> int:
        """슈퍼어드민 수 조회

        Returns:
            슈퍼어드민 수
        """
        return User.query.filter_by(
            account_type=User.ACCOUNT_SUPERADMIN,
            is_active=True
        ).count()

    def count_by_account_type(self, account_type: str) -> int:
        """계정 유형별 사용자 수 조회

        Args:
            account_type: 계정 유형

        Returns:
            사용자 수
        """
        return User.query.filter_by(account_type=account_type).count()

    def find_by_id(self, user_id: int) -> Optional[User]:
        """ID로 사용자 조회 (모델 반환)

        Args:
            user_id: 사용자 ID

        Returns:
            User 모델 객체 또는 None
        """
        return User.query.get(user_id)

    def find_by_email(self, email: str) -> Optional[User]:
        """이메일로 사용자 조회 (신규 표준 메서드명)

        Args:
            email: 이메일 주소

        Returns:
            User 모델 객체 또는 None
        """
        return User.query.filter_by(email=email).first()

    def find_by_username(self, username: str) -> Optional[User]:
        """사용자명으로 조회 (신규 표준 메서드명)

        Args:
            username: 사용자명

        Returns:
            User 모델 객체 또는 None
        """
        return User.query.filter_by(username=username).first()

    def find_by_company_id(self, company_id: int) -> List[User]:
        """법인 소속 사용자 목록 조회 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            company_id: 법인 ID

        Returns:
            User 모델 객체 리스트
        """
        return User.query.filter_by(company_id=company_id).all()

    def find_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str = None,
        account_type: str = None
    ) -> Tuple[List[User], object]:
        """사용자 목록 조회 (페이지네이션)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            page: 페이지 번호
            per_page: 페이지당 항목 수
            search: 검색어 (username/email)
            account_type: 계정 타입 필터

        Returns:
            Tuple[User 모델 리스트, 페이지네이션 객체]
        """
        from sqlalchemy import or_

        query = User.query

        if search:
            query = query.filter(
                or_(
                    User.username.ilike(f'%{search}%'),
                    User.email.ilike(f'%{search}%')
                )
            )

        if account_type:
            query = query.filter_by(account_type=account_type)

        pagination = query.order_by(User.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return pagination.items, pagination

    def find_recent(self, limit: int = 5) -> List[User]:
        """최근 가입 사용자 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            limit: 조회 제한 (기본 5)

        Returns:
            User 모델 리스트
        """
        return User.query.order_by(User.created_at.desc()).limit(limit).all()

    def create_personal_user(
        self,
        username: str,
        email: str,
        password: str,
        commit: bool = True
    ) -> User:
        """개인 계정 사용자 생성

        Phase 30: personal_service.register() 레이어 분리용 메서드

        Args:
            username: 사용자명
            email: 이메일
            password: 비밀번호
            commit: 즉시 커밋 여부

        Returns:
            생성된 User 모델 객체
        """
        user = User(
            username=username,
            email=email,
            role=User.ROLE_EMPLOYEE,
            account_type=User.ACCOUNT_PERSONAL,
            is_active=True
        )
        user.set_password(password)
        db.session.add(user)
        if commit:
            db.session.commit()
        else:
            db.session.flush()
        return user

    def find_active_personal_users(self) -> List[User]:
        """활성화된 개인 계정 사용자 목록 조회

        Phase 30: contract_core_service 레이어 분리용 메서드

        Returns:
            개인 계정 User 모델 리스트
        """
        return User.query.filter(
            User.account_type == User.ACCOUNT_PERSONAL,
            User.is_active == True
        ).all()


# 싱글톤 인스턴스
user_repository = UserRepository()
