"""
커스텀 예외 클래스 테스트

HR Management 시스템의 커스텀 예외 클래스들의 동작 확인
"""
import pytest
from app.shared.utils.exceptions import (
    HRMException,
    ValidationError,
    NotFoundError,
    PermissionDeniedError,
    AuthenticationError,
    ConflictError,
    BusinessRuleError,
    ExternalServiceError
)


class TestHRMException:
    """HRMException 기본 예외 클래스 테스트"""

    def test_basic_exception(self):
        """기본 예외 생성"""
        exc = HRMException("테스트 에러")
        assert exc.message == "테스트 에러"
        assert exc.code is None
        assert exc.details == {}

    def test_exception_with_code(self):
        """코드가 포함된 예외"""
        exc = HRMException("테스트 에러", code="TEST_ERROR")
        assert exc.message == "테스트 에러"
        assert exc.code == "TEST_ERROR"

    def test_exception_with_details(self):
        """상세 정보가 포함된 예외"""
        details = {"field": "name", "value": "test"}
        exc = HRMException("테스트 에러", details=details)
        assert exc.details == details

    def test_exception_to_dict(self):
        """예외를 딕셔너리로 변환"""
        exc = HRMException("테스트 에러", code="TEST", details={"key": "value"})
        result = exc.to_dict()
        assert result["message"] == "테스트 에러"
        assert result["code"] == "TEST"
        assert result["details"] == {"key": "value"}

    def test_exception_to_dict_minimal(self):
        """최소 정보만으로 딕셔너리 변환"""
        exc = HRMException("테스트 에러")
        result = exc.to_dict()
        assert result == {"message": "테스트 에러"}
        assert "code" not in result
        assert "details" not in result


class TestValidationError:
    """ValidationError 테스트"""

    def test_default_message(self):
        """기본 메시지"""
        exc = ValidationError()
        assert exc.message == "입력값이 올바르지 않습니다."
        assert exc.code == "VALIDATION_ERROR"

    def test_custom_message(self):
        """커스텀 메시지"""
        exc = ValidationError("이메일 형식이 올바르지 않습니다.")
        assert exc.message == "이메일 형식이 올바르지 않습니다."

    def test_with_field(self):
        """필드 정보 포함"""
        exc = ValidationError("필수 필드입니다.", field="name")
        assert exc.field == "name"
        assert exc.details["field"] == "name"

    def test_to_dict(self):
        """딕셔너리 변환"""
        exc = ValidationError("이메일 형식 오류", field="email")
        result = exc.to_dict()
        assert result["code"] == "VALIDATION_ERROR"
        assert result["details"]["field"] == "email"


class TestNotFoundError:
    """NotFoundError 테스트"""

    def test_default_resource(self):
        """기본 리소스"""
        exc = NotFoundError()
        assert "리소스" in exc.message
        assert exc.code == "NOT_FOUND"

    def test_custom_resource(self):
        """커스텀 리소스"""
        exc = NotFoundError("직원")
        assert exc.message == "직원을(를) 찾을 수 없습니다."
        assert exc.resource == "직원"

    def test_with_resource_id(self):
        """리소스 ID 포함"""
        exc = NotFoundError("계약", resource_id=123)
        assert exc.resource_id == 123
        assert exc.details["resource_id"] == 123

    def test_to_dict(self):
        """딕셔너리 변환"""
        exc = NotFoundError("회사", resource_id=456)
        result = exc.to_dict()
        assert result["code"] == "NOT_FOUND"
        assert result["details"]["resource"] == "회사"
        assert result["details"]["resource_id"] == 456


class TestPermissionDeniedError:
    """PermissionDeniedError 테스트"""

    def test_default_message(self):
        """기본 메시지"""
        exc = PermissionDeniedError()
        assert exc.message == "권한이 없습니다."
        assert exc.code == "PERMISSION_DENIED"

    def test_custom_message(self):
        """커스텀 메시지"""
        exc = PermissionDeniedError("관리자만 접근 가능합니다.")
        assert exc.message == "관리자만 접근 가능합니다."

    def test_with_required_role(self):
        """필요 역할 정보 포함"""
        exc = PermissionDeniedError("관리자 권한 필요", required_role="admin")
        assert exc.required_role == "admin"
        assert exc.details["required_role"] == "admin"


class TestAuthenticationError:
    """AuthenticationError 테스트"""

    def test_default_message(self):
        """기본 메시지"""
        exc = AuthenticationError()
        assert exc.message == "인증이 필요합니다."
        assert exc.code == "AUTHENTICATION_ERROR"

    def test_custom_message(self):
        """커스텀 메시지"""
        exc = AuthenticationError("세션이 만료되었습니다.")
        assert exc.message == "세션이 만료되었습니다."


class TestConflictError:
    """ConflictError 테스트"""

    def test_default_message(self):
        """기본 메시지"""
        exc = ConflictError()
        assert exc.message == "리소스 충돌이 발생했습니다."
        assert exc.code == "CONFLICT"

    def test_custom_message(self):
        """커스텀 메시지"""
        exc = ConflictError("이미 존재하는 사용자입니다.")
        assert exc.message == "이미 존재하는 사용자입니다."

    def test_with_field(self):
        """필드 정보 포함"""
        exc = ConflictError("이메일 중복", field="email")
        assert exc.field == "email"
        assert exc.details["field"] == "email"


class TestBusinessRuleError:
    """BusinessRuleError 테스트"""

    def test_default_message(self):
        """기본 메시지"""
        exc = BusinessRuleError()
        assert exc.message == "비즈니스 규칙을 위반했습니다."
        assert exc.code == "BUSINESS_RULE_VIOLATION"

    def test_custom_message(self):
        """커스텀 메시지"""
        exc = BusinessRuleError("승인된 계약만 동기화할 수 있습니다.")
        assert "승인된 계약" in exc.message

    def test_with_rule(self):
        """규칙 정보 포함"""
        exc = BusinessRuleError("날짜 순서 오류", rule="date_order")
        assert exc.rule == "date_order"
        assert exc.details["rule"] == "date_order"


class TestExternalServiceError:
    """ExternalServiceError 테스트"""

    def test_default_service(self):
        """기본 서비스"""
        exc = ExternalServiceError()
        assert "외부 서비스" in exc.message
        assert exc.code == "EXTERNAL_SERVICE_ERROR"

    def test_custom_service(self):
        """커스텀 서비스"""
        exc = ExternalServiceError("AI 서비스")
        assert exc.message == "AI 서비스 연결에 실패했습니다."
        assert exc.service == "AI 서비스"

    def test_with_error_code(self):
        """에러 코드 포함"""
        exc = ExternalServiceError("이메일 서비스", error_code="SMTP_ERROR")
        assert exc.error_code == "SMTP_ERROR"
        assert exc.details["error_code"] == "SMTP_ERROR"


class TestExceptionRaising:
    """예외 발생 테스트"""

    def test_raise_validation_error(self):
        """ValidationError 발생"""
        with pytest.raises(ValidationError) as exc_info:
            raise ValidationError("테스트")
        assert "테스트" in str(exc_info.value)

    def test_raise_not_found_error(self):
        """NotFoundError 발생"""
        with pytest.raises(NotFoundError) as exc_info:
            raise NotFoundError("직원")
        assert "직원" in str(exc_info.value)

    def test_catch_hrm_exception(self):
        """HRMException으로 캐치"""
        with pytest.raises(HRMException):
            raise ValidationError("테스트")

    def test_catch_specific_exception(self):
        """구체적인 예외로 캐치"""
        with pytest.raises(ValidationError):
            raise ValidationError("테스트")

