"""
Contract Workflow Service

계약 상태 변경 관련 비즈니스 로직을 처리합니다.
- 계약 생성/요청
- 계약 승인/거절/종료
- 양측 동의 계약 종료

Phase 30: 레이어 분리 - Model.query, db.session 직접 사용 제거
"""
from typing import Dict, Optional, List
from datetime import datetime, timezone

from app.shared.constants.session_keys import AccountType
from app.shared.constants.status import ContractStatus, EmployeeStatus
from app.shared.utils.transaction import atomic_transaction
from app.shared.base import ServiceResult


class ContractWorkflowService:
    """계약 워크플로우 서비스"""

    # ========================================
    # Repository Property 주입 (Phase 30)
    # ========================================

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        from app.extensions import person_contract_repo
        return person_contract_repo

    @property
    def user_repo(self):
        """지연 초기화된 사용자 Repository"""
        from app.extensions import user_repo
        return user_repo

    @property
    def company_repo(self):
        """지연 초기화된 법인 Repository"""
        from app.domains.company.repositories.company_repository import company_repository
        return company_repository

    @property
    def employee_repo(self):
        """지연 초기화된 직원 Repository"""
        from app.extensions import employee_repo
        return employee_repo

    @property
    def personal_profile_repo(self):
        """지연 초기화된 개인 프로필 Repository"""
        from app.extensions import personal_profile_repo
        return personal_profile_repo

    @property
    def data_sharing_settings_repo(self):
        """지연 초기화된 데이터 공유 설정 Repository"""
        from app.extensions import data_sharing_settings_repo
        return data_sharing_settings_repo

    # ========================================
    # 계약 생성/요청
    # ========================================

    def create_contract_request(
        self,
        person_email: str,
        company_id: int,
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None,
        contract_start_date=None,
        contract_end_date=None
    ) -> ServiceResult[Dict]:
        """계약 요청 생성 (법인 -> 개인/직원)"""
        # Phase 30: Repository 사용으로 변경
        person_user = self.user_repo.find_by_email(person_email)

        if not person_user or person_user.account_type not in AccountType.personal_types():
            return ServiceResult.fail('해당 이메일의 계정을 찾을 수 없습니다.')

        try:
            contract = self.contract_repo.create_contract_request(
                person_user_id=person_user.id,
                company_id=company_id,
                requested_by='company',
                contract_type=contract_type,
                position=position,
                department=department,
                notes=notes,
                contract_start_date=contract_start_date,
                contract_end_date=contract_end_date
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
        notes: str = None,
        contract_start_date=None,
        contract_end_date=None
    ) -> ServiceResult[Dict]:
        """직원/개인 계정에 대한 계약 요청 (21번 원칙)"""
        # Phase 30: Repository 사용으로 변경
        employee_user = self.user_repo.find_by_id(employee_user_id)

        if not employee_user or employee_user.account_type not in AccountType.personal_types():
            return ServiceResult.fail('해당 계정을 찾을 수 없습니다.')

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
                notes=notes,
                contract_start_date=contract_start_date,
                contract_end_date=contract_end_date
            )
            return ServiceResult.ok(data=contract)
        except ValueError as e:
            return ServiceResult.fail(str(e))

    # ========================================
    # 계약 상태 변경
    # ========================================

    def approve_contract(self, contract_id: int, user_id: int) -> ServiceResult[Dict]:
        """계약 승인

        21번 원칙: 계약 승인 시 Employee.status = 'active' 연동
        23번 원칙: 계약 승인 시 PCC.employee_number 동기화
        Bug 1 Fix: 동일 회사 활성 계약 중복 방지
        Bug 2 Fix: 사직 후 재입사 시 새 Employee + 새 사번 생성

        Phase 30: Repository 사용으로 변경
        """
        from app.domains.sync.services.sync_service import sync_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        # Bug 1 Fix: 이미 활성 계약이 있는지 체크
        existing_active = self.contract_repo.get_active_contract_by_person_and_company(
            contract.person_user_id,
            contract.company_id
        )
        if existing_active and existing_active.id != contract_id:
            return ServiceResult.fail("이미 해당 회사와 활성 계약이 존재합니다.")

        # Phase 30: Repository 사용
        user = self.user_repo.find_by_id(contract.person_user_id)
        company = self.company_repo.find_by_id(contract.company_id)

        # 재입사 플래그 (Bug 2)
        needs_reentry = False

        # 사전 검증 (employee_sub)
        if user and user.account_type == 'employee_sub':
            if not user.employee_id:
                return ServiceResult.fail("Employee 연결이 필요합니다. (User.employee_id NULL)")

            # Phase 30: Repository 사용
            existing_employee = self.employee_repo.find_by_id(user.employee_id)
            if existing_employee and existing_employee.status == EmployeeStatus.RESIGNED:
                # Bug 2 Fix: 사직 후 재입사 - 새 Employee 생성 필요
                needs_reentry = True

        try:
            with atomic_transaction():
                contract.approve(user_id)

                if user:
                    if user.account_type == 'personal':
                        # Phase 30: Repository 사용
                        profile = self.personal_profile_repo.find_by_user_id(user.id)
                        if profile:
                            employee = sync_service._find_or_create_employee(
                                contract, profile,
                                full_sync=True,
                                force_create=True
                            )
                            if employee:
                                user.employee_id = employee.id
                                employee.status = EmployeeStatus.ACTIVE

                                self._create_default_sharing_settings(contract_id)

                                sync_service.set_current_user(user_id)
                                sync_service.sync_personal_to_employee(
                                    contract_id=contract_id,
                                    sync_type='initial',
                                    commit=False  # Phase 30: 외부 트랜잭션에 위임
                                )

                                if employee.employee_number:
                                    contract.employee_number = employee.employee_number
                    else:
                        # employee_sub 계정 처리
                        if needs_reentry:
                            # Bug 2 Fix: 사직 후 재입사 - 새 Employee + 새 사번 생성
                            new_employee = self._create_new_employee_for_reentry(
                                user=user,
                                company_id=contract.company_id,
                                contract=contract,
                                company=company
                            )
                            user.employee_id = new_employee.id
                            contract.employee_number = new_employee.employee_number
                        elif user.employee_id:
                            # Phase 30: Repository 사용
                            employee = self.employee_repo.find_by_id(user.employee_id)
                            if employee:
                                employee.status = EmployeeStatus.ACTIVE
                                if company and company.root_organization_id:
                                    employee.organization_id = company.root_organization_id

                                if employee.employee_number:
                                    contract.employee_number = employee.employee_number

            return ServiceResult.ok(data=contract.to_dict(include_relations=True))
        except Exception as e:
            return ServiceResult.fail(f"계약 승인 실패: {str(e)}")

    def _create_default_sharing_settings(self, contract_id: int):
        """기본 데이터 공유 설정 생성 (내부용)

        Phase 30: Repository 사용으로 변경
        """
        # Phase 30: Repository 사용
        settings = self.data_sharing_settings_repo.find_by_contract_id(contract_id)
        if not settings:
            settings = self.data_sharing_settings_repo.create_for_contract(
                contract_id=contract_id,
                share_basic_info=True,
                share_contact=True,
                share_education=True,
                share_career=True,
                share_certificates=True,
                share_languages=True,
                share_military=True,
                is_realtime_sync=False,
                commit=False  # 외부 트랜잭션에 위임
            )
        return settings

    def _create_new_employee_for_reentry(
        self,
        user,
        company_id: int,
        contract,
        company=None
    ):
        """사직 후 재입사: 새 Employee + 새 사번 생성

        Phase 30: Repository 사용으로 변경

        Args:
            user: User 모델
            company_id: 법인 ID
            contract: PersonCorporateContract 모델
            company: Company 모델 (organization_id 설정용)

        Returns:
            새로 생성된 Employee 모델
        """
        from app.shared.utils.employee_number import generate_employee_number

        # 새 사번 생성
        new_number = generate_employee_number()

        # Phase 30: Repository 사용 - Profile에서 이름 조회
        profile = self.personal_profile_repo.find_by_user_id(user.id)
        name = profile.name if profile else user.username

        # 조직 ID 설정
        organization_id = None
        if company and company.root_organization_id:
            organization_id = company.root_organization_id

        # Phase 30: Repository 사용 - 새 Employee 생성
        new_employee = self.employee_repo.create({
            'company_id': company_id,
            'employee_number': new_number,
            'name': name,
            'status': EmployeeStatus.ACTIVE,
            'organization_id': organization_id,
        }, commit=False)

        return new_employee

    def reject_contract(self, contract_id: int, user_id: int, reason: str = None) -> ServiceResult[Dict]:
        """계약 거절"""
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

        21번 원칙: 계약 종료 시 Employee.status = 'terminated' 연동
        스냅샷 저장: termination_service를 통해 전체 인사기록 스냅샷 저장
        """
        from app.domains.sync.services.termination_service import termination_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        try:
            termination_service.set_current_user(user_id)
            result = termination_service.terminate_contract(
                contract_id=contract_id,
                reason=reason,
                terminate_by_user_id=user_id
            )

            if not result.get('success'):
                return ServiceResult.fail(result.get('error', '계약 종료 실패'))

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

        Phase 30: Repository 사용으로 변경
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        if not ContractStatus.can_request_termination(contract.status):
            return ServiceResult.fail(f"현재 상태({contract.status})에서는 종료 요청을 할 수 없습니다.")

        # Phase 30: Repository 사용
        user = self.user_repo.find_by_id(requester_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        is_person_side = (contract.person_user_id == requester_user_id)
        is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')

        if not is_person_side and not is_company_side:
            return ServiceResult.fail("계약 당사자만 종료 요청을 할 수 있습니다.")

        try:
            with atomic_transaction():
                contract.status = ContractStatus.TERMINATION_REQUESTED
                contract.termination_requested_by = requester_user_id
                # Phase 30: db.func.now() 대신 Python datetime 사용
                contract.termination_requested_at = datetime.now(timezone.utc)
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

        Phase 30: Repository 사용으로 변경
        """
        from app.domains.sync.services.termination_service import termination_service

        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        if not ContractStatus.is_termination_requested(contract.status):
            return ServiceResult.fail(f"종료 요청 상태가 아닙니다. (현재: {contract.status})")

        # Phase 30: Repository 사용
        user = self.user_repo.find_by_id(approver_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        requester_is_person = (contract.termination_requested_by == contract.person_user_id)

        if requester_is_person:
            is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')
            if not is_company_side:
                return ServiceResult.fail("법인 관리자만 종료를 승인할 수 있습니다.")
        else:
            is_person_side = (contract.person_user_id == approver_user_id)
            if not is_person_side:
                return ServiceResult.fail("개인 계정 소유자만 종료를 승인할 수 있습니다.")

        try:
            termination_service.set_current_user(approver_user_id)
            result = termination_service.terminate_contract(
                contract_id=contract_id,
                reason=contract.termination_reason,
                terminate_by_user_id=approver_user_id
            )

            if not result.get('success'):
                return ServiceResult.fail(result.get('error', '계약 종료 실패'))

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

        Phase 30: Repository 사용으로 변경
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return ServiceResult.fail("계약을 찾을 수 없습니다.")

        if not ContractStatus.is_termination_requested(contract.status):
            return ServiceResult.fail(f"종료 요청 상태가 아닙니다. (현재: {contract.status})")

        # Phase 30: Repository 사용
        user = self.user_repo.find_by_id(rejector_user_id)
        if not user:
            return ServiceResult.fail("사용자를 찾을 수 없습니다.")

        requester_is_person = (contract.termination_requested_by == contract.person_user_id)

        if requester_is_person:
            is_company_side = (user.company_id == contract.company_id and user.account_type == 'corporate')
            if not is_company_side:
                return ServiceResult.fail("법인 관리자만 종료를 거절할 수 있습니다.")
        else:
            is_person_side = (contract.person_user_id == rejector_user_id)
            if not is_person_side:
                return ServiceResult.fail("개인 계정 소유자만 종료를 거절할 수 있습니다.")

        try:
            with atomic_transaction():
                contract.status = ContractStatus.APPROVED
                contract.termination_rejected_by = rejector_user_id
                # Phase 30: db.func.now() 대신 Python datetime 사용
                contract.termination_rejected_at = datetime.now(timezone.utc)
                contract.termination_rejection_reason = reason
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

        Phase 30: Repository 사용으로 변경
        """
        # Phase 30: Repository 사용
        user = self.user_repo.find_by_id(user_id)
        if not user:
            return []

        # Phase 30: Repository 사용
        contracts = self.contract_repo.find_by_status(ContractStatus.TERMINATION_REQUESTED)

        result = []
        for contract in contracts:
            requester_is_person = (contract.termination_requested_by == contract.person_user_id)

            if requester_is_person:
                if user.company_id == contract.company_id and user.account_type == 'corporate':
                    result.append(contract.to_dict(include_relations=True))
            else:
                if contract.person_user_id == user_id:
                    result.append(contract.to_dict(include_relations=True))

        return result

    # ========================================
    # 직원 퇴사 연동 (Phase 27)
    # ========================================

    def terminate_contracts_by_employee_number(
        self,
        employee_number: str,
        company_id: int,
        reason: str = None,
        terminate_by_user_id: int = None
    ) -> ServiceResult[Dict]:
        """직원 사번으로 활성 계약 종료

        Phase 30: Repository 사용으로 변경

        직원 편집 폼에서 resignation_date 설정 시 호출됩니다.
        해당 직원의 모든 활성 계약(approved, termination_requested)을 종료합니다.

        Args:
            employee_number: 직원 사번
            company_id: 법인 ID
            reason: 종료 사유
            terminate_by_user_id: 종료 처리자 ID

        Returns:
            ServiceResult with terminated_count
        """
        # Phase 30: Repository 사용 - 활성 계약 조회
        contracts = self.contract_repo.find_active_by_employee_number_and_company(
            employee_number=employee_number,
            company_id=company_id
        )

        if not contracts:
            return ServiceResult.ok(data={'terminated_count': 0, 'message': '종료할 활성 계약이 없습니다.'})

        try:
            with atomic_transaction():
                for contract in contracts:
                    contract.status = ContractStatus.TERMINATED
                    contract.terminated_at = datetime.now(timezone.utc)
                    contract.termination_reason = reason or '직원 편집에서 퇴사 처리'
                    if terminate_by_user_id:
                        contract.terminated_by = terminate_by_user_id

            return ServiceResult.ok(data={
                'terminated_count': len(contracts),
                'message': f'{len(contracts)}개의 계약이 종료되었습니다.'
            })
        except Exception as e:
            return ServiceResult.fail(f"계약 종료 실패: {str(e)}")


# 싱글톤 인스턴스
contract_workflow_service = ContractWorkflowService()
