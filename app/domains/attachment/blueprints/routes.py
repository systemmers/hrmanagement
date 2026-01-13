"""
Attachment 도메인 API 라우트

범용 첨부파일 관리 API를 제공합니다.
- GET /api/attachments/<owner_type>/<owner_id> - 소유자별 첨부파일 목록
- POST /api/attachments - 첨부파일 업로드
- DELETE /api/attachments/<id> - 첨부파일 삭제
- PATCH /api/attachments/<owner_type>/<owner_id>/order - 순서 변경

Phase 1.2: FileStorageService 통합 (구조화된 경로 체계)
- employee: uploads/corporate/{company_id}/employees/{employee_id}/attachments/
- profile: uploads/personal/{user_id}/attachments/
- company: uploads/corporate/{company_id}/documents/
"""
import os
from datetime import datetime
from flask import request, current_app

from app.shared.utils.decorators import api_login_required
from app.shared.utils.transaction import atomic_transaction
from app.shared.utils.api_helpers import (
    api_success, api_error, api_not_found, api_server_error
)
from app.shared.services.file_storage_service import file_storage
from app.domains.attachment.models import Attachment
from app.domains.attachment.services import attachment_service
from app.domains.attachment.constants import OwnerType, AttachmentCategory, LinkedEntityType
from app.domains.employee.models import Employee
from app.domains.user.models.personal import PersonalProfile
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


