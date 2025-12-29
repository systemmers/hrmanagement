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
Phase 1 Refactoring: Repository 비즈니스 로직을 Service로 이동
"""
from typing import Dict, Optional, List, Any
from flask import session

from ..constants.session_keys import AccountType
from ..database import db
from ..models.user import User
from ..models.employee import Employee
from ..models.personal_profile import PersonalProfile
from ..models.person_contract import PersonCorporateContract, DataSharingSettings
from ..constants.status import ContractStatus, EmployeeStatus
from ..utils.transaction import atomic_transaction
from .base import ServiceResult


class ContractService:
    """계약 관리 서비스"""

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        from ..extensions import person_contract_repo
        return person_contract_repo

    @property
    def user_repo(self):
        """지연 초기화된 사용자 Repository"""
        from ..extensions import user_repo
        return user_repo

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
            if not existing_contract or existing_contract.get('status') in [ContractStatus.REJECTED, ContractStatus.TERMINATED]:
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
                if not existing_contract or existing_contract.get('status') in [ContractStatus.REJECTED, ContractStatus.TERMINATED]:
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

    def update_or_create_sharing_settings(
        self, contract_id: int, commit: bool = True, **kwargs
    ) -> Any:
        """데이터 공유 설정 생성 또는 업데이트

        Phase 2: Blueprint db.session 직접 사용 제거 - SSOT

        Args:
            contract_id: 계약 ID
            commit: 트랜잭션 커밋 여부 (atomic_transaction 내에서는 False)
            **kwargs: 업데이트할 필드 (share_basic_info, is_realtime_sync 등)

        Returns:
            DataSharingSettings 모델
        """
        from ..models.person_contract import DataSharingSettings

        settings = self.get_sharing_settings_model(contract_id)
        if not settings:
            settings = DataSharingSettings(contract_id=contract_id)
            db.session.add(settings)

        for key, value in kwargs.items():
            if hasattr(settings, key):
                setattr(settings, key, value)

        if commit:
            db.session.commit()
        else:
            db.session.flush()

        return settings

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
    ) -> ServiceResult[Dict]:
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
            return ServiceResult.fail('해당 이메일의 계정을 찾을 수 없습니다.')

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
            return ServiceResult.ok(data=contract)
        except ValueError as e:
            return ServiceResult.fail(str(e))

    def create_employee_contract_request(
        self,
        employee_user_id: int,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> ServiceResult[Dict]:
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
            return ServiceResult.fail('해당 계정을 찾을 수 없습니다.')

        # 이미 해당 법인과 계약이 있는지 확인
        existing = self.contract_repo.get_contract_between(
            person_user_id=employee_user_id,
            company_id=company_id
        )
        if existing:
            return ServiceResult.fail('이미 계약이 존재하거나 대기 중입니다.')

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
            return ServiceResult.ok(data=contract)
        except ValueError as e:
            return ServiceResult.fail(str(e))

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

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> ServiceResult[Dict]:
        """데이터 공유 설정 업데이트

        Returns:
            Tuple[성공여부, 설정정보, 에러메시지]
        """
        try:
            result = self.contract_repo.update_sharing_settings(contract_id, settings)
            return ServiceResult.ok(data=result)
        except ValueError as e:
            return ServiceResult.fail(str(e))

    # ========================================
    # 계약 상태 변경
    # ========================================

    def approve_contract(self, contract_id: int, user_id: int) -> ServiceResult[Dict]:
        """계약 승인

        Phase 1 Refactoring: Repository에서 비즈니스 로직 이동

        21번 원칙: 계약 승인 시 Employee.status = 'active' 연동
        23번 원칙: 계약 승인 시 PCC.employee_number 동기화

        개인 계정(personal):
        - 항상 새 Employee 생성 (회사별 분리, full_sync=True)
        - 전체 프로필 데이터 동기화 (기본 필드 + 관계형 데이터)
        - DataSharingSettings 자동 생성 (전체 공유 기본값)
        - employee_number 자동 동기화

        직원 계정(employee_sub):
        - 기존 Employee의 status만 active로 변경
        - organization_id를 계약 회사에 맞게 업데이트
        - employee_number 자동 동기화

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        from ..models.company import Company
        from ..services.sync_service import sync_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        user = User.query.get(contract.person_user_id)
        company = Company.query.get(contract.company_id)

        # 사전 검증 (employee_sub)
        if user and user.account_type == 'employee_sub':
            if not user.employee_id:
                return ServiceResult.fail("Employee 연결이 필요합니다. (User.employee_id NULL)")

            existing_employee = db.session.get(Employee, user.employee_id)
            if existing_employee and existing_employee.status == EmployeeStatus.RESIGNED:
                return ServiceResult.fail("퇴사한 직원은 재계약할 수 없습니다.")

        try:
            with atomic_transaction():
                contract.approve(user_id)

                if user:
                    if user.account_type == 'personal':
                        # 개인 계정: 항상 새 Employee 생성 (회사별 분리)
                        profile = PersonalProfile.query.filter_by(user_id=user.id).first()
                        if profile:
                            # force_create=True: 기존 Employee 무시, 새로 생성
                            # full_sync=True: 전체 프로필 데이터 동기화
                            employee = sync_service._find_or_create_employee(
                                contract, profile,
                                full_sync=True,
                                force_create=True
                            )
                            if employee:
                                user.employee_id = employee.id
                                employee.status = EmployeeStatus.ACTIVE

                                # DataSharingSettings 생성 (전체 공유 기본값)
                                self._create_default_sharing_settings(contract_id)

                                # 관계형 데이터 동기화 실행
                                sync_service.set_current_user(user_id)
                                sync_service.sync_personal_to_employee(
                                    contract_id=contract_id,
                                    sync_type='initial'
                                )

                                # 23번 원칙: employee_number 동기화
                                if employee.employee_number:
                                    contract.employee_number = employee.employee_number
                    else:
                        # 직원 계정(employee_sub): 기존 Employee 상태 업데이트
                        if user.employee_id:
                            employee = db.session.get(Employee, user.employee_id)
                            if employee:
                                employee.status = EmployeeStatus.ACTIVE
                                # organization_id를 계약 회사에 맞게 업데이트
                                if company and company.root_organization_id:
                                    employee.organization_id = company.root_organization_id

                                # 23번 원칙: employee_number 동기화
                                if employee.employee_number:
                                    contract.employee_number = employee.employee_number

            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"계약 승인 실패: {str(e)}")

    def _create_default_sharing_settings(self, contract_id: int) -> DataSharingSettings:
        """기본 데이터 공유 설정 생성 (내부용)

        Args:
            contract_id: 계약 ID

        Returns:
            DataSharingSettings 모델
        """
        settings = DataSharingSettings.query.filter_by(
            contract_id=contract_id
        ).first()
        if not settings:
            settings = DataSharingSettings(
                contract_id=contract_id,
                share_basic_info=True,
                share_contact=True,
                share_education=True,
                share_career=True,
                share_certificates=True,
                share_languages=True,
                share_military=True,
                is_realtime_sync=False,
            )
            db.session.add(settings)
            db.session.flush()
        return settings

    def reject_contract(self, contract_id: int, user_id: int, reason: str = None) -> ServiceResult[Dict]:
        """계약 거절

        Phase 1 Refactoring: Repository에서 비즈니스 로직 이동

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        try:
            with atomic_transaction():
                contract.reject(user_id, reason)

            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"계약 거절 실패: {str(e)}")

    def terminate_contract(self, contract_id: int, user_id: int, reason: str = None) -> ServiceResult[Dict]:
        """계약 종료

        Phase 1 Refactoring: Repository에서 비즈니스 로직 이동

        21번 원칙: 계약 종료 시 Employee.status = 'terminated' 연동
        스냅샷 저장: termination_service를 통해 전체 인사기록 스냅샷 저장

        Returns:
            Tuple[성공여부, 결과, 에러메시지]
        """
        from ..services.termination_service import termination_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        try:
            # termination_service를 통해 종료 처리 (스냅샷 포함)
            termination_service.set_current_user(user_id)
            result = termination_service.terminate_contract(
                contract_id=contract_id,
                reason=reason,
                terminate_by_user_id=user_id
            )

            if not result.get('success'):
                return False, None, result.get('error', '계약 종료 실패')

            # 갱신된 계약 정보 조회
            contract = self.contract_repo.find_by_id(contract_id)
            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"계약 종료 실패: {str(e)}")

    # ========================================
    # 양측 동의 계약 종료 (Phase 5.3)
    # ========================================

    def request_termination(
        self,
        contract_id: int,
        requester_user_id: int,
        reason: str = None
    ) -> ServiceResult[Dict]:
        """계약 종료 요청 (양측 동의 프로세스 시작)

        개인 또는 법인 어느 쪽이든 종료 요청 가능.
        상대방이 승인해야 최종 종료됨.

        상태 변경: approved -> termination_requested

        Args:
            contract_id: 계약 ID
            requester_user_id: 요청자 User ID
            reason: 종료 요청 사유

        Returns:
            Tuple[성공여부, 계약정보, 에러메시지]
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        # 상태 검증
        if not ContractStatus.can_request_termination(contract.status):
            return ServiceResult.fail(f"현재 상태({contract.status})에서는 종료 요청을 할 수 없습니다.")

        # 요청자 권한 검증 (계약 당사자인지 확인)
        user = User.query.get(requester_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        # 개인 측 또는 법인 측인지 확인
        is_person_side = (contract.person_user_id == requester_user_id)
        is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')

        if not is_person_side and not is_company_side:
            return ServiceResult.fail("계약 당사자만 종료 요청을 할 수 있습니다.")

        try:
            with atomic_transaction():
                contract.status = ContractStatus.TERMINATION_REQUESTED
                contract.termination_requested_by = requester_user_id
                contract.termination_requested_at = db.func.now()
                contract.termination_reason = reason

            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"종료 요청 실패: {str(e)}")

    def approve_termination(
        self,
        contract_id: int,
        approver_user_id: int
    ) -> ServiceResult[Dict]:
        """계약 종료 승인 (상대방이 승인)

        종료 요청의 상대방만 승인 가능.
        승인 시 최종 계약 종료 처리.

        상태 변경: termination_requested -> terminated

        Args:
            contract_id: 계약 ID
            approver_user_id: 승인자 User ID

        Returns:
            Tuple[성공여부, 계약정보, 에러메시지]
        """
        from ..services.termination_service import termination_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        # 상태 검증
        if not ContractStatus.is_termination_requested(contract.status):
            return ServiceResult.fail(f"종료 요청 상태가 아닙니다. (현재: {contract.status})")

        # 승인자 권한 검증 (종료 요청자의 상대방인지 확인)
        user = User.query.get(approver_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        # 요청자가 개인이면 법인만 승인 가능, 요청자가 법인이면 개인만 승인 가능
        requester_is_person = (contract.termination_requested_by == contract.person_user_id)

        if requester_is_person:
            # 요청자가 개인 -> 법인만 승인 가능
            is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')
            if not is_company_side:
                return ServiceResult.fail("법인 관리자만 종료를 승인할 수 있습니다.")
        else:
            # 요청자가 법인 -> 개인만 승인 가능
            is_person_side = (contract.person_user_id == approver_user_id)
            if not is_person_side:
                return ServiceResult.fail("개인 계정 소유자만 종료를 승인할 수 있습니다.")

        try:
            # termination_service를 통해 최종 종료 처리 (스냅샷 포함)
            termination_service.set_current_user(approver_user_id)
            result = termination_service.terminate_contract(
                contract_id=contract_id,
                reason=contract.termination_reason,
                terminate_by_user_id=approver_user_id
            )

            if not result.get('success'):
                return False, None, result.get('error', '계약 종료 실패')

            # 갱신된 계약 정보 조회
            contract = self.contract_repo.find_by_id(contract_id)
            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"종료 승인 실패: {str(e)}")

    def reject_termination(
        self,
        contract_id: int,
        rejector_user_id: int,
        reason: str = None
    ) -> ServiceResult[Dict]:
        """계약 종료 거절 (상대방이 거절)

        종료 요청의 상대방만 거절 가능.
        거절 시 계약 상태가 approved로 원복됨.

        상태 변경: termination_requested -> approved

        Args:
            contract_id: 계약 ID
            rejector_user_id: 거절자 User ID
            reason: 거절 사유

        Returns:
            Tuple[성공여부, 계약정보, 에러메시지]
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        # 상태 검증
        if not ContractStatus.is_termination_requested(contract.status):
            return ServiceResult.fail(f"종료 요청 상태가 아닙니다. (현재: {contract.status})")

        # 거절자 권한 검증 (종료 요청자의 상대방인지 확인)
        user = User.query.get(rejector_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        # 요청자가 개인이면 법인만 거절 가능, 요청자가 법인이면 개인만 거절 가능
        requester_is_person = (contract.termination_requested_by == contract.person_user_id)

        if requester_is_person:
            # 요청자가 개인 -> 법인만 거절 가능
            is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')
            if not is_company_side:
                return ServiceResult.fail("법인 관리자만 종료를 거절할 수 있습니다.")
        else:
            # 요청자가 법인 -> 개인만 거절 가능
            is_person_side = (contract.person_user_id == rejector_user_id)
            if not is_person_side:
                return ServiceResult.fail("개인 계정 소유자만 종료를 거절할 수 있습니다.")

        try:
            with atomic_transaction():
                contract.status = ContractStatus.APPROVED
                contract.termination_rejected_by = rejector_user_id
                contract.termination_rejected_at = db.func.now()
                contract.termination_rejection_reason = reason
                # 종료 요청 관련 필드 초기화
                contract.termination_requested_by = None
                contract.termination_requested_at = None
                contract.termination_reason = None

            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"종료 거절 실패: {str(e)}")

    def get_termination_pending_contracts(
        self,
        user_id: int
    ) -> List[Dict]:
        """종료 요청 대기 중인 계약 목록 조회

        현재 사용자가 승인/거절해야 하는 종료 요청 목록

        Args:
            user_id: 사용자 ID

        Returns:
            종료 요청 대기 중인 계약 목록
        """
        user = User.query.get(user_id)
        if not user:
            return []

        # termination_requested 상태인 계약 조회
        contracts = PersonCorporateContract.query.filter_by(
            status=ContractStatus.TERMINATION_REQUESTED
        ).all()

        result = []
        for contract in contracts:
            # 요청자가 누구인지에 따라 승인 권한 확인
            requester_is_person = (contract.termination_requested_by == contract.person_user_id)

            if requester_is_person:
                # 개인이 요청 -> 법인 관리자만 승인 가능
                if user.company_id == contract.company_id and user.account_type == 'corporate':
                    result.append(contract.to_dict(include_relations=True))
            else:
                # 법인이 요청 -> 개인만 승인 가능
                if contract.person_user_id == user_id:
                    result.append(contract.to_dict(include_relations=True))

        return result


# 싱글톤 인스턴스
contract_service = ContractService()
