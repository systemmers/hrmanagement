"""
상태 상수 모듈

비즈니스 로직에서 사용되는 상태값들의 SSOT (Single Source of Truth)
Magic String 대신 이 모듈의 상수를 사용해야 합니다.

Usage:
    from app.constants.status import ContractStatus, EmployeeStatus

    if contract.status == ContractStatus.APPROVED:
        ...

    employee.status = EmployeeStatus.ACTIVE
"""


class ContractStatus:
    """계약 상태 (PersonCorporateContract.status)"""
    PENDING = 'pending'        # 계약 요청 대기
    APPROVED = 'approved'      # 계약 승인/완료
    REJECTED = 'rejected'      # 계약 거절
    TERMINATED = 'terminated'  # 계약 종료
    TERMINATION_REQUESTED = 'termination_requested'  # 계약 종료 요청 (양측 동의 대기)

    # 상태 그룹
    ACTIVE_STATUSES = [APPROVED, TERMINATION_REQUESTED]  # 종료 요청 중에도 계약은 유효
    INACTIVE_STATUSES = [REJECTED, TERMINATED]
    ALL_STATUSES = [PENDING, APPROVED, REJECTED, TERMINATED, TERMINATION_REQUESTED]

    # 재계약 가능 상태 (기존 계약이 이 상태일 때 새 계약 가능)
    RECONTRACTABLE = [REJECTED, TERMINATED]

    # 종료 요청 가능 상태
    TERMINABLE = [APPROVED]

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


class EmployeeStatus:
    """직원 상태 (Employee.status)"""
    ACTIVE = 'active'              # 정상 재직
    PENDING_INFO = 'pending_info'  # 정보 입력 대기 (계약 승인 전)
    RESIGNED = 'resigned'          # 퇴사

    # 상태 그룹
    WORKING_STATUSES = [ACTIVE, PENDING_INFO]  # 재직 중
    ALL_STATUSES = [ACTIVE, PENDING_INFO, RESIGNED]

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
