"""
개인 프로필 헬퍼 모듈

개인 프로필 관련 중복 로직을 통합합니다.
Phase 6: 백엔드 리팩토링
"""
from functools import wraps
from typing import Optional, Tuple
from flask import session, jsonify, g

from app.models.personal_profile import PersonalProfile


def get_current_profile() -> Optional[PersonalProfile]:
    """
    현재 로그인한 사용자의 프로필 조회

    요청 스코프에서 캐싱하여 중복 DB 조회를 방지합니다.

    Returns:
        PersonalProfile 또는 None
    """
    if hasattr(g, '_current_profile'):
        return g._current_profile

    user_id = session.get('user_id')
    if not user_id:
        return None

    profile = PersonalProfile.query.filter_by(user_id=user_id).first()
    g._current_profile = profile
    return profile


def require_profile() -> Optional[Tuple]:
    """
    프로필 필수 확인 (API용)

    Returns:
        None: 프로필 있음
        Tuple: (json_response, status_code) 프로필 없을시 JSON 응답
    """
    profile = get_current_profile()
    if not profile:
        return (jsonify({'error': '프로필을 먼저 생성해주세요.'}), 404)
    return None


def profile_required(f):
    """
    프로필 필수 데코레이터 (API용)

    프로필이 없는 경우 JSON 에러 응답을 반환합니다.
    프로필이 있는 경우 함수의 첫 번째 인자로 profile을 전달합니다.

    사용 예:
        @profile_required
        def education_list(profile):
            educations = [edu.to_dict() for edu in profile.educations.all()]
            return jsonify({'educations': educations})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        profile_check = require_profile()
        if profile_check:
            return profile_check
        profile = get_current_profile()
        return f(profile, *args, **kwargs)
    return decorated_function


def profile_required_no_inject(f):
    """
    프로필 필수 데코레이터 (API용, 프로필 주입 없음)

    프로필이 없는 경우 JSON 에러 응답을 반환합니다.
    프로필 주입 없이 단순히 존재 여부만 확인합니다.

    사용 예:
        @profile_required_no_inject
        def education_list():
            profile = get_current_profile()
            educations = [edu.to_dict() for edu in profile.educations.all()]
            return jsonify({'educations': educations})
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        profile_check = require_profile()
        if profile_check:
            return profile_check
        return f(*args, **kwargs)
    return decorated_function
