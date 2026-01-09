"""
BusinessCard Service

명함 업로드/삭제 비즈니스 로직을 제공합니다.
FileStorageService를 활용하여 파일 관리를 수행합니다.
"""
import os
from datetime import datetime
from typing import Dict, Optional, Tuple
from flask import current_app

from app.domains.businesscard.repositories.businesscard_repository import BusinessCardRepository
from app.domains.employee.services import employee_service
from app.shared.services.file_storage_service import file_storage
from app.shared.base.service_result import ServiceResult


class BusinessCardService:
    """명함 서비스 (Facade)"""

    # 상수
    MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB
    ALLOWED_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
    UPLOAD_SUBFOLDER = 'business_cards'

    def __init__(self, repository: BusinessCardRepository = None):
        self.repository = repository or BusinessCardRepository()

    def _get_upload_folder(self) -> str:
        """명함 업로드 폴더 경로 반환 및 생성"""
        upload_folder = os.path.join(
            current_app.root_path,
            'static',
            'uploads',
            self.UPLOAD_SUBFOLDER
        )
        os.makedirs(upload_folder, exist_ok=True)
        return upload_folder

    def _allowed_image_file(self, filename: str) -> bool:
        """허용된 이미지 파일 확장자 검사"""
        if '.' not in filename:
            return False
        ext = filename.rsplit('.', 1)[1].lower()
        return ext in self.ALLOWED_EXTENSIONS

    def _get_file_extension(self, filename: str) -> str:
        """파일 확장자 추출"""
        if '.' in filename:
            return filename.rsplit('.', 1)[1].lower()
        return ''

    def _generate_filename(self, employee_id: int, original_filename: str, side: str) -> str:
        """고유한 파일명 생성"""
        ext = self._get_file_extension(original_filename)
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        return f"bc_{employee_id}_{side}_{timestamp}.{ext}"

    def _delete_file_if_exists(self, file_path: str) -> bool:
        """파일이 존재하면 삭제"""
        if not file_path:
            return False

        # /static/uploads/... 형식의 웹 경로를 실제 경로로 변환
        if file_path.startswith('/static/'):
            full_path = os.path.join(
                current_app.root_path,
                file_path.lstrip('/')
            )
        else:
            full_path = file_path

        if os.path.exists(full_path):
            try:
                os.remove(full_path)
                return True
            except OSError:
                return False
        return False

    def get_business_cards(self, employee_id: int) -> ServiceResult:
        """
        직원의 명함 이미지 조회

        Returns:
            ServiceResult with data: {'front': {...}, 'back': {...}}
        """
        try:
            # 직원 존재 확인
            employee = employee_service.get_employee_by_id(employee_id)
            if not employee:
                return ServiceResult.failure('직원을 찾을 수 없습니다.')

            cards = self.repository.get_by_employee(employee_id)
            return ServiceResult.success(data=cards)

        except Exception as e:
            return ServiceResult.failure(f'명함 조회 중 오류: {str(e)}')

    def get_business_card(self, employee_id: int, side: str) -> ServiceResult:
        """
        직원의 특정 면 명함 이미지 조회

        Args:
            employee_id: 직원 ID
            side: 'front' 또는 'back'
        """
        try:
            if side not in ['front', 'back']:
                return ServiceResult.failure('side는 front 또는 back이어야 합니다.')

            card = self.repository.get_one_by_side(employee_id, side)
            if not card:
                return ServiceResult.failure(f'명함 {side} 이미지를 찾을 수 없습니다.', code='NOT_FOUND')

            return ServiceResult.success(data=card)

        except Exception as e:
            return ServiceResult.failure(f'명함 조회 중 오류: {str(e)}')

    def upload_business_card(
        self,
        employee_id: int,
        file,
        side: str
    ) -> ServiceResult:
        """
        명함 이미지 업로드

        Args:
            employee_id: 직원 ID
            file: 업로드된 파일 객체
            side: 'front' 또는 'back'

        Returns:
            ServiceResult with uploaded card data
        """
        try:
            # side 검증
            if side not in ['front', 'back']:
                return ServiceResult.failure('side는 front 또는 back이어야 합니다.')

            # 직원 존재 확인
            employee = employee_service.get_employee_by_id(employee_id)
            if not employee:
                return ServiceResult.failure('직원을 찾을 수 없습니다.')

            # 파일 검증
            if not file or file.filename == '':
                return ServiceResult.failure('파일이 선택되지 않았습니다.')

            if not self._allowed_image_file(file.filename):
                return ServiceResult.failure(
                    '이미지 파일만 업로드 가능합니다. (jpg, png, gif, webp)'
                )

            # 파일 크기 확인
            file.seek(0, os.SEEK_END)
            file_size = file.tell()
            file.seek(0)

            if file_size > self.MAX_IMAGE_SIZE:
                return ServiceResult.failure('파일 크기가 5MB를 초과합니다.')

            # 기존 명함 이미지 삭제
            old_card = self.repository.get_one_by_side(employee_id, side)
            if old_card:
                old_path = old_card.get('file_path') or old_card.get('filePath')
                self._delete_file_if_exists(old_path)
                self.repository.delete_by_side(employee_id, side, commit=False)

            # 파일 저장
            unique_filename = self._generate_filename(employee_id, file.filename, side)
            upload_folder = self._get_upload_folder()
            file_path = os.path.join(upload_folder, unique_filename)
            file.save(file_path)

            # 웹 접근 경로
            web_path = f"/static/uploads/{self.UPLOAD_SUBFOLDER}/{unique_filename}"

            # DB 저장
            attachment = self.repository.create_business_card({
                'employee_id': employee_id,
                'file_name': file.filename,
                'file_path': web_path,
                'file_type': self._get_file_extension(file.filename),
                'file_size': file_size,
                'side': side,
                'upload_date': datetime.now().strftime('%Y-%m-%d')
            })

            return ServiceResult.success(
                data={
                    'side': side,
                    'file_path': web_path,
                    'attachment': attachment.to_dict() if hasattr(attachment, 'to_dict') else attachment
                },
                message=f'명함 {side} 이미지가 업로드되었습니다.'
            )

        except Exception as e:
            return ServiceResult.failure(f'명함 업로드 중 오류: {str(e)}')

    def delete_business_card(self, employee_id: int, side: str) -> ServiceResult:
        """
        명함 이미지 삭제

        Args:
            employee_id: 직원 ID
            side: 'front' 또는 'back'
        """
        try:
            # side 검증
            if side not in ['front', 'back']:
                return ServiceResult.failure('side는 front 또는 back이어야 합니다.')

            # 기존 명함 이미지 확인 및 삭제
            old_card = self.repository.get_one_by_side(employee_id, side)
            if not old_card:
                return ServiceResult.failure(
                    f'명함 {side} 이미지를 찾을 수 없습니다.',
                    code='NOT_FOUND'
                )

            # 파일 삭제
            old_path = old_card.get('file_path') or old_card.get('filePath')
            self._delete_file_if_exists(old_path)

            # DB 삭제
            self.repository.delete_by_side(employee_id, side)

            return ServiceResult.success(
                message=f'명함 {side} 이미지가 삭제되었습니다.'
            )

        except Exception as e:
            return ServiceResult.failure(f'명함 삭제 중 오류: {str(e)}')


# 싱글톤 인스턴스
businesscard_service = BusinessCardService()
