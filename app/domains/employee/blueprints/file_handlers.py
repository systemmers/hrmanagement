"""
파일 처리 헬퍼 함수

FileStorageService를 래핑하여 기존 API 호환성을 유지합니다.
"""
import os
from flask import current_app

from app.shared.services.file_storage_service import (
    file_storage,
    ALLOWED_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE
)

# 상수 re-export
__all__ = [
    'ALLOWED_EXTENSIONS',
    'ALLOWED_IMAGE_EXTENSIONS',
    'MAX_FILE_SIZE',
    'MAX_IMAGE_SIZE',
    'allowed_file',
    'allowed_image_file',
    'get_file_extension',
    'get_upload_folder',
    'get_profile_photo_folder',
    'get_business_card_folder',
    'generate_unique_filename',
    'delete_file_if_exists',
]


def allowed_file(filename):
    """허용된 파일 확장자 검사 (FileStorageService 위임)"""
    return file_storage.allowed_file(filename)


def allowed_image_file(filename):
    """허용된 이미지 파일 확장자 검사 (FileStorageService 위임)"""
    return file_storage.allowed_image_file(filename)


def get_file_extension(filename):
    """파일 확장자 추출 (FileStorageService 위임)"""
    return file_storage.get_file_extension(filename)


def get_upload_folder():
    """업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_profile_photo_folder():
    """프로필 사진 업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_photos')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_business_card_folder():
    """명함 이미지 업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'business_cards')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(employee_id, original_filename, prefix=''):
    """고유한 파일명 생성 (FileStorageService 위임)"""
    return file_storage.generate_filename(original_filename, prefix, employee_id)


def delete_file_if_exists(file_path):
    """파일이 존재하면 삭제 (FileStorageService 위임)"""
    return file_storage.delete_file(file_path)
