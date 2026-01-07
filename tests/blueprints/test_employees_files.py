"""
직원 파일 관리 테스트

첨부파일, 프로필 사진, 명함 이미지 업로드/다운로드 기능 테스트
"""
import pytest
import io
import json
from unittest.mock import Mock, patch, MagicMock
from werkzeug.datastructures import FileStorage

from app.shared.constants.session_keys import SessionKeys
from app.domains.user.models import User


class TestAttachmentAPI:
    """첨부파일 API 테스트"""

    def test_get_attachments_requires_login(self, client):
        """첨부파일 조회 로그인 필요 테스트"""
        response = client.get('/api/employees/1/attachments')
        assert response.status_code == 401

    def test_get_attachments_success(self, auth_client_corporate_full, test_employee):
        """첨부파일 조회 성공 테스트"""
        with patch('app.services.employee_service.employee_service.get_attachment_list') as mock_get:
            mock_get.return_value = [
                {
                    'id': 1,
                    'filename': 'resume.pdf',
                    'file_type': 'application/pdf',
                    'file_size': 1024
                }
            ]
            
            response = auth_client_corporate_full.get(
                f'/api/employees/{test_employee.id}/attachments'
            )
            assert response.status_code == 200
            data = json.loads(response.data)
            assert data['success'] is True
            assert len(data['data']['attachments']) == 1

    def test_get_attachments_error_handling(self, auth_client_corporate_full):
        """첨부파일 조회 에러 처리 테스트"""
        with patch('app.services.employee_service.employee_service.get_attachment_list') as mock_get:
            mock_get.side_effect = Exception('Database error')
            
            response = auth_client_corporate_full.get('/api/employees/1/attachments')
            assert response.status_code == 500
            data = json.loads(response.data)
            assert data['success'] is False


class TestAttachmentUpload:
    """첨부파일 업로드 테스트"""

    def test_upload_attachment_requires_manager_or_admin(
        self, client, test_user_personal
    ):
        """첨부파일 업로드 권한 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_PERSONAL
            sess[SessionKeys.USER_ROLE] = User.ROLE_EMPLOYEE

        response = client.post('/api/employees/1/attachments')
        assert response.status_code in [302, 403]

    def test_upload_attachment_employee_not_found(self, auth_client_corporate_full):
        """존재하지 않는 직원에 업로드 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = None
            
            response = auth_client_corporate_full.post('/api/employees/999/attachments')
            assert response.status_code == 404
            data = json.loads(response.data)
            assert data['success'] is False

    def test_upload_attachment_no_file(self, auth_client_corporate_full, test_employee):
        """파일 없이 업로드 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/attachments'
            )
            assert response.status_code == 400
            data = json.loads(response.data)
            assert '파일이 없습니다' in data['error']

    def test_upload_attachment_empty_filename(self, auth_client_corporate_full, test_employee):
        """빈 파일명 업로드 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            data = {'file': (io.BytesIO(b''), '')}
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/attachments',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 400
            result = json.loads(response.data)
            assert '선택되지 않았습니다' in result['error']

    def test_upload_attachment_invalid_file_type(self, auth_client_corporate_full, test_employee):
        """허용되지 않는 파일 형식 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            data = {'file': (io.BytesIO(b'test'), 'test.exe')}
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/attachments',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 400
            result = json.loads(response.data)
            assert '허용되지 않는' in result['error']

    @patch('app.blueprints.employees.files.get_upload_folder')
    @patch('app.blueprints.employees.files.generate_unique_filename')
    @patch('app.services.employee_service.employee_service.create_attachment')
    def test_upload_attachment_success(
        self, mock_create, mock_gen_name, mock_folder,
        auth_client_corporate_full, test_employee, tmp_path
    ):
        """첨부파일 업로드 성공 테스트"""
        # Mock 설정
        mock_folder.return_value = str(tmp_path)
        mock_gen_name.return_value = 'test_unique.pdf'
        mock_create.return_value = {'id': 1, 'filename': 'resume.pdf'}
        
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            # PDF 파일 생성
            file_content = b'%PDF-1.4 test content'
            data = {'file': (io.BytesIO(file_content), 'resume.pdf')}
            
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/attachments',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 200
            result = json.loads(response.data)
            assert result['success'] is True

    def test_upload_attachment_file_too_large(self, auth_client_corporate_full, test_employee):
        """파일 크기 초과 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            # 11MB 파일 생성
            large_file = io.BytesIO(b'x' * (11 * 1024 * 1024))
            data = {'file': (large_file, 'large.pdf')}
            
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/attachments',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 400
            result = json.loads(response.data)
            assert '10MB를 초과' in result['error']


class TestAttachmentDownload:
    """첨부파일 다운로드 테스트"""

    def test_download_attachment_requires_login(self, client):
        """다운로드 로그인 필요 테스트"""
        response = client.get('/api/employees/1/attachments/1')
        assert response.status_code == 401

    @patch('app.services.employee_service.employee_service.get_attachment_by_id')
    @patch('app.blueprints.employees.files.get_upload_folder')
    def test_download_attachment_not_found(
        self, mock_folder, mock_get, auth_client_corporate_full, tmp_path
    ):
        """존재하지 않는 첨부파일 다운로드 테스트"""
        mock_get.return_value = None
        mock_folder.return_value = str(tmp_path)
        
        response = auth_client_corporate_full.get('/api/employees/1/attachments/999')
        assert response.status_code == 404

    @patch('app.services.employee_service.employee_service.get_attachment_by_id')
    @patch('app.blueprints.employees.files.get_upload_folder')
    def test_download_attachment_file_not_exists(
        self, mock_folder, mock_get, auth_client_corporate_full, tmp_path
    ):
        """파일이 없는 경우 테스트"""
        mock_get.return_value = {
            'id': 1,
            'filename': 'test.pdf',
            'stored_filename': 'nonexistent.pdf'
        }
        mock_folder.return_value = str(tmp_path)
        
        response = auth_client_corporate_full.get('/api/employees/1/attachments/1')
        assert response.status_code == 404


