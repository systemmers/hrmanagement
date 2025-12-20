"""
Contract Service

개인-법인 계약 관련 비즈니스 로직을 처리합니다.
- 계약 조회 (개인/법인)
- 계약 요청/승인/거절/종료
- 데이터 공유 설정
- 계약 통계

21번 원칙 확장:
- personal 계정: 기존 개인-법인 계약
- employee_sub 계정: 직원-법인 계약 (동일한 프로세스)
"""
from typing import Dict, Optional, List, Any, Tuple
from flask import session

from ..constants.session_keys import AccountType
from ..extensions import person_contract_repo, user_repo
from ..database import db
from ..models.user import User


class ContractService:
    """계약 관리 서비스"""

    def __init__(self):
        self.contract_repo = person_contract_repo
        self.user_repo = user_repo

    # ========================================
    # 개인 계정용 메서드
    # ========================================

    def get_personal_contracts(self, user_id: int) -> List[Dict]:
        """개인 계약 목록 조회"""
        return self.contract_repo.get_by_person_user_id(user_id)

    def get_personal_pending_contracts(self, user_id: int) -> List[Dict]:
        """개인 대기 중인 계약 조회"""
        return self.contract_repo.get_pending_contracts_by_person(user_id)

    def get_personal_statistics(self, user_id: int) -> Dict:
        """개인 계약 통계"""
        return self.contract_repo.get_statistics_by_person(user_id)

    # ========================================
    # 법인 계정용 메서드
    # ========================================

    def get_company_contracts(self, company_id: int) -> List[Dict]:
        """법인 계약 목록 조회"""
        return self.contract_repo.get_by_company_id(company_id)

    def get_company_pending_contracts(self, company_id: int) -> List[Dict]:
        """법인 대기 중인 계약 조회"""
        return self.contract_repo.get_pending_contracts_by_company(company_id)

    def get_company_statistics(self, company_id: int) -> Dict:
        """법인 계약 통계"""
        return self.contract_repo.get_statistics_by_company(company_id)

    def search_contracts(self, company_id: int, status: str = None,
                         contract_type: str = None, search_term: str = None) -> List[Dict]:
        """계약 검색 (법인용)"""
        return self.contract_repo.search_contracts(
            company_id=company_id,
            status=status,
            contract_type=contract_type,
            search_term=search_term
        )

    # ========================================
    # 계약 상세 조회
    # ========================================

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        """계약 상세 조회"""
        return self.contract_repo.get_by_id(contract_id)

    def get_contract_model_by_id(self, contract_id: int):
        """계약 모델 조회 (ORM 객체)"""
        return self.contract_repo.get_model_by_id(contract_id)

    def get_sharing_settings(self, contract_id: int) -> Dict:
        """데이터 공유 설정 조회"""
        return self.contract_repo.get_sharing_settings(contract_id)

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        """동기화 로그 조회"""
        return self.contract_repo.get_sync_logs(contract_id, limit)

    # ========================================
    # 계약 생성/수정
    # ========================================

    def create_contract_request(
        self,
        person_email: str,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """계약 요청 생성 (법인 -> 개인/직원)

        21번 원칙: personal, employee_sub 계정 모두 지원

        Returns:
            Tuple[성공여부, 계약정보, 에러메시지]
        """
        # 개인 또는 직원 사용자 조회 (21번 원칙)
        person_user = User.query.filter(
            User.email == person_email,
            User.account_type.in_(AccountType.personal_types())
        ).first()

        if not person_user:
            return False, None, '해당 이메일의 계정을 찾을 수 없습니다.'

        try:
            contract = self.contract_repo.create_contract_request(
                person_user_id=person_user.id,
                company_id=company_id,
                requested_by='company',
                contract_type=contract_type,
                position=position,
                department=department,
                notes=notes
            )
            return True, contract, None
        except ValueError as e:
            return False, None, str(e)

    def create_employee_contract_request(
        self,
        employee_user_id: int,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """직원/개인 계정에 대한 계약 요청 (21번 원칙)

        직원 등록 후 계약 요청 시 사용
        employee_user_id로 직접 계약 요청
        21번 원칙: personal, employee_sub 계정 모두 지원

        Returns:
            Tuple[성공여부, 계약정보, 에러메시지]
        """
        # 직원 또는 개인 계정 확인 (21번 원칙)
        employee_user = User.query.filter(
            User.id == employee_user_id,
            User.account_type.in_(AccountType.personal_types())
        ).first()

        if not employee_user:
            return False, None, '해당 계정을 찾을 수 없습니다.'

        # 이미 해당 법인과 계약이 있는지 확인
        existing = self.contract_repo.get_contract_between(
            person_user_id=employee_user_id,
            company_id=company_id
        )
        if existing:
            return False, None, '이미 계약이 존재하거나 대기 중입니다.'

        try:
            contract = self.contract_repo.create_contract_request(
                person_user_id=employee_user_id,
                company_id=company_id,
                requested_by='company',
                contract_type=contract_type,
                position=position,
                department=department,
                notes=notes
            )
            return True, contract, None
        except ValueError as e:
            return False, None, str(e)

    def get_employee_contract_status(
        self,
        employee_user_id: int,
        company_id: int
    ) -> Optional[str]:
        """직원의 계약 상태 조회

        Returns:
            'none' | 'pending' | 'approved' | 'rejected' | 'terminated'
        """
        contract = self.contract_repo.get_contract_between(
            person_user_id=employee_user_id,
            company_id=company_id
        )
        if not contract:
            return 'none'
        return contract.get('status', 'none')

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """데이터 공유 설정 업데이트

        Returns:
            Tuple[성공여부, 설정정보, 에러메시지]
        """
        try:
            result = self.contract_repo.update_sharing_settings(contract_id, settings)
            return True, result, None
        except ValueError as e:
            return False, None, str(e)

    # ========================================
    # 계약 상태 변경
    # ========================================

    def approve_contract(self, contract_id: int, user_id: int) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """계약 승인

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        try:
            result = self.contract_repo.approve_contract(contract_id, user_id)
            return True, result, None
        except ValueError as e:
            return False, None, str(e)

    def reject_contract(self, contract_id: int, user_id: int, reason: str = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """계약 거절

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        try:
            result = self.contract_repo.reject_contract(contract_id, user_id, reason)
            return True, result, None
        except ValueError as e:
            return False, None, str(e)

    def terminate_contract(self, contract_id: int, user_id: int, reason: str = None) -> Tuple[bool, Optional[Dict], Optional[str]]:
        """계약 종료

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        try:
            result = self.contract_repo.terminate_contract(contract_id, user_id, reason)
            return True, result, None
        except ValueError as e:
            return False, None, str(e)


# 싱글톤 인스턴스
contract_service = ContractService()
