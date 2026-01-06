"""
개인 프로필 헬퍼 모듈

개인 프로필 관련 중복 로직을 통합합니다.
Phase 6: 백엔드 리팩토링
Phase 8: 상수 모듈 적용
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from functools import wraps
from typing import Optional, Tuple, TYPE_CHECKING
from flask import session, jsonify, g

from ..constants.session_keys import SessionKeys

if TYPE_CHECKING:
    from app.models import PersonalProfile

# 지연 초기화용
_personal_profile_repo = None


def _get_personal_profile_repo():
    """지연 초기화된 PersonalProfile Repository"""
    global _personal_profile_repo
    if _personal_profile_repo is None:
        from app.repositories.personal_profile_repository import personal_profile_repository
        _personal_profile_repo = personal_profile_repository
    return _personal_profile_repo


def get_current_profile() -> Optional["PersonalProfile"]:
    """
    현재 로그인한 사용자의 프로필 조회

    요청 스코프에서 캐싱하여 중복 DB 조회를 방지합니다.

    Returns:
        PersonalProfile 또는 None
    """
    if hasattr(g, '_current_profile'):
        return g._current_profile

    user_id = session.get(SessionKeys.USER_ID)
    if not user_id:
        return None

    # Phase 31: Repository 패턴 적용
    profile = _get_personal_profile_repo().find_by_user_id(user_id)
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
