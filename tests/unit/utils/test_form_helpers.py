"""
Form Helpers 테스트

폼 데이터 처리 헬퍼 함수 테스트

Phase 29: normalize_form_field 테스트 제거 (함수 삭제됨)
"""
import pytest

from app.utils.form_helpers import (
    parse_boolean,
    get_form_value,
    parse_int,
)


class TestParseBoolean:
    """parse_boolean 테스트"""

    def test_parse_boolean_true_values(self):
        """True로 변환되는 값들"""
        assert parse_boolean('true') is True
        assert parse_boolean('True') is True
        assert parse_boolean('1') is True
        assert parse_boolean(True) is True
        assert parse_boolean(1) is True

    def test_parse_boolean_false_values(self):
        """False로 변환되는 값들"""
        assert parse_boolean('false') is False
        assert parse_boolean('False') is False
        assert parse_boolean('0') is False
        assert parse_boolean(False) is False
        assert parse_boolean(0) is False
        assert parse_boolean(None) is False
        assert parse_boolean('') is False


# Phase 29: TestNormalizeFormField 클래스 제거됨
# normalize_form_field 함수가 삭제되어 테스트도 제거


class TestGetFormValue:
    """get_form_value 테스트"""

    def test_get_form_value_strips_whitespace(self):
        """공백 제거"""
        form_data = {'name': '  홍길동  '}
        result = get_form_value(form_data, 'name')
        assert result == '홍길동'

    def test_get_form_value_empty_string(self):
        """빈 문자열 처리"""
        form_data = {'name': '   '}
        result = get_form_value(form_data, 'name', default='기본값')
        assert result == '기본값'

    def test_get_form_value_default(self):
        """기본값 반환"""
        form_data = {}
        result = get_form_value(form_data, 'name', default='기본값')
        assert result == '기본값'


class TestParseInt:
    """parse_int 테스트"""

    def test_parse_int_valid(self):
        """유효한 정수 변환"""
        assert parse_int('123') == 123
        assert parse_int('0') == 0
        assert parse_int('-10') == -10

    def test_parse_int_invalid(self):
        """잘못된 값 변환"""
        assert parse_int('abc') is None
        assert parse_int('12.5') is None
        assert parse_int('') is None

    def test_parse_int_with_default(self):
        """기본값 사용"""
        assert parse_int('abc', default=0) == 0
        assert parse_int(None, default=100) == 100


# Phase 29: TestParseFloat, TestParseDate 클래스 제거됨
# 해당 함수들이 form_helpers.py에 존재하지 않아 테스트도 제거
