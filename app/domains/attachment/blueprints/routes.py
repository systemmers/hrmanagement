"""
Attachment 도메인 API 라우트

범용 첨부파일 관리 API를 제공합니다.
- GET /api/attachments/<owner_type>/<owner_id> - 소유자별 첨부파일 목록
- POST /api/attachments - 첨부파일 업로드
- DELETE /api/attachments/<id> - 첨부파일 삭제
- PATCH /api/attachments/<owner_type>/<owner_id>/order - 순서 변경
"""
import os
from datetime import datetime
from flask import request, current_app

from app.shared.utils.decorators import api_login_required
from app.shared.utils.transaction import atomic_transaction
from app.shared.utils.api_helpers import (
    api_success, api_error, api_not_found, api_server_error
)
from app.domains.attachment.models import Attachment
from app.domains.attachment.services import attachment_service
from app.domains.attachment.constants import OwnerType, AttachmentCategory
from . import attachment_bp


# 허용 파일 확장자
ALLOWED_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'ppt', 'pptx',
                      'txt', 'hwp', 'jpg', 'jpeg', 'png', 'gif', 'webp', 'zip'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB


def allowed_file(filename):
    """허용된 파일 확장자인지 확인"""
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def get_file_extension(filename):
    """파일 확장자 추출"""
    if '.' in filename:
        return filename.rsplit('.', 1)[1].lower()
    return ''


def get_upload_folder():
    """업로드 폴더 경로 반환 (없으면 생성)"""
    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(owner_type, owner_id, original_filename):
    """고유한 파일명 생성"""
    ext = get_file_extension(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return f"{owner_type}_{owner_id}_{timestamp}.{ext}"


def delete_file_if_exists(file_path):
    """파일이 존재하면 삭제"""
    if file_path and file_path.startswith('/static/'):
        full_path = os.path.join(current_app.static_folder, file_path[8:])
        if os.path.exists(full_path):
            os.remove(full_path)


# ========================================
# 첨부파일 목록 조회 API
# ========================================

@attachment_bp.route('/api/attachments/<owner_type>/<int:owner_id>', methods=['GET'])
@api_login_required
def get_attachments(owner_type, owner_id):
    """
    소유자별 첨부파일 목록 조회 API

    Args:
        owner_type: 소유자 타입 (employee, profile, company)
        owner_id: 소유자 ID

    Returns:
        첨부파일 목록
    """
    try:
        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE, OwnerType.COMPANY]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        attachments = attachment_service.get_by_owner(owner_type, owner_id)
        return api_success({'attachments': attachments})

    except Exception as e:
        current_app.logger.error(f'첨부파일 목록 조회 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 첨부파일 업로드 API
# ========================================

@attachment_bp.route('/api/attachments', methods=['POST'])
@api_login_required
def upload_attachment():
    """
    첨부파일 업로드 API

    Form Data:
        - file: 업로드할 파일
        - owner_type: 소유자 타입 (employee, profile, company)
        - owner_id: 소유자 ID
        - category: 카테고리 (선택, 기본값: document)

    Returns:
        생성된 첨부파일 정보
    """
    try:
        # 파일 검증
        if 'file' not in request.files:
            return api_error('파일이 없습니다.')

        file = request.files['file']
        if file.filename == '':
            return api_error('파일이 선택되지 않았습니다.')

        if not allowed_file(file.filename):
            return api_error('허용되지 않는 파일 형식입니다.')

        # 파일 크기 확인
        file.seek(0, os.SEEK_END)
        file_size = file.tell()
        file.seek(0)

        if file_size > MAX_FILE_SIZE:
            return api_error('파일 크기가 10MB를 초과합니다.')

        # 폼 데이터 추출
        owner_type = request.form.get('owner_type')
        owner_id = request.form.get('owner_id')
        category = request.form.get('category', AttachmentCategory.DOCUMENT)

        # 필수 필드 검증
        if not owner_type:
            return api_error('owner_type은 필수입니다.')
        if not owner_id:
            return api_error('owner_id는 필수입니다.')

        try:
            owner_id = int(owner_id)
        except ValueError:
            return api_error('owner_id는 숫자여야 합니다.')

        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE, OwnerType.COMPANY]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        # 파일 저장
        ext = get_file_extension(file.filename)
        unique_filename = generate_unique_filename(owner_type, owner_id, file.filename)

        upload_folder = get_upload_folder()
        file_path = os.path.join(upload_folder, unique_filename)
        file.save(file_path)

        # 웹 접근 경로
        web_path = f"/static/uploads/attachments/{unique_filename}"

        # 현재 최대 display_order 조회
        existing = attachment_service.get_by_owner(owner_type, owner_id)
        max_order = max([a.get('display_order', 0) for a in existing], default=-1)

        # DB 저장
        created = attachment_service.create({
            'owner_type': owner_type,
            'owner_id': owner_id,
            'file_name': file.filename,
            'file_path': web_path,
            'file_type': ext,
            'file_size': file_size,
            'category': category,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'display_order': max_order + 1
        })

        return api_success({
            'attachment': created
        })

    except Exception as e:
        current_app.logger.error(f'첨부파일 업로드 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 첨부파일 삭제 API
# ========================================

@attachment_bp.route('/api/attachments/<int:attachment_id>', methods=['DELETE'])
@api_login_required
def delete_attachment(attachment_id):
    """
    첨부파일 삭제 API

    Args:
        attachment_id: 첨부파일 ID

    Returns:
        삭제 성공 메시지
    """
    try:
        # 첨부파일 조회
        attachment = attachment_service.get_by_id(attachment_id)
        if not attachment:
            return api_not_found('첨부파일')

        # 파일 경로 추출
        file_path = attachment.get('file_path')

        # 실제 파일 삭제
        delete_file_if_exists(file_path)

        # DB에서 삭제
        attachment_service.delete(attachment_id)

        return api_success(message='첨부파일이 삭제되었습니다.')

    except Exception as e:
        current_app.logger.error(f'첨부파일 삭제 실패: {e}')
        return api_server_error(str(e))


# ========================================
# 첨부파일 순서 변경 API
# ========================================

@attachment_bp.route('/api/attachments/<owner_type>/<int:owner_id>/order', methods=['PATCH'])
@api_login_required
def update_attachment_order(owner_type, owner_id):
    """
    첨부파일 순서 변경 API

    Args:
        owner_type: 소유자 타입 (employee, profile, company)
        owner_id: 소유자 ID

    Body:
        {
            "order": [3, 1, 2]  // 첨부파일 ID 순서
        }

    Returns:
        성공 메시지
    """
    try:
        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE, OwnerType.COMPANY]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        order = data.get('order', [])
        if not isinstance(order, list):
            return api_error('order는 배열이어야 합니다.')

        with atomic_transaction():
            attachment_service.update_order(owner_type, owner_id, order, commit=False)

        return api_success(message='순서가 변경되었습니다.')

    except Exception as e:
        current_app.logger.error(f'첨부파일 순서 변경 실패: {e}')
        return api_server_error(str(e))
