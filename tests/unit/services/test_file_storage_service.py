"""
FileStorageService 단위 테스트

파일 저장 서비스의 핵심 비즈니스 로직 테스트:
- 경로 생성
- 파일 업로드/삭제
- 파일 조회
"""
import pytest
from unittest.mock import Mock, patch, mock_open
import os

from app.services.file_storage_service import (
    FileStorageService,
    file_storage,
    ALLOWED_EXTENSIONS,
    MAX_FILE_SIZE
)


class TestFileStorageServiceInit:
    """FileStorageService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert file_storage is not None
        assert isinstance(file_storage, FileStorageService)


class TestFileStorageServicePathGeneration:
    """경로 생성 테스트"""

    def test_get_corporate_path(self, app):
        """법인 파일 경로 생성"""
        with patch('app.services.file_storage_service.os.path.join') as mock_join, \
             patch('app.services.file_storage_service.os.makedirs') as mock_makedirs, \
             patch('app.services.file_storage_service.current_app') as mock_app:
            mock_app.root_path = '/app'
            mock_join.return_value = '/app/static/uploads/corporate/1/employees/1/attachments'

            result = file_storage.get_corporate_path(
                company_id=1,
                employee_id=1,
                category='attachments'
            )

            assert result is not None
            mock_makedirs.assert_called_once()

    def test_get_personal_path(self, app):
        """개인 파일 경로 생성"""
        with patch('app.services.file_storage_service.os.path.join') as mock_join, \
             patch('app.services.file_storage_service.os.makedirs') as mock_makedirs, \
             patch('app.services.file_storage_service.current_app') as mock_app:
            mock_app.root_path = '/app'
            mock_join.return_value = '/app/static/uploads/personal/1/attachments'

            result = file_storage.get_personal_path(
                user_id=1,
                category='attachments'
            )

            assert result is not None


class TestFileStorageServiceValidation:
    """파일 검증 테스트"""

    def test_is_allowed_file_valid(self):
        """허용된 파일 확장자"""
        assert FileStorageService.allowed_file('test.pdf') is True
        assert FileStorageService.allowed_file('test.jpg') is True

    def test_is_allowed_file_invalid(self):
        """허용되지 않은 파일 확장자"""
        assert FileStorageService.allowed_file('test.exe') is False
        assert FileStorageService.allowed_file('test.bat') is False

    def test_is_allowed_image_valid(self):
        """허용된 이미지 확장자"""
        assert FileStorageService.allowed_image_file('test.jpg') is True
        assert FileStorageService.allowed_image_file('test.png') is True

    def test_is_allowed_image_invalid(self):
        """허용되지 않은 이미지 확장자"""
        assert FileStorageService.allowed_image_file('test.pdf') is False

