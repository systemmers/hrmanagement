"""
계정 관리 Blueprint

계정 설정, 비밀번호 변경, 개인정보 공개 설정, 계정 탈퇴 기능을 제공합니다.
- 개인 계정(personal)과 직원 계정(corporate employee) 모두 사용
"""
from flask import Blueprint

account_bp = Blueprint('account', __name__, url_prefix='/account')

from . import routes
