"""
ServiceResult - 서비스 계층 표준 결과 클래스

서비스 메서드의 반환값을 표준화하여 일관된 에러 처리를 지원합니다.

사용 예시:
    # 성공 케이스
    return ServiceResult.ok(data={'id': 1, 'name': 'test'})
    return ServiceResult.ok(data=employee.to_dict(), message='직원 생성 완료')

    # 실패 케이스
    return ServiceResult.fail('직원을 찾을 수 없습니다.', error_code='NOT_FOUND')
    return ServiceResult.fail('권한이 없습니다.', error_code='FORBIDDEN')

    # Blueprint에서 사용
    result = employee_service.get_by_id(id)
    if not result.success:
        return jsonify({'error': result.message}), 400
    return jsonify(result.data)
"""
from dataclasses import dataclass, field
from typing import TypeVar, Generic, Optional, Dict, Any

T = TypeVar('T')


@dataclass
class ServiceResult(Generic[T]):
    """서비스 계층 표준 결과 클래스

    Attributes:
        success: 작업 성공 여부
        data: 반환 데이터 (성공 시)
        message: 결과 메시지 (성공/실패 모두 사용 가능)
        error_code: 에러 코드 (실패 시, 선택적)
        error_details: 추가 에러 정보 (디버깅용, 선택적)
    """
    success: bool
    data: Optional[T] = None
    message: Optional[str] = None
    error_code: Optional[str] = None
    error_details: Optional[Dict[str, Any]] = field(default=None)

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환 (API 응답용)"""
        result = {
            'success': self.success,
        }
        if self.data is not None:
            result['data'] = self.data
        if self.message is not None:
            result['message'] = self.message
        if self.error_code is not None:
            result['error_code'] = self.error_code
        if self.error_details is not None:
            result['error_details'] = self.error_details
        return result

    @classmethod
    def ok(
        cls,
        data: Optional[T] = None,
        message: Optional[str] = None
    ) -> 'ServiceResult[T]':
        """성공 결과 생성

        Args:
            data: 반환할 데이터
            message: 성공 메시지 (선택적)

        Returns:
            ServiceResult with success=True
        """
        return cls(success=True, data=data, message=message)

    @classmethod
    def fail(
        cls,
        message: str,
        error_code: Optional[str] = None,
        error_details: Optional[Dict[str, Any]] = None
    ) -> 'ServiceResult[T]':
        """실패 결과 생성

        Args:
            message: 에러 메시지
            error_code: 에러 코드 (NOT_FOUND, FORBIDDEN, VALIDATION_ERROR 등)
            error_details: 추가 에러 정보

        Returns:
            ServiceResult with success=False
        """
        return cls(
            success=False,
            message=message,
            error_code=error_code,
            error_details=error_details
        )

    @classmethod
    def not_found(cls, resource: str = '리소스') -> 'ServiceResult[T]':
        """리소스를 찾을 수 없음"""
        return cls.fail(
            message=f'{resource}을(를) 찾을 수 없습니다.',
            error_code='NOT_FOUND'
        )

    @classmethod
    def forbidden(cls, message: str = '권한이 없습니다.') -> 'ServiceResult[T]':
        """권한 없음"""
        return cls.fail(message=message, error_code='FORBIDDEN')

    @classmethod
    def validation_error(
        cls,
        message: str,
        errors: Optional[Dict[str, Any]] = None
    ) -> 'ServiceResult[T]':
        """유효성 검사 실패"""
        return cls.fail(
            message=message,
            error_code='VALIDATION_ERROR',
            error_details=errors
        )

    @classmethod
    def from_exception(cls, e: Exception) -> 'ServiceResult[T]':
        """예외에서 결과 생성"""
        return cls.fail(
            message=str(e),
            error_code='INTERNAL_ERROR',
            error_details={'exception_type': type(e).__name__}
        )

    def __bool__(self) -> bool:
        """Boolean 컨텍스트에서 success 값 반환

        if result: 와 같은 패턴 지원
        """
        return self.success
