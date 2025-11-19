"""
직원 관리 Blueprint
직원 CRUD 기능
"""
from flask import Blueprint

employee_bp = Blueprint('employee', __name__)

from app.employee import routes