def get_legacy_upload_folder():
    """레거시 업로드 폴더 경로 반환 (기존 파일 호환용)"""
    upload_folder = os.path.join(current_app.static_folder, 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(original_filename):
    """고유한 파일명 생성"""
    ext = get_file_extension(original_filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S_%f')
    return f"attachment_{timestamp}.{ext}"


def delete_file_if_exists(file_path):
    """파일이 존재하면 삭제 (FileStorageService 및 레거시 경로 지원)"""
    if not file_path:
        return

    # FileStorageService 경로 또는 레거시 경로 모두 처리
    if file_path.startswith('/static/'):
        full_path = os.path.join(current_app.static_folder, file_path[8:])
        if os.path.exists(full_path):
            os.remove(full_path)
            current_app.logger.debug(f'파일 삭제: {full_path}')


def get_owner_context(owner_type, owner_id):
    """
    소유자 타입에 따른 파일 저장 컨텍스트 조회

    Returns:
        dict: {'company_id': int, 'employee_id': int, 'user_id': int} 또는 None
    """
    if owner_type == OwnerType.EMPLOYEE:
        employee = Employee.query.get(owner_id)
        if employee:
            return {
                'company_id': employee.company_id,
                'employee_id': employee.id
            }
    elif owner_type == OwnerType.PROFILE:
        profile = PersonalProfile.query.get(owner_id)
        if profile:
            return {
                'user_id': profile.user_id
            }
    elif owner_type == OwnerType.COMPANY:
        return {
            'company_id': owner_id
        }
    return None


def save_attachment_file(file, owner_type, owner_id, category):
    """
    FileStorageService를 사용하여 첨부파일 저장

    Args:
        file: Flask FileStorage 객체
        owner_type: 소유자 타입 (employee, profile, company)
        owner_id: 소유자 ID
        category: 첨부파일 카테고리

    Returns:
        str: 저장된 파일의 웹 경로 또는 None
    """
    context = get_owner_context(owner_type, owner_id)
    if not context:
        return None

    # 카테고리에 따른 서브폴더 결정
    subfolder = f'attachments/{category}' if category else 'attachments'

    try:
        if owner_type == OwnerType.EMPLOYEE:
            # save_corporate_file 반환: (full_path, web_path, file_size)
            _, web_path, _ = file_storage.save_corporate_file(
                file,
                context['company_id'],
                context['employee_id'],
                subfolder
            )
        elif owner_type == OwnerType.PROFILE:
            # save_personal_file 반환: (full_path, web_path, file_size)
            _, web_path, _ = file_storage.save_personal_file(
                file,
                context['user_id'],
                subfolder
            )
        elif owner_type == OwnerType.COMPANY:
            # 회사 문서는 save_company_document 사용
            # 반환: (full_path, web_path, file_size, filename)
            _, web_path, _, _ = file_storage.save_company_document(
                file,
                context['company_id'],
                category if category else 'doc'
            )
        else:
            return None

        return web_path
    except Exception as e:
        current_app.logger.error(f'파일 저장 실패: {e}')
        return None


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
        - linked_entity_type: 연결 엔티티 타입 (선택, education/career/certificate)
        - linked_entity_id: 연결 엔티티 ID (선택)

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
        linked_entity_type = request.form.get('linked_entity_type')
        linked_entity_id = request.form.get('linked_entity_id')

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

        # FileStorageService를 사용한 파일 저장 (Phase 1.2)
        ext = get_file_extension(file.filename)
        web_path = save_attachment_file(file, owner_type, owner_id, category)
        if not web_path:
            return api_error('파일 저장에 실패했습니다. 소유자 정보를 확인해주세요.')

        # 현재 최대 display_order 조회
        existing = attachment_service.get_by_owner(owner_type, owner_id)
        max_order = max([a.get('display_order', 0) for a in existing], default=-1)

        # DB 저장
        attachment_data = {
            'owner_type': owner_type,
            'owner_id': owner_id,
            'file_name': file.filename,
            'file_path': web_path,
            'file_type': ext,
            'file_size': file_size,
            'category': category,
            'upload_date': datetime.now().strftime('%Y-%m-%d'),
            'display_order': max_order + 1
        }

        # 연결 엔티티 정보 추가 (Phase 5.2: 항목별 증빙 서류 연동)
        if linked_entity_type:
            attachment_data['linked_entity_type'] = linked_entity_type
        if linked_entity_id:
            try:
                attachment_data['linked_entity_id'] = int(linked_entity_id)
            except ValueError:
                return api_error('linked_entity_id는 숫자여야 합니다.')

        created = attachment_service.create(attachment_data)

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


# ========================================
# 항목별 증빙 서류 연동 API (Phase 4.2)
# ========================================

@attachment_bp.route('/api/attachments/<owner_type>/<int:owner_id>/linked/<linked_entity_type>/<int:linked_entity_id>', methods=['GET'])
@api_login_required
def get_linked_attachments(owner_type, owner_id, linked_entity_type, linked_entity_id):
    """
    연결된 엔티티별 첨부파일 조회 API

    Args:
        owner_type: 소유자 타입 (employee, profile)
        owner_id: 소유자 ID
        linked_entity_type: 연결 엔티티 타입 (education, career, certificate 등)
        linked_entity_id: 연결 엔티티 ID

    Returns:
        해당 엔티티에 연결된 첨부파일 목록
    """
    try:
        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        # linked_entity_type 검증
        if linked_entity_type not in LinkedEntityType.ALL_TYPES:
            return api_error(f'유효하지 않은 연결 엔티티 타입입니다. 허용값: {", ".join(LinkedEntityType.ALL_TYPES)}')

        attachments = attachment_service.get_by_linked_entity(
            owner_type, owner_id, linked_entity_type, linked_entity_id
        )
        return api_success({'attachments': attachments})

    except Exception as e:
        current_app.logger.error(f'연결 첨부파일 조회 실패: {e}')
        return api_server_error(str(e))


@attachment_bp.route('/api/attachments/<owner_type>/<int:owner_id>/linked/<linked_entity_type>', methods=['GET'])
@api_login_required
def get_all_linked_attachments_by_type(owner_type, owner_id, linked_entity_type):
    """
    연결 엔티티 타입별 모든 첨부파일 조회 API

    Args:
        owner_type: 소유자 타입 (employee, profile)
        owner_id: 소유자 ID
        linked_entity_type: 연결 엔티티 타입 (education, career, certificate 등)

    Returns:
        해당 타입의 모든 첨부파일 목록
    """
    try:
        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        # linked_entity_type 검증
        if linked_entity_type not in LinkedEntityType.ALL_TYPES:
            return api_error(f'유효하지 않은 연결 엔티티 타입입니다. 허용값: {", ".join(LinkedEntityType.ALL_TYPES)}')

        attachments = attachment_service.get_all_by_linked_entity_type(
            owner_type, owner_id, linked_entity_type
        )
        return api_success({'attachments': attachments})

    except Exception as e:
        current_app.logger.error(f'연결 엔티티 타입별 첨부파일 조회 실패: {e}')
        return api_server_error(str(e))


@attachment_bp.route('/api/attachments/<int:attachment_id>/link', methods=['PATCH'])
@api_login_required
def link_attachment(attachment_id):
    """
    기존 첨부파일을 엔티티에 연결 API

    Args:
        attachment_id: 첨부파일 ID

    Body:
        {
            "linked_entity_type": "education",
            "linked_entity_id": 1
        }

    Returns:
        수정된 첨부파일 정보
    """
    try:
        data = request.get_json()
        if not data:
            return api_error('요청 본문이 없습니다.')

        linked_entity_type = data.get('linked_entity_type')
        linked_entity_id = data.get('linked_entity_id')

        if not linked_entity_type:
            return api_error('linked_entity_type은 필수입니다.')
        if not linked_entity_id:
            return api_error('linked_entity_id는 필수입니다.')

        # linked_entity_type 검증
        if linked_entity_type not in LinkedEntityType.ALL_TYPES:
            return api_error(f'유효하지 않은 연결 엔티티 타입입니다. 허용값: {", ".join(LinkedEntityType.ALL_TYPES)}')

        attachment = attachment_service.link_attachment_to_entity(
            attachment_id, linked_entity_type, linked_entity_id
        )
        if not attachment:
            return api_not_found('첨부파일')

        return api_success({
            'attachment': attachment
        }, message='첨부파일이 연결되었습니다.')

    except Exception as e:
        current_app.logger.error(f'첨부파일 연결 실패: {e}')
        return api_server_error(str(e))


@attachment_bp.route('/api/attachments/<int:attachment_id>/unlink', methods=['PATCH'])
@api_login_required
def unlink_attachment(attachment_id):
    """
    첨부파일의 엔티티 연결 해제 API

    Args:
        attachment_id: 첨부파일 ID

    Returns:
        수정된 첨부파일 정보
    """
    try:
        attachment = attachment_service.unlink_attachment_from_entity(attachment_id)
        if not attachment:
            return api_not_found('첨부파일')

        return api_success({
            'attachment': attachment
        }, message='첨부파일 연결이 해제되었습니다.')

    except Exception as e:
        current_app.logger.error(f'첨부파일 연결 해제 실패: {e}')
        return api_server_error(str(e))


@attachment_bp.route('/api/attachments/<owner_type>/<int:owner_id>/evidence-status/<linked_entity_type>', methods=['GET'])
@api_login_required
def get_evidence_status(owner_type, owner_id, linked_entity_type):
    """
    특정 엔티티 타입의 증빙 서류 현황 조회 API

    Args:
        owner_type: 소유자 타입 (employee, profile)
        owner_id: 소유자 ID
        linked_entity_type: 연결 엔티티 타입

    Returns:
        {
            "entity_ids_with_evidence": [1, 3, 5],
            "total_evidence_count": 8
        }
    """
    try:
        # owner_type 검증
        valid_types = [OwnerType.EMPLOYEE, OwnerType.PROFILE]
        if owner_type not in valid_types:
            return api_error(f'유효하지 않은 소유자 타입입니다. 허용값: {", ".join(valid_types)}')

        # linked_entity_type 검증
        if linked_entity_type not in LinkedEntityType.ALL_TYPES:
            return api_error(f'유효하지 않은 연결 엔티티 타입입니다. 허용값: {", ".join(LinkedEntityType.ALL_TYPES)}')

        result = attachment_service.get_evidence_status(
            owner_type, owner_id, linked_entity_type
        )
        return api_success(result)

    except Exception as e:
        current_app.logger.error(f'증빙 서류 현황 조회 실패: {e}')
        return api_server_error(str(e))
