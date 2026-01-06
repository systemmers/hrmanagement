"""
상태 상수 모듈

비즈니스 로직에서 사용되는 상태값들의 SSOT (Single Source of Truth)
Magic String 대신 이 모듈의 상수를 사용해야 합니다.

Usage:
    from app.shared.constants.status import ContractStatus, EmployeeStatus

    if contract.status == ContractStatus.APPROVED:
        ...

    employee.status = EmployeeStatus.ACTIVE
"""


class ContractStatus:
    """
    계약 상태 (PersonCorporateContract.status)

    SSOT (Single Source of Truth) for contract status values.
    Phase 30: SSOT 통합 - DB 현실에 맞춤 (PENDING='requested')

    DB에 저장되는 실제 값: 'requested', 'approved', 'rejected',
                         'terminated', 'termination_requested', 'expired'
    """
    # 기본 상태
    REQUESTED = 'requested'    # 계약 요청 대기 (DB 실제 값)
    PENDING = 'requested'      # 하위 호환 별칭 (REQUESTED와 동일)
    APPROVED = 'approved'      # 계약 승인/완료
    REJECTED = 'rejected'      # 계약 거절
    TERMINATED = 'terminated'  # 계약 종료
    TERMINATION_REQUESTED = 'termination_requested'  # 계약 종료 요청 (양측 동의 대기)
    EXPIRED = 'expired'        # 계약 만료

    # 상태 그룹
    ACTIVE_STATUSES = [APPROVED, TERMINATION_REQUESTED]  # 종료 요청 중에도 계약은 유효
    INACTIVE_STATUSES = [REJECTED, TERMINATED, EXPIRED]
    ALL_STATUSES = [REQUESTED, APPROVED, REJECTED, TERMINATED, TERMINATION_REQUESTED, EXPIRED]

    # 재계약 가능 상태 (기존 계약이 이 상태일 때 새 계약 가능)
    RECONTRACTABLE = [REJECTED, TERMINATED, EXPIRED]

    # 계약갱신 가능 상태


    # 종료 요청 가능 상태
    TERMINABLE = [APPROVED]

    # 상태 전이 규칙 (Phase 30)
    # key: 현재 상태, value: 전이 가능한 상태 목록
    TRANSITIONS = {
        'requested': ['approved', 'rejected'],
        'approved': ['termination_requested', 'terminated'],
        'termination_requested': ['approved', 'terminated'],  # 거절 시 approved 복귀
        'rejected': [],      # 최종 상태
        'terminated': [],    # 최종 상태
        'expired': [],       # 최종 상태
    }

    @classmethod
    def is_active(cls, status: str) -> bool:
        """활성 상태인지 확인"""
        return status in cls.ACTIVE_STATUSES

    @classmethod
    def can_recontract(cls, status: str) -> bool:
        """재계약 가능 상태인지 확인"""
        return status in cls.RECONTRACTABLE

    @classmethod
    def can_request_termination(cls, status: str) -> bool:
        """종료 요청 가능 상태인지 확인"""
        return status in cls.TERMINABLE

    @classmethod
    def is_termination_requested(cls, status: str) -> bool:
        """종료 요청 상태인지 확인"""
        return status == cls.TERMINATION_REQUESTED

    @classmethod
    def validate_transition(cls, from_status: str, to_status: str) -> tuple:
        """
        상태 전이 검증 (Phase 30)

        Args:
            from_status: 현재 상태
            to_status: 전이하려는 상태

        Returns:
            (bool, str): (전이 가능 여부, 오류 메시지)
        """
        allowed = cls.TRANSITIONS.get(from_status, [])
        if to_status not in allowed:
            return False, f"'{from_status}'에서 '{to_status}'로 전이할 수 없습니다"
        return True, ""

    @classmethod
    def get_allowed_transitions(cls, current_status: str) -> list:
        """
        현재 상태에서 가능한 전이 목록 (Phase 30)

        Args:
            current_status: 현재 상태

        Returns:
            list: 전이 가능한 상태 목록
        """
        return cls.TRANSITIONS.get(current_status, [])


class EmployeeStatus:
    """직원 상태 (Employee.status)"""
    ACTIVE = 'active'                      # 정상 재직
    PENDING_INFO = 'pending_info'          # 정보 입력 대기 (계정 발급 후)
    PENDING_CONTRACT = 'pending_contract'  # 계약 요청 대기 (정보 입력 완료 후)
    RESIGNED = 'resigned'                  # 퇴사

    # 상태 그룹
    WORKING_STATUSES = [ACTIVE, PENDING_INFO, PENDING_CONTRACT]  # 재직 중
    ALL_STATUSES = [ACTIVE, PENDING_INFO, PENDING_CONTRACT, RESIGNED]

    @classmethod
    def is_working(cls, status: str) -> bool:
        """재직 중인지 확인"""
        return status in cls.WORKING_STATUSES

    @classmethod
    def is_resigned(cls, status: str) -> bool:
        """퇴사 상태인지 확인"""
        return status == cls.RESIGNED


class AccountStatus:
    """계정 상태"""
    NONE = 'none'              # 계정 없음
    REQUESTED = 'requested'    # 계정 요청됨
    PENDING = 'pending'        # 계정 대기

    ALL_STATUSES = [NONE, REQUESTED, PENDING]
