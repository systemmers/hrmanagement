"""
File Storage Service

파일 저장 체계를 관리하는 서비스입니다.
- 계정 유형별 경로 분리 (personal/corporate)
- 파일 업로드/삭제/조회
- 보안 접근 제어
"""
import os
import shutil
from datetime import datetime
from typing import Optional, Tuple
from werkzeug.utils import secure_filename
from flask import current_app

from app.constants.session_keys import AccountType


# ========================================
# 설정 상수
# ========================================

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB

# 파일 카테고리
CATEGORY_ATTACHMENT = 'attachments'
CATEGORY_PROFILE_PHOTO = 'profile_photo'
CATEGORY_BUSINESS_CARD_FRONT = 'business_card_front'
CATEGORY_BUSINESS_CARD_BACK = 'business_card_back'
CATEGORY_COMPANY_DOCUMENT = 'documents'
CATEGORY_ADMIN_PHOTO = 'admin_photos'

# 법인 서류 허용 확장자
ALLOWED_DOCUMENT_EXTENSIONS = {'pdf', 'doc', 'docx', 'xls', 'xlsx', 'hwp', 'jpg', 'jpeg', 'png'}


class FileStorageService:
    """파일 저장 서비스

    디렉토리 구조:
    uploads/
    ├── corporate/{company_id}/
    │   └── employees/{employee_id}/
    │       ├── attachments/
    │       ├── profile_photo/
    │       └── business_card/
    ├── personal/{user_id}/
    │   ├── attachments/
    │   └── profile_photo/
    └── temp/
    """

    def __init__(self):
        self.base_path = None  # Flask app context에서 초기화

    def _get_base_path(self) -> str:
        """기본 업로드 경로 반환"""
        if self.base_path:
            return self.base_path
        return os.path.join(current_app.root_path, 'static', 'uploads')

    # ========================================
    # 경로 생성
    # ========================================

    def get_corporate_path(self, company_id: int, employee_id: int,
                           category: str = CATEGORY_ATTACHMENT) -> str:
        """법인 직원 파일 경로 생성

        Args:
            company_id: 회사 ID
            employee_id: 직원 ID
            category: 파일 카테고리 (attachments, profile_photo, business_card)

        Returns:
            절대 경로
        """
        base = self._get_base_path()
        path = os.path.join(base, 'corporate', str(company_id),
                            'employees', str(employee_id), category)
        os.makedirs(path, exist_ok=True)
        return path

    def get_personal_path(self, user_id: int, category: str = CATEGORY_ATTACHMENT) -> str:
        """개인 계정 파일 경로 생성

        Args:
            user_id: 사용자 ID
            category: 파일 카테고리 (attachments, profile_photo)

        Returns:
            절대 경로
        """
        base = self._get_base_path()
        path = os.path.join(base, 'personal', str(user_id), category)
        os.makedirs(path, exist_ok=True)
        return path

    def get_temp_path(self) -> str:
        """임시 파일 경로 반환"""
        base = self._get_base_path()
        path = os.path.join(base, 'temp')
        os.makedirs(path, exist_ok=True)
        return path

    # ========================================
    # 웹 경로 생성
    # ========================================

    def get_corporate_web_path(self, company_id: int, employee_id: int,
                                filename: str, category: str = CATEGORY_ATTACHMENT) -> str:
        """법인 직원 웹 접근 경로"""
        return f"/static/uploads/corporate/{company_id}/employees/{employee_id}/{category}/{filename}"

    def get_personal_web_path(self, user_id: int, filename: str,
                              category: str = CATEGORY_ATTACHMENT) -> str:
        """개인 계정 웹 접근 경로"""
        return f"/static/uploads/personal/{user_id}/{category}/{filename}"

    # ========================================
    # 파일 검증
    # ========================================

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """허용된 파일 확장자 검사"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

    @staticmethod
    def allowed_image_file(filename: str) -> bool:
        """허용된 이미지 파일 확장자 검사"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS

    @staticmethod
    def get_file_extension(filename: str) -> str:
        """파일 확장자 추출"""
        return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''

    @staticmethod
    def get_file_size(file) -> int:
        """파일 크기 반환 (바이트)"""
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        return size

    def validate_file(self, file, is_image: bool = False) -> Tuple[bool, Optional[str]]:
        """파일 유효성 검사

        Args:
            file: 업로드된 파일 객체
            is_image: 이미지 파일 여부

        Returns:
            (성공여부, 에러메시지)
        """
        if not file or file.filename == '':
            return False, '파일이 선택되지 않았습니다.'

        if is_image:
            if not self.allowed_image_file(file.filename):
                return False, '이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)'
            max_size = MAX_IMAGE_SIZE
            size_msg = '5MB'
        else:
            if not self.allowed_file(file.filename):
                return False, '허용되지 않는 파일 형식입니다.'
            max_size = MAX_FILE_SIZE
            size_msg = '10MB'

        file_size = self.get_file_size(file)
        if file_size > max_size:
            return False, f'파일 크기가 {size_msg}를 초과합니다.'

        return True, None

    # ========================================
    # 파일명 생성
    # ========================================

    def generate_filename(self, original_filename: str, prefix: str = '',
                          entity_id: Optional[int] = None) -> str:
        """고유한 파일명 생성

        Args:
            original_filename: 원본 파일명
            prefix: 접두사 (예: 'profile', 'front', 'back')
            entity_id: 엔티티 ID (직원 ID 또는 사용자 ID)

        Returns:
            고유한 파일명
        """
        filename = secure_filename(original_filename)
        ext = self.get_file_extension(filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')

        parts = []
        if entity_id:
            parts.append(str(entity_id))
        if prefix:
            parts.append(prefix)
        parts.append(timestamp)

        return f"{'_'.join(parts)}.{ext}"

    # ========================================
    # 파일 저장/삭제
    # ========================================

    def save_file(self, file, folder_path: str, filename: str) -> str:
        """파일 저장

        Args:
            file: 업로드된 파일 객체
            folder_path: 저장할 폴더 경로
            filename: 저장할 파일명

        Returns:
            저장된 파일의 전체 경로
        """
        os.makedirs(folder_path, exist_ok=True)
        file_path = os.path.join(folder_path, filename)
        file.save(file_path)
        return file_path

    def delete_file(self, file_path: str) -> bool:
        """파일 삭제

        Args:
            file_path: 삭제할 파일 경로 (웹 경로 또는 절대 경로)

        Returns:
            삭제 성공 여부
        """
        if not file_path:
            return False

        # 웹 경로인 경우 절대 경로로 변환
        if file_path.startswith('/static/'):
            full_path = os.path.join(current_app.root_path, file_path.lstrip('/'))
        else:
            full_path = file_path

        if os.path.exists(full_path):
            os.remove(full_path)
            return True
        return False

    def delete_folder(self, folder_path: str) -> bool:
        """폴더 및 내용 삭제

        Args:
            folder_path: 삭제할 폴더 경로

        Returns:
            삭제 성공 여부
        """
        if os.path.exists(folder_path):
            shutil.rmtree(folder_path)
            return True
        return False

    # ========================================
    # 법인 직원 파일 관리
    # ========================================

    def save_corporate_file(self, file, company_id: int, employee_id: int,
                            category: str = CATEGORY_ATTACHMENT,
                            prefix: str = '') -> Tuple[str, str, int]:
        """법인 직원 파일 저장

        Args:
            file: 업로드된 파일 객체
            company_id: 회사 ID
            employee_id: 직원 ID
            category: 파일 카테고리
            prefix: 파일명 접두사

        Returns:
            (절대경로, 웹경로, 파일크기)
        """
        folder_path = self.get_corporate_path(company_id, employee_id, category)
        filename = self.generate_filename(file.filename, prefix, employee_id)
        file_size = self.get_file_size(file)

        full_path = self.save_file(file, folder_path, filename)
        web_path = self.get_corporate_web_path(company_id, employee_id, filename, category)

        return full_path, web_path, file_size

    def delete_corporate_file(self, company_id: int, employee_id: int,
                               filename: str, category: str = CATEGORY_ATTACHMENT) -> bool:
        """법인 직원 파일 삭제"""
        folder_path = self.get_corporate_path(company_id, employee_id, category)
        file_path = os.path.join(folder_path, filename)
        return self.delete_file(file_path)

    # ========================================
    # 개인 계정 파일 관리
    # ========================================

    def save_personal_file(self, file, user_id: int,
                           category: str = CATEGORY_ATTACHMENT,
                           prefix: str = '') -> Tuple[str, str, int]:
        """개인 계정 파일 저장

        Args:
            file: 업로드된 파일 객체
            user_id: 사용자 ID
            category: 파일 카테고리
            prefix: 파일명 접두사

        Returns:
            (절대경로, 웹경로, 파일크기)
        """
        folder_path = self.get_personal_path(user_id, category)
        filename = self.generate_filename(file.filename, prefix, user_id)
        file_size = self.get_file_size(file)

        full_path = self.save_file(file, folder_path, filename)
        web_path = self.get_personal_web_path(user_id, filename, category)

        return full_path, web_path, file_size

    def delete_personal_file(self, user_id: int, filename: str,
                             category: str = CATEGORY_ATTACHMENT) -> bool:
        """개인 계정 파일 삭제"""
        folder_path = self.get_personal_path(user_id, category)
        file_path = os.path.join(folder_path, filename)
        return self.delete_file(file_path)

    # ========================================
    # 법인 관리자 사진 관리
    # ========================================

    def get_admin_photos_path(self) -> str:
        """법인 관리자 프로필 사진 경로 생성

        Returns:
            절대 경로
        """
        base = self._get_base_path()
        path = os.path.join(base, CATEGORY_ADMIN_PHOTO)
        os.makedirs(path, exist_ok=True)
        return path

    def get_admin_photos_web_path(self, filename: str) -> str:
        """법인 관리자 프로필 사진 웹 접근 경로"""
        return f"/static/uploads/{CATEGORY_ADMIN_PHOTO}/{filename}"

    # ========================================
    # 범용 사진 업로드 처리 (DRY)
    # ========================================

    def handle_photo_upload(self, file, entity_id: int, category: str,
                            fallback_value: Optional[str] = None) -> Tuple[Optional[str], Optional[str]]:
        """범용 사진 업로드 처리

        request.files에서 받은 파일을 검증하고 저장합니다.
        DRY 원칙에 따라 여러 라우트에서 공통으로 사용합니다.

        Args:
            file: 업로드된 파일 객체 (request.files.get('photoFile'))
            entity_id: 엔티티 ID (직원 ID, 관리자 프로필 ID 등)
            category: 저장 카테고리 ('profile_photo', 'admin_photos' 등)
            fallback_value: 파일이 없을 때 반환할 기본값

        Returns:
            (웹 경로 또는 fallback_value, 에러 메시지 또는 None)

        Examples:
            # 법인 관리자 프로필 사진
            web_path, error = file_storage.handle_photo_upload(
                request.files.get('photoFile'),
                admin_profile_id,
                CATEGORY_ADMIN_PHOTO,
                request.form.get('photo', '')
            )

            # 직원 프로필 사진
            web_path, error = file_storage.handle_photo_upload(
                request.files.get('photoFile'),
                employee_id,
                CATEGORY_PROFILE_PHOTO
            )
        """
        # 파일이 없으면 fallback 값 반환
        if not file or file.filename == '':
            return fallback_value, None

        # 이미지 파일 검증
        is_valid, error_msg = self.validate_file(file, is_image=True)
        if not is_valid:
            return None, error_msg

        # 카테고리별 경로 결정
        if category == CATEGORY_ADMIN_PHOTO:
            folder_path = self.get_admin_photos_path()
            filename = self.generate_filename(file.filename, 'admin', entity_id)
            web_path = self.get_admin_photos_web_path(filename)
        elif category == CATEGORY_PROFILE_PHOTO:
            # 프로필 사진은 별도 폴더 구조 사용 (기존 호환성)
            base = self._get_base_path()
            folder_path = os.path.join(base, 'profile_photos')
            os.makedirs(folder_path, exist_ok=True)
            filename = self.generate_filename(file.filename, 'profile', entity_id)
            web_path = f"/static/uploads/profile_photos/{filename}"
        else:
            # 기타 카테고리
            base = self._get_base_path()
            folder_path = os.path.join(base, category)
            os.makedirs(folder_path, exist_ok=True)
            filename = self.generate_filename(file.filename, category, entity_id)
            web_path = f"/static/uploads/{category}/{filename}"

        # 파일 저장
        self.save_file(file, folder_path, filename)

        return web_path, None

    # ========================================
    # 법인 서류 파일 관리
    # ========================================

    def get_company_documents_path(self, company_id: int) -> str:
        """법인 서류 경로 생성

        Args:
            company_id: 회사 ID

        Returns:
            절대 경로
        """
        base = self._get_base_path()
        path = os.path.join(base, 'corporate', str(company_id), CATEGORY_COMPANY_DOCUMENT)
        os.makedirs(path, exist_ok=True)
        return path

    def get_company_documents_web_path(self, company_id: int, filename: str) -> str:
        """법인 서류 웹 접근 경로"""
        return f"/static/uploads/corporate/{company_id}/{CATEGORY_COMPANY_DOCUMENT}/{filename}"

    @staticmethod
    def allowed_document_file(filename: str) -> bool:
        """허용된 서류 파일 확장자 검사"""
        return '.' in filename and \
               filename.rsplit('.', 1)[1].lower() in ALLOWED_DOCUMENT_EXTENSIONS

    def validate_document_file(self, file) -> Tuple[bool, Optional[str]]:
        """법인 서류 파일 유효성 검사

        Args:
            file: 업로드된 파일 객체

        Returns:
            (성공여부, 에러메시지)
        """
        if not file or file.filename == '':
            return False, '파일이 선택되지 않았습니다.'

        if not self.allowed_document_file(file.filename):
            return False, '허용되지 않는 파일 형식입니다. (pdf, doc, docx, xls, xlsx, hwp, jpg, png)'

        file_size = self.get_file_size(file)
        if file_size > MAX_FILE_SIZE:
            return False, '파일 크기가 10MB를 초과합니다.'

        return True, None

    def save_company_document(self, file, company_id: int,
                              prefix: str = 'doc') -> Tuple[str, str, int, str]:
        """법인 서류 파일 저장

        Args:
            file: 업로드된 파일 객체
            company_id: 회사 ID
            prefix: 파일명 접두사

        Returns:
            (절대경로, 웹경로, 파일크기, 저장된 파일명)
        """
        folder_path = self.get_company_documents_path(company_id)
        filename = self.generate_filename(file.filename, prefix)
        file_size = self.get_file_size(file)

        full_path = self.save_file(file, folder_path, filename)
        web_path = self.get_company_documents_web_path(company_id, filename)

        return full_path, web_path, file_size, filename

    def delete_company_document(self, company_id: int, filename: str) -> bool:
        """법인 서류 파일 삭제"""
        folder_path = self.get_company_documents_path(company_id)
        file_path = os.path.join(folder_path, filename)
        return self.delete_file(file_path)

    def get_company_document_full_path(self, company_id: int, filename: str) -> str:
        """법인 서류 전체 경로 반환"""
        folder_path = self.get_company_documents_path(company_id)
        return os.path.join(folder_path, filename)

    # ========================================
    # 접근 권한 검사
    # ========================================

    def has_corporate_access(self, company_id: int, user_company_id: int) -> bool:
        """법인 파일 접근 권한 검사

        Args:
            company_id: 파일이 속한 회사 ID
            user_company_id: 사용자의 회사 ID

        Returns:
            접근 가능 여부
        """
        return company_id == user_company_id

    def has_personal_access(self, file_user_id: int, current_user_id: int) -> bool:
        """개인 파일 접근 권한 검사

        Args:
            file_user_id: 파일 소유자 ID
            current_user_id: 현재 사용자 ID

        Returns:
            접근 가능 여부
        """
        return file_user_id == current_user_id

    # ========================================
    # 마이그레이션 지원
    # ========================================

    def migrate_legacy_file(self, legacy_path: str, account_type: str,
                            company_id: Optional[int] = None,
                            employee_id: Optional[int] = None,
                            user_id: Optional[int] = None,
                            category: str = CATEGORY_ATTACHMENT) -> Optional[str]:
        """레거시 파일을 새 구조로 마이그레이션

        Args:
            legacy_path: 기존 파일 경로 (웹 경로)
            account_type: 'corporate' 또는 'personal'
            company_id: 회사 ID (corporate인 경우)
            employee_id: 직원 ID (corporate인 경우)
            user_id: 사용자 ID (personal인 경우)
            category: 파일 카테고리

        Returns:
            새 웹 경로 또는 None (실패시)
        """
        # 절대 경로로 변환
        if legacy_path.startswith('/static/'):
            full_path = os.path.join(current_app.root_path, legacy_path.lstrip('/'))
        else:
            full_path = legacy_path

        if not os.path.exists(full_path):
            return None

        # 파일명 추출
        filename = os.path.basename(full_path)

        # 새 경로 생성
        if account_type == AccountType.CORPORATE and company_id and employee_id:
            new_folder = self.get_corporate_path(company_id, employee_id, category)
            new_web_path = self.get_corporate_web_path(company_id, employee_id, filename, category)
        elif account_type == AccountType.PERSONAL and user_id:
            new_folder = self.get_personal_path(user_id, category)
            new_web_path = self.get_personal_web_path(user_id, filename, category)
        else:
            return None

        # 파일 이동
        new_full_path = os.path.join(new_folder, filename)
        shutil.move(full_path, new_full_path)

        return new_web_path


# 싱글톤 인스턴스
file_storage = FileStorageService()
