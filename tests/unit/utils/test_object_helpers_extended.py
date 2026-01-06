"""
Object Access Helpers 확장 테스트

Dict/Model 객체 접근 통합 유틸리티 테스트
"""
import pytest
from app.utils.object_helpers import safe_get, safe_get_nested


class TestSafeGetExtended:
    """safe_get 확장 기능 테스트"""

    def test_safe_get_none(self):
        """None 객체 처리"""
        result = safe_get(None, 'key', 'default')
        assert result == 'default'

    def test_safe_get_dict_none_value(self):
        """dict에서 None 값 가져오기"""
        data = {'name': None}
        result = safe_get(data, 'name', 'default')
        assert result is None

    def test_safe_get_object_with_none_attr(self):
        """None 값을 가진 객체 속성"""
        class TestObj:
            name = None

        obj = TestObj()
        result = safe_get(obj, 'name', 'default')
        assert result is None


class TestSafeGetNestedExtended:
    """safe_get_nested 확장 기능 테스트"""

    def test_safe_get_nested_partial_none(self):
        """중간에 None이 있는 경로"""
        data = {'user': None}
        result = safe_get_nested(data, 'user', 'profile', 'name', default='default')
        assert result == 'default'

    def test_safe_get_nested_single_key(self):
        """단일 키로 중첩 조회"""
        data = {'name': 'test'}
        result = safe_get_nested(data, 'name')
        assert result == 'test'

    def test_safe_get_nested_empty_keys(self):
        """키가 없는 경우"""
        data = {'name': 'test'}
        result = safe_get_nested(data)
        assert result == data

    def test_safe_get_nested_deep_path(self):
        """깊은 경로 탐색"""
        data = {
            'a': {
                'b': {
                    'c': {
                        'd': {
                            'value': 'deep'
                        }
                    }
                }
            }
        }
        result = safe_get_nested(data, 'a', 'b', 'c', 'd', 'value')
        assert result == 'deep'

