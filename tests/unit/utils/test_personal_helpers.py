"""
개인 프로필 헬퍼 테스트

프로필 조회 및 필수 확인 기능 테스트
"""
import pytest
from unittest.mock import Mock, patch
from flask import g, session

from app.utils.personal_helpers import (
    get_current_profile,
    require_profile,
    profile_required,
    profile_required_no_inject
)
from app.models.personal_profile import PersonalProfile


class TestGetCurrentProfile:
    """현재 프로필 조회 테스트"""

    def test_get_cached_profile(self, app):
        """캐시된 프로필 반환"""
        with app.app_context():
            with app.test_request_context():
                # 캐시에 프로필 설정
                mock_profile = Mock(spec=PersonalProfile)
                g._current_profile = mock_profile

                result = get_current_profile()

                assert result == mock_profile

    def test_get_profile_no_session(self, app):
        """세션 없을 때 None 반환"""
        with app.app_context():
            with app.test_request_context():
                result = get_current_profile()
                assert result is None

    def test_get_profile_from_db(self, app, session):
        """DB에서 프로필 조회"""
        from app.models.user import User

        with app.app_context():
            with app.test_request_context():
                # 테스트 사용자 및 프로필 생성
                user = User(username='test', email='test@test.com')
                user.set_password('test123')
                session.add(user)
                session.commit()

                profile = PersonalProfile(
                    user_id=user.id,
                    name='테스트',
                    email='test@test.com'
                )
                session.add(profile)
                session.commit()

                # 세션에 user_id 설정
                from app.constants.session_keys import SessionKeys
                flask_session = {}
                flask_session[SessionKeys.USER_ID] = user.id

                with patch('app.utils.personal_helpers.session', flask_session):
                    result = get_current_profile()

                    assert result is not None
                    assert result.name == '테스트'
                    assert g._current_profile == result


class TestRequireProfile:
    """프로필 필수 확인 테스트"""

    def test_require_profile_exists(self, app):
        """프로필이 있을 때 None 반환"""
        with app.app_context():
            with app.test_request_context():
                mock_profile = Mock(spec=PersonalProfile)

                with patch('app.utils.personal_helpers.get_current_profile', return_value=mock_profile):
                    result = require_profile()
                    assert result is None

    def test_require_profile_not_exists(self, app):
        """프로필이 없을 때 에러 응답 반환"""
        with app.app_context():
            with app.test_request_context():
                with patch('app.utils.personal_helpers.get_current_profile', return_value=None):
                    result = require_profile()

                    assert result is not None
                    assert len(result) == 2
                    response, status_code = result
                    assert status_code == 404
                    assert 'error' in response.json


class TestProfileRequiredDecorator:
    """프로필 필수 데코레이터 테스트"""

    def test_profile_required_with_profile(self, app):
        """프로필이 있을 때 함수 실행"""
        with app.app_context():
            with app.test_request_context():
                mock_profile = Mock(spec=PersonalProfile)
                mock_profile.name = '테스트'

                @profile_required
                def test_function(profile):
                    return {'name': profile.name}

                with patch('app.utils.personal_helpers.get_current_profile', return_value=mock_profile), \
                     patch('app.utils.personal_helpers.require_profile', return_value=None):
                    result = test_function()

                    assert result['name'] == '테스트'

    def test_profile_required_without_profile(self, app):
        """프로필이 없을 때 에러 반환"""
        with app.app_context():
            with app.test_request_context():
                @profile_required
                def test_function(profile):
                    return {'name': profile.name}

                error_response = ({'error': '프로필을 먼저 생성해주세요.'}, 404)

                with patch('app.utils.personal_helpers.require_profile', return_value=error_response):
                    result = test_function()

                    assert result == error_response


class TestProfileRequiredNoInjectDecorator:
    """프로필 필수 데코레이터 (주입 없음) 테스트"""

    def test_profile_required_no_inject_with_profile(self, app):
        """프로필이 있을 때 함수 실행 (주입 없음)"""
        with app.app_context():
            with app.test_request_context():
                @profile_required_no_inject
                def test_function():
                    return {'success': True}

                with patch('app.utils.personal_helpers.require_profile', return_value=None):
                    result = test_function()

                    assert result['success'] is True

    def test_profile_required_no_inject_without_profile(self, app):
        """프로필이 없을 때 에러 반환 (주입 없음)"""
        with app.app_context():
            with app.test_request_context():
                @profile_required_no_inject
                def test_function():
                    return {'success': True}

                error_response = ({'error': '프로필을 먼저 생성해주세요.'}, 404)

                with patch('app.utils.personal_helpers.require_profile', return_value=error_response):
                    result = test_function()

                    assert result == error_response

    def test_decorator_preserves_function_name(self, app):
        """데코레이터가 함수명을 보존하는지 확인"""
        with app.app_context():
            @profile_required
            def my_function(profile):
                return profile

            assert my_function.__name__ == 'my_function'

    def test_decorator_no_inject_preserves_function_name(self, app):
        """데코레이터(주입 없음)가 함수명을 보존하는지 확인"""
        with app.app_context():
            @profile_required_no_inject
            def my_function():
                return True

            assert my_function.__name__ == 'my_function'

