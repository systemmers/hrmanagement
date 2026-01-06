"""
API 헬퍼 함수 테스트

API 응답 형식 표준화 기능 테스트
"""
import pytest
from app.shared.utils.api_helpers import (
    api_success,
    api_error,
    api_not_found,
    api_unauthorized,
    api_forbidden,
    api_validation_error,
    api_server_error
)


class TestApiSuccess:
    """성공 응답 테스트"""

    def test_api_success_with_data(self, app):
        """데이터와 함께 성공 응답"""
        with app.app_context():
            response, status_code = api_success({'user': 'test'})

            assert status_code == 200
            assert response.json['success'] is True
            assert response.json['data'] == {'user': 'test'}

    def test_api_success_with_message(self, app):
        """메시지와 함께 성공 응답"""
        with app.app_context():
            response, status_code = api_success(message='완료되었습니다')

            assert status_code == 200
            assert response.json['success'] is True
            assert response.json['message'] == '완료되었습니다'

    def test_api_success_with_custom_status(self, app):
        """커스텀 상태 코드와 함께 성공 응답"""
        with app.app_context():
            response, status_code = api_success({'id': 123}, status_code=201)

            assert status_code == 201
            assert response.json['success'] is True
            assert response.json['data'] == {'id': 123}

    def test_api_success_empty(self, app):
        """빈 성공 응답"""
        with app.app_context():
            response, status_code = api_success()

            assert status_code == 200
            assert response.json['success'] is True
            assert 'data' not in response.json


class TestApiError:
    """에러 응답 테스트"""

    def test_api_error_basic(self, app):
        """기본 에러 응답"""
        with app.app_context():
            response, status_code = api_error('에러 발생')

            assert status_code == 400
            assert response.json['success'] is False
            assert response.json['error'] == '에러 발생'

    def test_api_error_with_status(self, app):
        """커스텀 상태 코드와 함께 에러 응답"""
        with app.app_context():
            response, status_code = api_error('권한 없음', 403)

            assert status_code == 403
            assert response.json['error'] == '권한 없음'

    def test_api_error_with_errors(self, app):
        """상세 에러와 함께 에러 응답"""
        with app.app_context():
            errors = {'email': '필수 항목', 'password': '너무 짧음'}
            response, status_code = api_error('검증 실패', errors=errors)

            assert status_code == 400
            assert response.json['errors'] == errors


class TestApiNotFound:
    """404 응답 테스트"""

    def test_api_not_found_default(self, app):
        """기본 404 응답"""
        with app.app_context():
            response, status_code = api_not_found()

            assert status_code == 404
            assert '리소스' in response.json['error']

    def test_api_not_found_custom(self, app):
        """커스텀 리소스명과 함께 404 응답"""
        with app.app_context():
            response, status_code = api_not_found('사용자')

            assert status_code == 404
            assert '사용자' in response.json['error']


class TestApiUnauthorized:
    """401 응답 테스트"""

    def test_api_unauthorized_default(self, app):
        """기본 401 응답"""
        with app.app_context():
            response, status_code = api_unauthorized()

            assert status_code == 401
            assert '로그인' in response.json['error']

    def test_api_unauthorized_custom(self, app):
        """커스텀 메시지와 함께 401 응답"""
        with app.app_context():
            response, status_code = api_unauthorized('인증 필요')

            assert status_code == 401
            assert response.json['error'] == '인증 필요'


class TestApiForbidden:
    """403 응답 테스트"""

    def test_api_forbidden_default(self, app):
        """기본 403 응답"""
        with app.app_context():
            response, status_code = api_forbidden()

            assert status_code == 403
            assert '권한' in response.json['error']

    def test_api_forbidden_custom(self, app):
        """커스텀 메시지와 함께 403 응답"""
        with app.app_context():
            response, status_code = api_forbidden('접근 거부')

            assert status_code == 403
            assert response.json['error'] == '접근 거부'


class TestApiValidationError:
    """422 응답 테스트"""

    def test_api_validation_error(self, app):
        """검증 에러 응답"""
        with app.app_context():
            errors = {
                'email': '이메일 형식',
                'password': '8자 이상'
            }
            response, status_code = api_validation_error(errors)

            assert status_code == 422
            assert response.json['success'] is False
            assert response.json['errors'] == errors


class TestApiServerError:
    """500 응답 테스트"""

    def test_api_server_error_default(self, app):
        """기본 500 응답"""
        with app.app_context():
            response, status_code = api_server_error()

            assert status_code == 500
            assert '서버' in response.json['error']

    def test_api_server_error_custom(self, app):
        """커스텀 메시지와 함께 500 응답"""
        with app.app_context():
            response, status_code = api_server_error('DB 오류')

            assert status_code == 500
            assert response.json['error'] == 'DB 오류'

