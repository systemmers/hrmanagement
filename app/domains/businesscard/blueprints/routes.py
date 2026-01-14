"""
BusinessCard Blueprint Routes

명함 API 엔드포인트를 정의합니다.

API Endpoints:
- GET    /api/businesscard/employee/<id>        - 명함 조회 (앞/뒤)
- GET    /api/businesscard/employee/<id>/<side> - 특정 면 명함 조회
- POST   /api/businesscard/employee/<id>        - 명함 업로드
- DELETE /api/businesscard/employee/<id>/<side> - 명함 삭제
"""
from flask import request, session

from app.domains.businesscard.blueprints import businesscard_bp
from app.domains.businesscard.services import businesscard_service
from app.shared.utils.decorators import login_required
from app.shared.constants.session_keys import SessionKeys, UserRole
from app.shared.utils.api_helpers import (
    api_success,
    api_error,
    api_not_found,
    api_forbidden,
    api_server_error
)


def _check_permission(employee_id: int) -> bool:
    """
    권한 체크: 본인 또는 관리자만 접근 가능

    Returns:
        True if authorized, False otherwise
    """
    is_admin = session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN
    is_self = session.get(SessionKeys.EMPLOYEE_ID) == employee_id
    return is_admin or is_self


@businesscard_bp.route('/employee/<int:employee_id>', methods=['GET'])
@login_required
def get_business_cards(employee_id):
    """
    직원의 명함 이미지 조회 (앞면/뒷면 모두)

    Returns:
        {
            "success": true,
            "data": {
                "front": {...} or null,
                "back": {...} or null
            }
        }
    """
    try:
        if not _check_permission(employee_id):
            return api_forbidden()

        result = businesscard_service.get_business_cards(employee_id)

        if result.success:
            return api_success(result.data)
        else:
            return api_error(result.message)

    except Exception as e:
        return api_server_error(str(e))


@businesscard_bp.route('/employee/<int:employee_id>/<side>', methods=['GET'])
@login_required
def get_business_card(employee_id, side):
    """
    직원의 특정 면 명함 이미지 조회

    Args:
        employee_id: 직원 ID
        side: 'front' 또는 'back'
    """
    try:
        if not _check_permission(employee_id):
            return api_forbidden()

        if side not in ['front', 'back']:
            return api_error('side는 front 또는 back이어야 합니다.')

        result = businesscard_service.get_business_card(employee_id, side)

        if result.success:
            return api_success(result.data)
        elif result.error_code == 'NOT_FOUND':
            return api_not_found('명함 이미지')
        else:
            return api_error(result.message)

    except Exception as e:
        return api_server_error(str(e))


@businesscard_bp.route('/employee/<int:employee_id>', methods=['POST'])
@login_required
def upload_business_card(employee_id):
    """
    명함 이미지 업로드

    Form Data:
        - file: 업로드할 이미지 파일
        - side: 'front' 또는 'back'

    Returns:
        {
            "success": true,
            "data": {
                "side": "front",
                "file_path": "/static/uploads/business_cards/...",
                "attachment": {...}
            }
        }
    """
    try:
        if not _check_permission(employee_id):
            return api_forbidden()

        # side 파라미터 검증
        side = request.form.get('side')
        if side not in ['front', 'back']:
            return api_error('side 파라미터는 front 또는 back이어야 합니다.')

        # 파일 검증
        if 'file' not in request.files:
            return api_error('파일이 없습니다.')

        file = request.files['file']

        result = businesscard_service.upload_business_card(employee_id, file, side)

        if result.success:
            return api_success(result.data, message=result.message)
        else:
            return api_error(result.message)

    except Exception as e:
        return api_server_error(str(e))


@businesscard_bp.route('/employee/<int:employee_id>/<side>', methods=['DELETE'])
@login_required
def delete_business_card(employee_id, side):
    """
    명함 이미지 삭제

    Args:
        employee_id: 직원 ID
        side: 'front' 또는 'back'
    """
    try:
        if not _check_permission(employee_id):
            return api_forbidden()

        if side not in ['front', 'back']:
            return api_error('side는 front 또는 back이어야 합니다.')

        result = businesscard_service.delete_business_card(employee_id, side)

        if result.success:
            return api_success(message=result.message)
        elif result.error_code == 'NOT_FOUND':
            return api_not_found('명함 이미지')
        else:
            return api_error(result.message)

    except Exception as e:
        return api_server_error(str(e))
