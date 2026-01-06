"""
사용자 서비스

사용자 인증 및 계정 관리 비즈니스 로직을 제공합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Phase 24: Option A 레이어 분리 - Service는 Dict 반환 표준화
"""
from typing import Dict, List, Optional, Any, Tuple


class UserService:
    """
    사용자 서비스

    인증, 비밀번호 관리, 계정 설정 기능을 제공합니다.
    """

    @property
    def user_repo(self):
        """지연 초기화된 사용자 Repository"""
        from app.domains.user import get_user_repo
        return get_user_repo()

    # ========================================
    # 인증
    # ========================================

    def authenticate(self, username: str, password: str) -> Optional[Any]:
        """사용자 인증

        Args:
            username: 사용자명
            password: 비밀번호

        Returns:
            User 객체 또는 None
        """
        return self.user_repo.authenticate(username, password)

    # ========================================
    # 비밀번호 관리
    # ========================================

    def update_password(self, user_id: int, new_password: str) -> bool:
        """비밀번호 변경

        Args:
            user_id: 사용자 ID
            new_password: 새 비밀번호

        Returns:
            성공 여부
        """
        return self.user_repo.update_password(user_id, new_password)

    # ========================================
    # 개인정보 공개 설정
    # ========================================

    def get_privacy_settings(self, user_id: int) -> Optional[Dict]:
        """개인정보 공개 설정 조회

        Args:
            user_id: 사용자 ID

        Returns:
            공개 설정 Dict 또는 None
        """
        return self.user_repo.get_privacy_settings(user_id)

    def update_privacy_settings(self, user_id: int, settings: Dict) -> bool:
        """개인정보 공개 설정 저장

        Args:
            user_id: 사용자 ID
            settings: 공개 설정 Dict

        Returns:
            성공 여부
        """
        return self.user_repo.update_privacy_settings(user_id, settings)

    # ========================================
    # 계정 관리
    # ========================================

    def deactivate(self, user_id: int) -> bool:
        """계정 비활성화 (soft delete)

        Args:
            user_id: 사용자 ID

        Returns:
            성공 여부
        """
        return self.user_repo.deactivate(user_id)

    def get_by_id(self, user_id: int) -> Optional[Dict]:
        """사용자 ID로 조회 (Dict 반환)

        Phase 24: find_by_id() + to_dict() 패턴 적용

        Args:
            user_id: 사용자 ID

        Returns:
            User Dict 또는 None
        """
        model = self.user_repo.find_by_id(user_id)
        return model.to_dict() if model else None

    def get_model_by_id(self, user_id: int) -> Optional[Any]:
        """사용자 ID로 모델 객체 조회

        Args:
            user_id: 사용자 ID

        Returns:
            User 모델 객체 또는 None
        """
        return self.user_repo.find_by_id(user_id)

    def get_by_company_and_account_type(
        self,
        company_id: int,
        account_type: str
    ) -> list:
        """회사 ID와 계정 유형으로 사용자 목록 조회

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            company_id: 회사 ID
            account_type: 계정 유형 (employee_sub, corporate 등)

        Returns:
            User 모델 객체 리스트
        """
        return self.user_repo.get_by_company_and_account_type(company_id, account_type)

    def get_by_company_and_account_type_paginated(
        self,
        company_id: int,
        account_type: str,
        page: int = 1,
        per_page: int = 20
    ) -> Tuple[List[Dict], Any]:
        """회사 ID와 계정 유형으로 사용자 목록 조회 (페이지네이션)

        Args:
            company_id: 회사 ID
            account_type: 계정 유형
            page: 페이지 번호
            per_page: 페이지당 항목 수

        Returns:
            Tuple[사용자 목록 (company_sequence 포함), 페이지네이션 객체]
        """
        return self.user_repo.get_by_company_and_account_type_paginated(
            company_id, account_type, page, per_page
        )

    def get_employee_sub_users_with_employee(self, company_id: int) -> list:
        """회사 소속 employee_sub 계정 목록 조회 (Employee 정보 포함)

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            company_id: 회사 ID

        Returns:
            User 모델 객체 리스트 (employee 관계 로드됨)
        """
        return self.user_repo.get_employee_sub_users_with_employee(company_id)

    def find_by_employee_id(self, employee_id: int) -> Optional[Any]:
        """Employee ID로 연결된 User 조회

        Phase 24: Blueprint → Repository 직접 호출 제거

        Args:
            employee_id: Employee.id

        Returns:
            User 모델 객체 또는 None
        """
        return self.user_repo.find_by_employee_id(employee_id)

    def get_users_with_contract_and_employee_details(
        self,
        users: List[Dict],
        company_id: int
    ) -> List[Dict]:
        """사용자 목록에 계약 상태 및 직원 정보 추가 (레이어 분리용)

        Blueprint의 for 루프 데이터 변환 로직을 Service로 이동.

        Args:
            users: 사용자 Dict 목록
            company_id: 법인 ID

        Returns:
            계약 상태와 직원 이름이 추가된 사용자 목록
        """
        from app.services.user_employee_link_service import user_employee_link_service
        from app.domains.employee.services import employee_service

        if not users or not company_id:
            return users

        # 계약 상태 벌크 조회
        user_ids = [u['id'] for u in users]
        contract_map = user_employee_link_service.get_users_with_contract_status_bulk(
            user_ids, company_id
        )

        # Employee 정보 벌크 조회 (이름 표시용)
        employee_ids = [u.get('employee_id') for u in users if u.get('employee_id')]
        employee_map = {}
        if employee_ids:
            employees = employee_service.get_employees_by_ids(employee_ids)
            employee_map = {emp.get('id'): emp for emp in employees}

        # contract_status, name 추가
        for user in users:
            contract_info = contract_map.get(user['id'], {})
            user['contract_status'] = contract_info.get('status', 'none')

            # Employee에서 이름 조회
            employee_id = user.get('employee_id')
            if employee_id and employee_id in employee_map:
                user['name'] = employee_map[employee_id].get('name', '-')
            else:
                user['name'] = '-'

        return users


# 싱글톤 인스턴스
user_service = UserService()
