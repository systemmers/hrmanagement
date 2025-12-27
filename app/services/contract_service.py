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

Phase 24: Option A 레이어 분리 - Service는 Dict 반환 표준화
"""
from typing import Dict, Optional, List, Any, Tuple
from flask import session

from ..constants.session_keys import AccountType
from ..extensions import person_contract_repo, user_repo, employee_repo
from ..database import db
from ..models.user import User
from ..models.employee import Employee


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

    def get_contract_eligible_targets(self, company_id: int) -> Dict[str, List[Dict]]:
        """계약 요청 가능한 대상 목록 조회

        Returns:
            {
                'personal_accounts': [개인계정 목록],
                'employee_accounts': [직원계정 목록 (pending_contract 상태)]
            }
        """
        result = {
            'personal_accounts': [],
            'employee_accounts': []
        }

        # 1. 개인계정 중 해당 법인과 계약 미체결 (또는 거절/종료된 계약만 있는 경우)
        # 기존 계약이 없거나, active/pending 상태가 아닌 계정만 포함
        personal_users = User.query.filter(
            User.account_type == AccountType.PERSONAL,
            User.is_active == True
        ).all()

        for user in personal_users:
            # 해당 법인과의 계약 상태 확인
            existing_contract = self.contract_repo.get_contract_between(
                person_user_id=user.id,
                company_id=company_id
            )
            # 계약이 없거나, rejected/terminated 상태인 경우만 포함
            if not existing_contract or existing_contract.get('status') in ['rejected', 'terminated']:
                result['personal_accounts'].append({
                    'user_id': user.id,
                    'name': user.username,
                    'email': user.email,
                    'account_type': 'personal'
                })

        # 2. 직원계정 중 계약 미체결 상태 (pending_info 또는 pending_contract)
        pending_employees = Employee.query.filter(
            Employee.company_id == company_id,
            Employee.status.in_(['pending_info', 'pending_contract'])
        ).all()

        for emp in pending_employees:
            # 직원의 user 계정 정보 조회
            emp_user = User.query.filter(
                User.employee_id == emp.id
            ).first()

            if emp_user:
                # 해당 법인과의 계약 상태 확인
                existing_contract = self.contract_repo.get_contract_between(
                    person_user_id=emp_user.id,
                    company_id=company_id
                )
                # 계약이 없거나, rejected/terminated 상태인 경우만 포함
                if not existing_contract or existing_contract.get('status') in ['rejected', 'terminated']:
                    # 상태별 레이블 설정
                    status_label = '프로필 미완성' if emp.status == 'pending_info' else '계약 대기'
                    result['employee_accounts'].append({
                        'user_id': emp_user.id,
                        'employee_id': emp.id,
                        'name': emp.name,
                        'email': emp_user.email,
                        'department': emp.department,
                        'position': emp.position,
                        'account_type': 'employee_sub',
                        'status': emp.status,
                        'status_label': status_label
                    })

        return result

    # ========================================
    # 계약 상세 조회
    # ========================================

    def get_contract_by_id(self, contract_id: int) -> Optional[Dict]:
        """계약 상세 조회 (Dict 반환)

        Phase 24: find_by_id() + to_dict() 패턴 적용
        """
        model = self.contract_repo.find_by_id(contract_id)
        return model.to_dict() if model else None

    def get_contract_model_by_id(self, contract_id: int):
        """계약 모델 조회 (ORM 객체)"""
        return self.contract_repo.find_by_id(contract_id)

    def get_sharing_settings(self, contract_id: int) -> Dict:
        """데이터 공유 설정 조회"""
        return self.contract_repo.get_sharing_settings(contract_id)

    def get_sharing_settings_model(self, contract_id: int) -> Optional[Any]:
        """데이터 공유 설정 모델 조회

        Phase 24: Blueprint Model.query 제거 - Service 경유

        Args:
            contract_id: 계약 ID

        Returns:
            DataSharingSettings 모델 또는 None
        """
        from ..models.person_contract import DataSharingSettings
        return DataSharingSettings.query.filter_by(contract_id=contract_id).first()

    def get_sync_logs_filtered(
        self, contract_id: int, sync_type: str = None, limit: int = 50
    ) -> List[Dict]:
        """동기화 로그 조회 (필터링 지원)

        Phase 24: Blueprint Model.query 제거 - Service 경유

        Args:
            contract_id: 계약 ID
            sync_type: 동기화 유형 필터 (선택)
            limit: 최대 조회 수

        Returns:
            로그 목록 (Dict)
        """
        from ..models.person_contract import SyncLog
        query = SyncLog.query.filter_by(contract_id=contract_id)
        if sync_type:
            query = query.filter_by(sync_type=sync_type)
        logs = query.order_by(SyncLog.executed_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        """동기화 로그 조회"""
        return self.contract_repo.get_sync_logs(contract_id, limit)

    def find_contract_with_history(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        """계약 이력 조회 (approved/terminated/expired)

        Phase 24: Blueprint Model.query 제거 - Service 경유

        Args:
            employee_number: 직원번호
            company_id: 회사 ID

        Returns:
            계약 모델 또는 None
        """
        from ..models.person_contract import PersonCorporateContract

        if not employee_number or not company_id:
            return None

        return PersonCorporateContract.query.filter(
            PersonCorporateContract.employee_number == employee_number,
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_([
                PersonCorporateContract.STATUS_APPROVED,
                PersonCorporateContract.STATUS_TERMINATED,
                PersonCorporateContract.STATUS_EXPIRED
            ])
        ).first()

    def find_approved_contract(
        self, employee_number: str, company_id: int
    ) -> Optional[Any]:
        """승인된 계약 조회

        Phase 24: Blueprint Model.query 제거 - Service 경유

        Args:
            employee_number: 직원번호
            company_id: 회사 ID

        Returns:
            계약 모델 또는 None
        """
        return self.contract_repo.find_approved_contract_by_employee_number(
            employee_number, company_id
        )

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
