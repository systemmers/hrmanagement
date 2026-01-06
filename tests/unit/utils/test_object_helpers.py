"""
Object Helpers 테스트

객체 접근 헬퍼 함수 테스트
"""
import pytest

from app.shared.utils.object_helpers import safe_get, safe_get_nested


class TestSafeGet:
    """safe_get 테스트"""

    def test_safe_get_from_dict(self):
        """딕셔너리에서 값 추출"""
        data = {'name': '홍길동', 'age': 30}
        assert safe_get(data, 'name') == '홍길동'
        assert safe_get(data, 'age') == 30

    def test_safe_get_from_object(self):
        """객체에서 값 추출"""
        class TestObj:
            def __init__(self):
                self.name = '홍길동'
                self.age = 30

        obj = TestObj()
        assert safe_get(obj, 'name') == '홍길동'
        assert safe_get(obj, 'age') == 30

    def test_safe_get_not_found(self):
        """값을 찾을 수 없을 때 기본값 반환"""
        data = {'name': '홍길동'}
        assert safe_get(data, 'age', default=0) == 0
        assert safe_get(data, 'email') is None

    def test_safe_get_none_object(self):
        """None 객체 처리"""
        assert safe_get(None, 'name', default='기본값') == '기본값'
        assert safe_get(None, 'name') is None


class TestSafeGetNested:
    """safe_get_nested 테스트"""

    def test_safe_get_nested_from_dict(self):
        """중첩된 딕셔너리에서 값 추출"""
        data = {
            'user': {
                'profile': {
                    'name': '홍길동'
                }
            }
        }
        assert safe_get_nested(data, 'user', 'profile', 'name') == '홍길동'

    def test_safe_get_nested_from_object(self):
        """중첩된 객체에서 값 추출"""
        class Profile:
            def __init__(self):
                self.name = '홍길동'

        class User:
            def __init__(self):
                self.profile = Profile()

        user = User()
        assert safe_get_nested(user, 'profile', 'name') == '홍길동'

    def test_safe_get_nested_not_found(self):
        """경로를 찾을 수 없을 때 기본값 반환"""
        data = {'user': {'profile': {}}}
        assert safe_get_nested(data, 'user', 'profile', 'name', default='기본값') == '기본값'
        assert safe_get_nested(data, 'user', 'profile', 'name') is None

    def test_safe_get_nested_none_in_path(self):
        """경로 중간에 None이 있을 때"""
        data = {'user': None}
        assert safe_get_nested(data, 'user', 'profile', 'name', default='기본값') == '기본값'