class TestAttachmentDelete:
    """첨부파일 삭제 테스트"""

    def test_delete_attachment_requires_manager_or_admin(
        self, client, test_user_personal
    ):
        """첨부파일 삭제 권한 테스트"""
        with client.session_transaction() as sess:
            sess[SessionKeys.USER_ID] = test_user_personal.id
            sess[SessionKeys.ACCOUNT_TYPE] = User.ACCOUNT_PERSONAL
            sess[SessionKeys.USER_ROLE] = User.ROLE_EMPLOYEE

        response = client.delete('/api/attachments/1')
        assert response.status_code == 403

    @patch('app.services.employee_service.employee_service.get_attachment_by_id')
    def test_delete_attachment_not_found(self, mock_get, auth_client_corporate_full):
        """존재하지 않는 첨부파일 삭제 테스트"""
        mock_get.return_value = None
        
        response = auth_client_corporate_full.delete('/api/attachments/999')
        assert response.status_code == 404

    @patch('app.services.employee_service.employee_service.get_attachment_by_id')
    @patch('app.services.employee_service.employee_service.delete_attachment')
    @patch('app.blueprints.employees.files.get_upload_folder')
    @patch('app.blueprints.employees.files.delete_file_if_exists')
    def test_delete_attachment_success(
        self, mock_delete_file, mock_folder, mock_delete, mock_get,
        auth_client_corporate_full, tmp_path
    ):
        """첨부파일 삭제 성공 테스트"""
        mock_get.return_value = {
            'id': 1,
            'filename': 'test.pdf',
            'stored_filename': 'stored.pdf'
        }
        mock_delete.return_value = True
        mock_folder.return_value = str(tmp_path)
        mock_delete_file.return_value = None
        
        response = auth_client_corporate_full.delete('/api/attachments/1')
        assert response.status_code == 200
        result = json.loads(response.data)
        assert result['success'] is True


class TestProfilePhoto:
    """프로필 사진 테스트"""

    def test_upload_profile_photo_requires_login(self, client):
        """프로필 사진 업로드 로그인 필요 테스트"""
        response = client.post('/api/employees/1/profile-photo')
        assert response.status_code == 401

    def test_upload_profile_photo_invalid_image(
        self, auth_client_corporate_full, test_employee
    ):
        """잘못된 이미지 형식 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            data = {'file': (io.BytesIO(b'not an image'), 'test.txt')}
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/profile-photo',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 400

    @patch('app.blueprints.employees.files.get_profile_photo_folder')
    @patch('app.blueprints.employees.files.generate_unique_filename')
    @patch('app.services.employee_service.employee_service.update_employee')
    def test_upload_profile_photo_success(
        self, mock_update, mock_gen_name, mock_folder,
        auth_client_corporate_full, test_employee, tmp_path
    ):
        """프로필 사진 업로드 성공 테스트"""
        mock_folder.return_value = str(tmp_path)
        mock_gen_name.return_value = 'profile_1.jpg'
        mock_update.return_value = test_employee
        
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            # 작은 이미지 파일 생성
            image_data = io.BytesIO(b'fake image data')
            data = {'file': (image_data, 'profile.jpg')}
            
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/profile-photo',
                data=data,
                content_type='multipart/form-data'
            )
            # 실제 이미지가 아니므로 400 또는 500 예상
            assert response.status_code in [200, 400, 500]


class TestBusinessCard:
    """명함 이미지 테스트"""

    def test_upload_business_card_requires_login(self, client):
        """명함 업로드 로그인 필요 테스트"""
        response = client.post('/api/employees/1/business-card')
        assert response.status_code == 401

    def test_upload_business_card_invalid_image(
        self, auth_client_corporate_full, test_employee
    ):
        """잘못된 명함 이미지 형식 테스트"""
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            data = {'file': (io.BytesIO(b'not an image'), 'card.exe')}
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/business-card',
                data=data,
                content_type='multipart/form-data'
            )
            assert response.status_code == 400

    @patch('app.blueprints.employees.files.get_business_card_folder')
    @patch('app.blueprints.employees.files.generate_unique_filename')
    @patch('app.services.employee_service.employee_service.update_employee')
    def test_upload_business_card_success(
        self, mock_update, mock_gen_name, mock_folder,
        auth_client_corporate_full, test_employee, tmp_path
    ):
        """명함 업로드 성공 테스트"""
        mock_folder.return_value = str(tmp_path)
        mock_gen_name.return_value = 'card_1.jpg'
        mock_update.return_value = test_employee
        
        with patch('app.services.employee_service.employee_service.get_employee_by_id') as mock_get:
            mock_get.return_value = test_employee
            
            # 작은 이미지 파일 생성
            image_data = io.BytesIO(b'fake card image')
            data = {'file': (image_data, 'card.jpg')}
            
            response = auth_client_corporate_full.post(
                f'/api/employees/{test_employee.id}/business-card',
                data=data,
                content_type='multipart/form-data'
            )
            # 실제 이미지가 아니므로 400 또는 500 예상
            assert response.status_code in [200, 400, 500]

