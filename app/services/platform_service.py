"""
Platform Service

플랫폼 관리자용 비즈니스 로직을 처리합니다.
- 사용자 관리 (조회/수정/권한)
- 법인 관리 (조회/수정)
- 플랫폼 설정 관리

Phase 24: 레이어 분리 리팩토링 - Blueprint → Service → Repository
"""
from typing import Dict, List, Optional, Tuple
from sqlalchemy import or_

from app.database import db
from app.models import User, Company
from app.models.system_setting import SystemSetting
from app.utils.transaction import atomic_transaction


class PlatformService:
    """플랫폼 관리 서비스"""

    # ========================================
    # 사용자 관리
    # ========================================

    def get_users_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str = None,
        account_type: str = None
    ) -> Tuple[List[User], object]:
        """사용자 목록 조회 (페이지네이션)

        Args:
            page: 페이지 번호
            per_page: 페이지당 항목 수
            search: 검색어 (username/email)
            account_type: 계정 타입 필터

        Returns:
            Tuple[사용자 목록, 페이지네이션 객체]
        """
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

    def get_user_by_id(self, user_id: int) -> Optional[User]:
        """사용자 ID로 조회

        Args:
            user_id: 사용자 ID

        Returns:
            User 모델 또는 None
        """
        return db.session.get(User, user_id)

    def toggle_user_active(
        self,
        user_id: int,
        current_user_id: int
    ) -> Tuple[bool, Optional[str], Optional[bool]]:
        """사용자 활성화/비활성화 토글

        Args:
            user_id: 대상 사용자 ID
            current_user_id: 현재 로그인한 사용자 ID

        Returns:
            Tuple[성공여부, 에러메시지, 변경된 is_active 값]
        """
        if user_id == current_user_id:
            return False, '자기 자신은 비활성화할 수 없습니다.', None

        user = self.get_user_by_id(user_id)
        if not user:
            return False, '사용자를 찾을 수 없습니다.', None

        try:
            with atomic_transaction():
                user.is_active = not user.is_active
            return True, None, user.is_active
        except Exception as e:
            return False, str(e), None

    def grant_superadmin(self, user_id: int) -> Tuple[bool, Optional[str]]:
        """Superadmin 권한 부여

        Args:
            user_id: 대상 사용자 ID

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        user = self.get_user_by_id(user_id)
        if not user:
            return False, '사용자를 찾을 수 없습니다.'

        if user.is_superadmin:
            return False, '이미 슈퍼관리자입니다.'

        try:
            with atomic_transaction():
                user.is_superadmin = True
                user.account_type = User.ACCOUNT_PLATFORM
            return True, None
        except Exception as e:
            return False, str(e)

    def revoke_superadmin(
        self,
        user_id: int,
        current_user_id: int
    ) -> Tuple[bool, Optional[str]]:
        """Superadmin 권한 해제

        Args:
            user_id: 대상 사용자 ID
            current_user_id: 현재 로그인한 사용자 ID

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        if user_id == current_user_id:
            return False, '자기 자신의 권한은 해제할 수 없습니다.'

        user = self.get_user_by_id(user_id)
        if not user:
            return False, '사용자를 찾을 수 없습니다.'

        if not user.is_superadmin:
            return False, '슈퍼관리자가 아닙니다.'

        # 마지막 superadmin 확인
        superadmin_count = User.query.filter_by(is_superadmin=True).count()
        if superadmin_count <= 1:
            return False, '최소 1명의 슈퍼관리자가 필요합니다.'

        try:
            with atomic_transaction():
                user.is_superadmin = False
            return True, None
        except Exception as e:
            return False, str(e)

    # ========================================
    # 법인 관리
    # ========================================

    def get_companies_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str = None
    ) -> Tuple[List[Company], object]:
        """법인 목록 조회 (페이지네이션)

        Args:
            page: 페이지 번호
            per_page: 페이지당 항목 수
            search: 검색어 (name/business_number)

        Returns:
            Tuple[법인 목록, 페이지네이션 객체]
        """
        query = Company.query

        if search:
            query = query.filter(
                or_(
                    Company.name.ilike(f'%{search}%'),
                    Company.business_number.ilike(f'%{search}%')
                )
            )

        pagination = query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return pagination.items, pagination

    def get_company_by_id(self, company_id: int) -> Optional[Company]:
        """법인 ID로 조회

        Args:
            company_id: 법인 ID

        Returns:
            Company 모델 또는 None
        """
        return db.session.get(Company, company_id)

    def toggle_company_active(self, company_id: int) -> Tuple[bool, Optional[str], Optional[bool]]:
        """법인 활성화/비활성화 토글

        Args:
            company_id: 대상 법인 ID

        Returns:
            Tuple[성공여부, 에러메시지, 변경된 is_active 값]
        """
        company = self.get_company_by_id(company_id)
        if not company:
            return False, '법인을 찾을 수 없습니다.', None

        try:
            with atomic_transaction():
                company.is_active = not company.is_active
            return True, None, company.is_active
        except Exception as e:
            return False, str(e), None

    def update_company_plan(
        self,
        company_id: int,
        plan_type: str,
        max_employees: int
    ) -> Tuple[bool, Optional[str]]:
        """법인 플랜 변경

        Args:
            company_id: 법인 ID
            plan_type: 플랜 타입
            max_employees: 최대 직원 수

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        company = self.get_company_by_id(company_id)
        if not company:
            return False, '법인을 찾을 수 없습니다.'

        try:
            with atomic_transaction():
                company.plan_type = plan_type
                company.max_employees = max_employees
            return True, None
        except Exception as e:
            return False, str(e)

    # ========================================
    # 플랫폼 설정
    # ========================================

    def get_platform_settings(self) -> Dict:
        """플랫폼 설정 조회

        Returns:
            설정 Dict
        """
        from app.models.platform_settings import PlatformSettings
        settings = PlatformSettings.query.first()
        if settings:
            return settings.to_dict()
        return {}

    def update_platform_settings(self, data: Dict) -> Tuple[bool, Optional[str]]:
        """플랫폼 설정 수정

        Args:
            data: 설정 데이터

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        from app.models.platform_settings import PlatformSettings

        try:
            with atomic_transaction():
                settings = PlatformSettings.query.first()
                if not settings:
                    settings = PlatformSettings()
                    db.session.add(settings)

                for key, value in data.items():
                    if hasattr(settings, key):
                        setattr(settings, key, value)

            return True, None
        except Exception as e:
            return False, str(e)

    def get_users_by_company(self, company_id: int) -> List[User]:
        """법인 소속 사용자 목록 조회

        Args:
            company_id: 법인 ID

        Returns:
            사용자 목록
        """
        return User.query.filter_by(company_id=company_id).all()

    # ========================================
    # 시스템 설정
    # ========================================

    def get_all_settings(self) -> List[SystemSetting]:
        """모든 시스템 설정 조회

        Returns:
            설정 목록
        """
        return SystemSetting.query.order_by(SystemSetting.key).all()

    def get_setting_by_key(self, key: str) -> Optional[SystemSetting]:
        """키로 시스템 설정 조회

        Args:
            key: 설정 키

        Returns:
            SystemSetting 또는 None
        """
        return SystemSetting.query.filter_by(key=key).first()

    def update_setting(self, key: str, value: str) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """시스템 설정 수정

        Args:
            key: 설정 키
            value: 설정 값

        Returns:
            Tuple[성공여부, 에러메시지, 설정정보]
        """
        setting = self.get_setting_by_key(key)
        if not setting:
            return False, f'설정 "{key}"을(를) 찾을 수 없습니다.', None

        try:
            with atomic_transaction():
                setting.value = value
            return True, None, {
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            }
        except Exception as e:
            return False, str(e), None

    def create_setting(
        self,
        key: str,
        value: str,
        description: str = ''
    ) -> Tuple[bool, Optional[str], Optional[Dict]]:
        """시스템 설정 생성

        Args:
            key: 설정 키
            value: 설정 값
            description: 설명

        Returns:
            Tuple[성공여부, 에러메시지, 설정정보]
        """
        if self.get_setting_by_key(key):
            return False, f'설정 "{key}"이(가) 이미 존재합니다.', None

        try:
            with atomic_transaction():
                setting = SystemSetting(
                    key=key,
                    value=value,
                    description=description
                )
                db.session.add(setting)
            return True, None, {
                'key': setting.key,
                'value': setting.value,
                'description': setting.description
            }
        except Exception as e:
            return False, str(e), None

    # ========================================
    # 통계
    # ========================================

    def get_dashboard_stats(self) -> Dict:
        """대시보드 통계 조회

        Returns:
            통계 Dict
        """
        from ..models.person_contract import PersonCorporateContract

        total_users = User.query.count()
        active_users = User.query.filter_by(is_active=True).count()
        total_companies = Company.query.count()
        active_companies = Company.query.filter_by(is_active=True).count()
        total_contracts = PersonCorporateContract.query.count()
        active_contracts = PersonCorporateContract.query.filter_by(
            status=PersonCorporateContract.STATUS_APPROVED
        ).count()
        superadmins = User.query.filter_by(is_superadmin=True).count()

        return {
            'total_users': total_users,
            'active_users': active_users,
            'total_companies': total_companies,
            'active_companies': active_companies,
            'total_contracts': total_contracts,
            'active_contracts': active_contracts,
            'superadmins': superadmins,
        }

    def get_recent_users(self, limit: int = 5) -> list:
        """최근 가입 사용자 조회

        Args:
            limit: 조회 제한 (기본 5)

        Returns:
            User 모델 리스트
        """
        return User.query.order_by(User.created_at.desc()).limit(limit).all()

    def get_recent_companies(self, limit: int = 5) -> list:
        """최근 등록 법인 조회

        Args:
            limit: 조회 제한 (기본 5)

        Returns:
            Company 모델 리스트
        """
        return Company.query.order_by(Company.created_at.desc()).limit(limit).all()


# 싱글톤 인스턴스
platform_service = PlatformService()
