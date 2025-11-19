"""
인증 Blueprint
로그인/로그아웃 기능
"""
from flask import Blueprint

auth_bp = Blueprint('auth', __name__)

from app.auth import routes
