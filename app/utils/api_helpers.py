"""
API 응답 헬퍼 모듈

API 응답 형식을 표준화합니다.
Phase 6: 백엔드 리팩토링
"""
from typing import Any, Optional, Dict
from flask import jsonify


def api_success(data: Any = None, message: str = None, status_code: int = 200):
    """
    성공 API 응답 생성

    Args:
        data: 응답 데이터
        message: 성공 메시지 (선택)
        status_code: HTTP 상태 코드 (기본 200)

    Returns:
        Tuple[Response, int]: (JSON 응답, 상태 코드)

    사용 예:
        return api_success({'user': user_data})
        return api_success(message='처리 완료')
        return api_success({'id': 123}, status_code=201)
    """
    response = {'success': True}

    if data is not None:
        response['data'] = data

    if message:
        response['message'] = message

    return jsonify(response), status_code


def api_error(message: str, status_code: int = 400, errors: Dict = None):
    """
    에러 API 응답 생성

    Args:
        message: 에러 메시지
        status_code: HTTP 상태 코드 (기본 400)
        errors: 상세 에러 정보 (필드별 에러 등)

    Returns:
        Tuple[Response, int]: (JSON 응답, 상태 코드)

    사용 예:
        return api_error('유효하지 않은 요청입니다.')
        return api_error('권한이 없습니다.', 403)
        return api_error('유효성 검사 실패', errors={'email': '이메일 형식이 아닙니다.'})
    """
    response = {
        'success': False,
        'error': message
    }

    if errors:
        response['errors'] = errors

    return jsonify(response), status_code


def api_not_found(resource: str = '리소스'):
    """
    404 Not Found 응답 생성

    Args:
        resource: 찾지 못한 리소스 이름

    Returns:
        Tuple[Response, int]: (JSON 응답, 404)
    """
    return api_error(f'{resource}를 찾을 수 없습니다.', 404)


def api_unauthorized(message: str = '로그인이 필요합니다.'):
    """
    401 Unauthorized 응답 생성

    Args:
        message: 인증 에러 메시지

    Returns:
        Tuple[Response, int]: (JSON 응답, 401)
    """
    return api_error(message, 401)


def api_forbidden(message: str = '권한이 없습니다.'):
    """
    403 Forbidden 응답 생성

    Args:
        message: 권한 에러 메시지

    Returns:
        Tuple[Response, int]: (JSON 응답, 403)
    """
    return api_error(message, 403)


def api_validation_error(errors: Dict):
    """
    422 Validation Error 응답 생성

    Args:
        errors: 필드별 에러 딕셔너리

    Returns:
        Tuple[Response, int]: (JSON 응답, 422)

    사용 예:
        return api_validation_error({
            'email': '이메일 형식이 아닙니다.',
            'password': '비밀번호는 8자 이상이어야 합니다.'
        })
    """
    return api_error('유효성 검사 실패', 422, errors)


def api_server_error(message: str = '서버 오류가 발생했습니다.'):
    """
    500 Internal Server Error 응답 생성

    Args:
        message: 서버 에러 메시지

    Returns:
        Tuple[Response, int]: (JSON 응답, 500)
    """
    return api_error(message, 500)
