"""
직원 파일 관리 라우트

첨부파일, 프로필 사진, 명함 이미지 업로드/다운로드 기능을 제공합니다.
Phase 8: 상수 모듈 적용
Phase 27.2: API 응답 표준화 (api_helpers 사용)
"""
import os
from datetime import datetime
from flask import Blueprint, request, current_app, session

from ...shared.constants.session_keys import SessionKeys, UserRole
from ...shared.utils.decorators import login_required, manager_or_admin_required
from ...shared.utils.object_helpers import safe_get
from ...shared.utils.api_helpers import (
    api_success, api_error, api_not_found, api_forbidden, api_server_error
)
from ...services.employee_service import employee_service
from .helpers import (
    allowed_file, allowed_image_file, get_file_extension,
    get_upload_folder, get_profile_photo_folder, get_business_card_folder,
    generate_unique_filename, delete_file_if_exists,
    MAX_FILE_SIZE, MAX_IMAGE_SIZE
)


# Blueprint는 __init__.py에서 정의하므로 여기서는 라우트 함수만 정의


def register_file_routes(bp: Blueprint):
    """파일 관련 라우트를 Blueprint에 등록"""

    # ========================================
    # 첨부파일 API
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/attachments', methods=['GET'])
    @login_required
    def get_attachments(employee_id):
        """직원 첨부파일 목록 조회 API"""
        try:
            attachments = employee_service.get_attachment_list(employee_id)
            return api_success({'attachments': attachments})
        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/attachments', methods=['POST'])
    @manager_or_admin_required
    def upload_attachment(employee_id):
        """첨부파일 업로드 API"""
        try:
            # 직원 존재 확인
            employee = employee_service.get_employee_by_id(employee_id)
            if not employee:
                return api_not_found('직원')

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

            # 파일 저장
            ext = get_file_extension(file.filename)
            unique_filename = generate_unique_filename(employee_id, file.filename)

            upload_folder = get_upload_folder()
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # 웹 접근 경로
            web_path = f"/static/uploads/attachments/{unique_filename}"

            # 카테고리 (폼에서 전달)
            category = request.form.get('category', '기타')

            # DB 저장
            attachment_data = {
                'employeeId': employee_id,
                'fileName': file.filename,
                'filePath': web_path,
                'fileType': ext,
                'fileSize': file_size,
                'category': category,
                'uploadDate': datetime.now().strftime('%Y-%m-%d')
            }
            created = employee_service.create_attachment(attachment_data)

            return api_success({
                'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
            })

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/attachments/<int:attachment_id>', methods=['DELETE'])
    @manager_or_admin_required
    def delete_attachment(attachment_id):
        """첨부파일 삭제 API"""
        try:
            # 첨부파일 조회
            attachment = employee_service.get_attachment_by_id(attachment_id)
            if not attachment:
                return api_not_found('첨부파일')

            # 파일 경로 추출
            file_path = safe_get(attachment, 'file_path')

            # 실제 파일 삭제
            delete_file_if_exists(file_path)

            # DB에서 삭제
            employee_service.delete_attachment(attachment_id)

            return api_success(message='첨부파일이 삭제되었습니다.')

        except Exception as e:
            return api_server_error(str(e))

    # ========================================
    # 프로필 사진 API
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['POST'])
    @login_required
    def upload_profile_photo(employee_id):
        """프로필 사진 업로드 API"""
        try:
            # 권한 체크: 본인 또는 관리자/매니저
            user_role = session.get(SessionKeys.USER_ROLE)
            is_admin_or_manager = user_role in [UserRole.ADMIN, UserRole.MANAGER]
            is_self = session.get(SessionKeys.EMPLOYEE_ID) == employee_id
            if not is_admin_or_manager and not is_self:
                return api_forbidden()

            # 직원 존재 확인
            employee = employee_service.get_employee_by_id(employee_id)
            if not employee:
                return api_not_found('직원')

            # 파일 검증
            if 'file' not in request.files:
                return api_error('파일이 없습니다.')

            file = request.files['file']
            if file.filename == '':
                return api_error('파일이 선택되지 않았습니다.')

            if not allowed_image_file(file.filename):
                return api_error('이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)')

            # 파일 크기 확인
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_IMAGE_SIZE:
                return api_error('파일 크기가 5MB를 초과합니다.')

            category = 'profile_photo'

            # 기존 프로필 사진 삭제
            old_photo = employee_service.get_attachment_by_category(employee_id, category)
            if old_photo:
                old_path = safe_get(old_photo, 'file_path')
                delete_file_if_exists(old_path)
                employee_service.delete_attachment_by_category(employee_id, category)

            # 파일 저장
            ext = get_file_extension(file.filename)
            unique_filename = generate_unique_filename(employee_id, file.filename, 'profile')

            upload_folder = get_profile_photo_folder()
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # 웹 접근 경로
            web_path = f"/static/uploads/profile_photos/{unique_filename}"

            # DB 저장
            attachment_data = {
                'employeeId': employee_id,
                'fileName': file.filename,
                'filePath': web_path,
                'fileType': ext,
                'fileSize': file_size,
                'category': category,
                'uploadDate': datetime.now().strftime('%Y-%m-%d')
            }
            created = employee_service.create_attachment(attachment_data)

            return api_success({
                'file_path': web_path,
                'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
            })

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['GET'])
    @login_required
    def get_profile_photo(employee_id):
        """프로필 사진 조회 API"""
        try:
            photo = employee_service.get_attachment_by_category(employee_id, 'profile_photo')
            return api_success({
                'file_path': safe_get(photo, 'file_path') if photo else None,
                'attachment': photo
            })

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/profile-photo', methods=['DELETE'])
    @login_required
    def delete_profile_photo(employee_id):
        """프로필 사진 삭제 API"""
        try:
            # 권한 체크: 본인 또는 관리자/매니저
            user_role = session.get(SessionKeys.USER_ROLE)
            is_admin_or_manager = user_role in [UserRole.ADMIN, UserRole.MANAGER]
            is_self = session.get(SessionKeys.EMPLOYEE_ID) == employee_id
            if not is_admin_or_manager and not is_self:
                return api_forbidden()

            category = 'profile_photo'

            # 기존 프로필 사진 삭제
            old_photo = employee_service.get_attachment_by_category(employee_id, category)
            if old_photo:
                old_path = safe_get(old_photo, 'file_path')
                delete_file_if_exists(old_path)
                employee_service.delete_attachment_by_category(employee_id, category)
                return api_success(message='프로필 사진이 삭제되었습니다.')
            else:
                return api_not_found('프로필 사진')

        except Exception as e:
            return api_server_error(str(e))

    # ========================================
    # 명함 이미지 API
    # ========================================

    @bp.route('/api/employees/<int:employee_id>/business-card', methods=['POST'])
    @login_required
    def upload_business_card(employee_id):
        """명함 이미지 업로드 API (앞면/뒷면)"""
        try:
            # 권한 체크: 본인 또는 관리자
            is_admin = session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN
            is_self = session.get(SessionKeys.EMPLOYEE_ID) == employee_id
            if not is_admin and not is_self:
                return api_forbidden()

            # 직원 존재 확인
            employee = employee_service.get_employee_by_id(employee_id)
            if not employee:
                return api_not_found('직원')

            # side 파라미터 검증
            side = request.form.get('side')
            if side not in ['front', 'back']:
                return api_error('side 파라미터는 front 또는 back이어야 합니다.')

            category = f'business_card_{side}'

            # 파일 검증
            if 'file' not in request.files:
                return api_error('파일이 없습니다.')

            file = request.files['file']
            if file.filename == '':
                return api_error('파일이 선택되지 않았습니다.')

            if not allowed_image_file(file.filename):
                return api_error('이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)')

            # 파일 크기 확인
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > MAX_IMAGE_SIZE:
                return api_error('파일 크기가 5MB를 초과합니다.')

            # 기존 명함 이미지 삭제
            old_card = employee_service.get_attachment_by_category(employee_id, category)
            if old_card:
                old_path = safe_get(old_card, 'file_path')
                delete_file_if_exists(old_path)
                employee_service.delete_attachment_by_category(employee_id, category)

            # 파일 저장
            ext = get_file_extension(file.filename)
            unique_filename = generate_unique_filename(employee_id, file.filename, side)

            upload_folder = get_business_card_folder()
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # 웹 접근 경로
            web_path = f"/static/uploads/business_cards/{unique_filename}"

            # DB 저장
            attachment_data = {
                'employeeId': employee_id,
                'fileName': file.filename,
                'filePath': web_path,
                'fileType': ext,
                'fileSize': file_size,
                'category': category,
                'uploadDate': datetime.now().strftime('%Y-%m-%d')
            }
            created = employee_service.create_attachment(attachment_data)

            return api_success({
                'side': side,
                'file_path': web_path,
                'attachment': created.to_dict() if hasattr(created, 'to_dict') else created
            })

        except Exception as e:
            return api_server_error(str(e))

    @bp.route('/api/employees/<int:employee_id>/business-card/<side>', methods=['DELETE'])
    @login_required
    def delete_business_card(employee_id, side):
        """명함 이미지 삭제 API"""
        try:
            # 권한 체크: 본인 또는 관리자
            is_admin = session.get(SessionKeys.USER_ROLE) == UserRole.ADMIN
            is_self = session.get(SessionKeys.EMPLOYEE_ID) == employee_id
            if not is_admin and not is_self:
                return api_forbidden()

            # side 파라미터 검증
            if side not in ['front', 'back']:
                return api_error('side 파라미터는 front 또는 back이어야 합니다.')

            category = f'business_card_{side}'

            # 기존 명함 이미지 삭제
            old_card = employee_service.get_attachment_by_category(employee_id, category)
            if old_card:
                old_path = safe_get(old_card, 'file_path')
                delete_file_if_exists(old_path)
                employee_service.delete_attachment_by_category(employee_id, category)
                return api_success(message=f'명함 {side} 이미지가 삭제되었습니다.')
            else:
                return api_not_found('명함 이미지')

        except Exception as e:
            return api_server_error(str(e))
