"""
법인 설정 API 공통 헬퍼

모든 법인 설정 API 모듈에서 사용하는 공통 함수와 import를 정의합니다.
"""
from flask import session

from app.shared.constants.session_keys import SessionKeys


def get_company_id():
    """세션에서 company_id 조회"""
    return session.get(SessionKeys.COMPANY_ID)
