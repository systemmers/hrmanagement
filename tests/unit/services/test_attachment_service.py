"""
AttachmentService 단위 테스트

첨부파일 서비스의 핵심 비즈니스 로직 테스트:
- 첨부파일 조회
- 카테고리별 조회
- 파일 타입별 조회
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.employee.services.attachment_service import AttachmentService, attachment_service


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    mock_attachment_repo = Mock()

    with patch('app.domains.employee.get_attachment_repo', return_value=mock_attachment_repo):
        yield attachment_service, mock_attachment_repo


class TestAttachmentServiceInit:
    """AttachmentService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert attachment_service is not None
        assert isinstance(attachment_service, AttachmentService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(attachment_service, 'attachment_repo')


class TestAttachmentServiceQueries:
    """첨부파일 조회 테스트"""

    def test_get_by_employee_id_success(self, mock_repos):
        """직원 ID로 첨부파일 목록 조회 성공"""
        service, mock_repo = mock_repos

        mock_attachment1 = Mock()
        mock_attachment1.to_dict.return_value = {'id': 1, 'filename': 'test1.pdf'}
        mock_attachment2 = Mock()
        mock_attachment2.to_dict.return_value = {'id': 2, 'filename': 'test2.pdf'}
        mock_repo.find_by_employee_id.return_value = [mock_attachment1, mock_attachment2]

        result = service.get_by_employee_id(employee_id=1)

        assert len(result) == 2
        assert result[0]['filename'] == 'test1.pdf'

    def test_get_by_category_success(self, mock_repos):
        """카테고리별 첨부파일 조회 성공"""
        service, mock_repo = mock_repos

        expected = [{'id': 1, 'category': 'resume'}]
        mock_repo.get_by_category.return_value = expected

        result = service.get_by_category(employee_id=1, category='resume')

        assert result == expected
        mock_repo.get_by_category.assert_called_once_with(1, 'resume')

    def test_get_one_by_category_success(self, mock_repos):
        """카테고리별 첨부파일 1개 조회 성공"""
        service, mock_repo = mock_repos

        expected = {'id': 1, 'category': 'resume'}
        mock_repo.get_one_by_category.return_value = expected

        result = service.get_one_by_category(employee_id=1, category='resume')

        assert result == expected

    def test_get_one_by_category_not_found(self, mock_repos):
        """카테고리별 첨부파일 없을 때"""
        service, mock_repo = mock_repos

        mock_repo.get_one_by_category.return_value = None

        result = service.get_one_by_category(employee_id=1, category='resume')

        assert result is None

    def test_get_by_file_type_success(self, mock_repos):
        """파일 타입별 첨부파일 조회 성공"""
        service, mock_repo = mock_repos

        expected = [{'id': 1, 'file_type': 'pdf'}]
        mock_repo.get_by_file_type.return_value = expected

        result = service.get_by_file_type(employee_id=1, file_type='pdf')

        assert result == expected


class TestAttachmentServiceDelete:
    """첨부파일 삭제 테스트"""

    def test_delete_by_category_success(self, mock_repos):
        """카테고리별 첨부파일 삭제 성공"""
        service, mock_repo = mock_repos

        mock_repo.delete_by_category.return_value = True

        result = service.delete_by_category(employee_id=1, category='resume')

        assert result is True
        mock_repo.delete_by_category.assert_called_once_with(1, 'resume')

    def test_delete_by_category_failure(self, mock_repos):
        """카테고리별 첨부파일 삭제 실패"""
        service, mock_repo = mock_repos

        mock_repo.delete_by_category.return_value = False

        result = service.delete_by_category(employee_id=1, category='resume')

        assert result is False
