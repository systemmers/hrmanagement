"""
ServiceResult 테스트

ServiceResult 패턴 테스트
"""
import pytest

from app.shared.base.service_result import ServiceResult


class TestServiceResult:
    """ServiceResult 테스트 클래스"""

    def test_ok_success(self):
        """성공 결과 생성"""
        result = ServiceResult.ok(data={'id': 1, 'name': '테스트'})

        assert result.success is True
        assert result.data == {'id': 1, 'name': '테스트'}
        assert result.message is None

    def test_fail_error(self):
        """실패 결과 생성"""
        result = ServiceResult.fail('에러 발생')

        assert result.success is False
        assert result.data is None
        assert result.message == '에러 발생'

    def test_ok_without_data(self):
        """데이터 없이 성공 결과 생성"""
        result = ServiceResult.ok()

        assert result.success is True
        assert result.data is None

    def test_fail_with_message(self):
        """메시지와 함께 실패 결과 생성"""
        result = ServiceResult.fail('에러', error_code='TEST_ERROR')

        assert result.success is False
        assert result.message == '에러'
        assert result.error_code == 'TEST_ERROR'

