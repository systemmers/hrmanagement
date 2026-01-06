"""
HR Management 커스텀 예외 클래스

비즈니스 로직 예외를 구체적으로 정의하여 명확한 에러 처리를 지원합니다.
Phase 27.3: 예외 처리 표준화
"""
from typing import Optional, Dict, Any


class HRMException(Exception):
    """
    HR Management 기본 예외 클래스

    모든 커스텀 예외의 기본 클래스입니다.

    Attributes:
        message: 에러 메시지
        code: 에러 코드 (선택)
        details: 추가 에러 정보 (선택)
    """

    def __init__(
        self,
        message: str = "시스템 오류가 발생했습니다.",
        code: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None
    ):
        self.message = message
        self.code = code
        self.details = details or {}
        super().__init__(self.message)

    def to_dict(self) -> Dict[str, Any]:
        """예외를 딕셔너리로 변환"""
        result = {"message": self.message}
        if self.code:
            result["code"] = self.code
        if self.details:
            result["details"] = self.details
        return result


class ValidationError(HRMException):
    """
    입력값 검증 오류

    폼 데이터, API 요청 등의 유효성 검사 실패 시 발생합니다.
    HTTP 400 Bad Request에 해당합니다.

    Examples:
        >>> raise ValidationError("이메일 형식이 올바르지 않습니다.")
        >>> raise ValidationError("필수 필드가 누락되었습니다.", field="name")
    """

    def __init__(
        self,
        message: str = "입력값이 올바르지 않습니다.",
        field: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        super().__init__(message, code="VALIDATION_ERROR", details=details)
        self.field = field


class NotFoundError(HRMException):
    """
    리소스 미발견 오류

    요청한 리소스(직원, 계약, 회사 등)를 찾을 수 없을 때 발생합니다.
    HTTP 404 Not Found에 해당합니다.

    Examples:
        >>> raise NotFoundError("직원")
        >>> raise NotFoundError("계약", resource_id=123)
    """

    def __init__(
        self,
        resource: str = "리소스",
        resource_id: Optional[int] = None,
        **kwargs
    ):
        message = f"{resource}을(를) 찾을 수 없습니다."
        details = kwargs.get("details", {})
        details["resource"] = resource
        if resource_id is not None:
            details["resource_id"] = resource_id
        super().__init__(message, code="NOT_FOUND", details=details)
        self.resource = resource
        self.resource_id = resource_id


class PermissionDeniedError(HRMException):
    """
    권한 부족 오류

    리소스에 대한 접근 권한이 없을 때 발생합니다.
    HTTP 403 Forbidden에 해당합니다.

    Examples:
        >>> raise PermissionDeniedError()
        >>> raise PermissionDeniedError("관리자만 접근 가능합니다.")
    """

    def __init__(
        self,
        message: str = "권한이 없습니다.",
        required_role: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if required_role:
            details["required_role"] = required_role
        super().__init__(message, code="PERMISSION_DENIED", details=details)
        self.required_role = required_role


class AuthenticationError(HRMException):
    """
    인증 오류

    로그인이 필요하거나 인증이 실패했을 때 발생합니다.
    HTTP 401 Unauthorized에 해당합니다.

    Examples:
        >>> raise AuthenticationError()
        >>> raise AuthenticationError("세션이 만료되었습니다.")
    """

    def __init__(
        self,
        message: str = "인증이 필요합니다.",
        **kwargs
    ):
        super().__init__(message, code="AUTHENTICATION_ERROR", **kwargs)


class ConflictError(HRMException):
    """
    충돌 오류

    리소스 충돌(중복 생성, 동시 수정 등)이 발생했을 때 사용합니다.
    HTTP 409 Conflict에 해당합니다.

    Examples:
        >>> raise ConflictError("이미 존재하는 사용자입니다.")
        >>> raise ConflictError("해당 이메일은 이미 사용 중입니다.", field="email")
    """

    def __init__(
        self,
        message: str = "리소스 충돌이 발생했습니다.",
        field: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if field:
            details["field"] = field
        super().__init__(message, code="CONFLICT", details=details)
        self.field = field


class BusinessRuleError(HRMException):
    """
    비즈니스 규칙 위반 오류

    비즈니스 로직 규칙을 위반했을 때 발생합니다.
    HTTP 400 Bad Request에 해당합니다.

    Examples:
        >>> raise BusinessRuleError("승인된 계약만 동기화할 수 있습니다.")
        >>> raise BusinessRuleError("퇴사일은 입사일 이후여야 합니다.", rule="date_order")
    """

    def __init__(
        self,
        message: str = "비즈니스 규칙을 위반했습니다.",
        rule: Optional[str] = None,
        **kwargs
    ):
        details = kwargs.get("details", {})
        if rule:
            details["rule"] = rule
        super().__init__(message, code="BUSINESS_RULE_VIOLATION", details=details)
        self.rule = rule


class ExternalServiceError(HRMException):
    """
    외부 서비스 오류

    외부 API(AI 서비스, 이메일 등) 호출 실패 시 발생합니다.
    HTTP 502 Bad Gateway 또는 503 Service Unavailable에 해당합니다.

    Examples:
        >>> raise ExternalServiceError("AI 서비스")
        >>> raise ExternalServiceError("이메일 서비스", error_code="SMTP_ERROR")
    """

    def __init__(
        self,
        service: str = "외부 서비스",
        error_code: Optional[str] = None,
        **kwargs
    ):
        message = f"{service} 연결에 실패했습니다."
        details = kwargs.get("details", {})
        details["service"] = service
        if error_code:
            details["error_code"] = error_code
        super().__init__(message, code="EXTERNAL_SERVICE_ERROR", details=details)
        self.service = service
        self.error_code = error_code


# SQLAlchemy 예외 re-export (편의성)
try:
    from sqlalchemy.exc import IntegrityError as DBIntegrityError
    from sqlalchemy.exc import OperationalError as DBOperationalError
except ImportError:
    # SQLAlchemy가 없는 환경에서도 import 가능하도록
    DBIntegrityError = None
    DBOperationalError = None


__all__ = [
    'HRMException',
    'ValidationError',
    'NotFoundError',
    'PermissionDeniedError',
    'AuthenticationError',
    'ConflictError',
    'BusinessRuleError',
    'ExternalServiceError',
    'DBIntegrityError',
    'DBOperationalError',
]
