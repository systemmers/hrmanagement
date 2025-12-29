"""
EmployeeService 단위 테스트

직원 서비스의 핵심 비즈니스 로직 테스트:
- 직원 CRUD
- 접근 권한 검증
- 관계형 데이터 조회
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, List

from app.services.employee_service import EmployeeService, employee_service


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture (extensions 모듈 패치)"""
    from app import extensions

    # Mock 객체 생성
    mock_employee_repo = Mock()
    mock_education_repo = Mock()
    mock_career_repo = Mock()
    mock_certificate_repo = Mock()
    mock_family_repo = Mock()
    mock_military_repo = Mock()
    mock_attachment_repo = Mock()

    # extensions 모듈의 repo 변수들을 Mock으로 대체
    with patch.object(extensions, 'employee_repo', mock_employee_repo), \
         patch.object(extensions, 'education_repo', mock_education_repo), \
         patch.object(extensions, 'career_repo', mock_career_repo), \
         patch.object(extensions, 'certificate_repo', mock_certificate_repo), \
         patch.object(extensions, 'family_repo', mock_family_repo), \
         patch.object(extensions, 'military_repo', mock_military_repo), \
         patch.object(extensions, 'attachment_repo', mock_attachment_repo):
        yield employee_service


class TestEmployeeServiceInit:
    """EmployeeService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert employee_service is not None
        assert isinstance(employee_service, EmployeeService)

    def test_service_has_repo_attributes(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(employee_service, 'employee_repo')
        assert hasattr(employee_service, 'education_repo')
        assert hasattr(employee_service, 'career_repo')
        assert hasattr(employee_service, 'family_repo')


class TestEmployeeServiceAccessControl:
    """접근 권한 검증 테스트"""

    def test_verify_access_returns_false_without_org_id(self, mock_repos):
        """조직 ID 없을 때 접근 거부"""
        # Core 서비스의 get_current_org_id를 패치 (Facade는 Core에 위임)
        with patch.object(mock_repos.core, 'get_current_org_id', return_value=None):
            result = mock_repos.verify_access(1)
            assert result is False

    def test_verify_access_returns_true_with_ownership(self, mock_repos):
        """소유권 있을 때 접근 허용"""
        mock_repos.employee_repo.verify_ownership.return_value = True
        # Core 서비스의 get_current_org_id를 패치 (Facade는 Core에 위임)
        with patch.object(mock_repos.core, 'get_current_org_id', return_value=1):
            result = mock_repos.verify_access(100)
            mock_repos.employee_repo.verify_ownership.assert_called_once_with(100, 1)
            assert result is True


class TestEmployeeServiceRead:
    """직원 조회 테스트"""

    def test_get_employee_returns_none_without_access(self, mock_repos):
        """접근 권한 없을 때 None 반환"""
        # Core 서비스의 verify_access를 패치 (Facade는 Core에 위임)
        with patch.object(mock_repos.core, 'verify_access', return_value=False):
            result = mock_repos.get_employee(1)
            assert result is None

    def test_get_employee_returns_dict_with_access(self, mock_repos):
        """접근 권한 있을 때 Dict 반환"""
        mock_employee = Mock()
        mock_employee.to_dict.return_value = {'id': 1, 'name': '테스트'}
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        # Core 서비스의 verify_access를 패치 (Facade는 Core에 위임)
        with patch.object(mock_repos.core, 'verify_access', return_value=True):
            result = mock_repos.get_employee(1)
            assert result == {'id': 1, 'name': '테스트'}

    def test_get_employee_by_id_returns_dict(self, mock_repos):
        """ID로 직원 조회 시 Dict 반환"""
        mock_employee = Mock()
        mock_employee.to_dict.return_value = {'id': 1, 'name': '테스트'}
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        result = mock_repos.get_employee_by_id(1)
        assert result == {'id': 1, 'name': '테스트'}

    def test_get_employee_by_id_returns_none_when_not_found(self, mock_repos):
        """직원 없을 때 None 반환"""
        mock_repos.employee_repo.find_by_id.return_value = None

        result = mock_repos.get_employee_by_id(99999)
        assert result is None

    def test_get_all_employees_returns_list(self, mock_repos):
        """전체 직원 조회 시 List 반환"""
        mock_emp1 = Mock()
        mock_emp1.to_dict.return_value = {'id': 1, 'name': '직원1'}
        mock_emp2 = Mock()
        mock_emp2.to_dict.return_value = {'id': 2, 'name': '직원2'}
        mock_repos.employee_repo.find_all.return_value = [mock_emp1, mock_emp2]

        result = mock_repos.get_all_employees(organization_id=1)
        assert len(result) == 2
        assert result[0]['name'] == '직원1'
        assert result[1]['name'] == '직원2'


class TestEmployeeServiceRelations:
    """관계형 데이터 조회 테스트"""

    def test_get_education_list_returns_list(self, mock_repos):
        """학력 목록 조회"""
        mock_edu = Mock()
        mock_edu.to_dict.return_value = {'id': 1, 'school_name': '테스트대학'}
        mock_repos.education_repo.find_by_employee_id.return_value = [mock_edu]

        result = mock_repos.get_education_list(1)
        assert len(result) == 1
        assert result[0]['school_name'] == '테스트대학'

    def test_get_career_list_returns_list(self, mock_repos):
        """경력 목록 조회"""
        mock_career = Mock()
        mock_career.to_dict.return_value = {'id': 1, 'company_name': '테스트회사'}
        mock_repos.career_repo.find_by_employee_id.return_value = [mock_career]

        result = mock_repos.get_career_list(1)
        assert len(result) == 1
        assert result[0]['company_name'] == '테스트회사'

    def test_get_certificate_list_returns_list(self, mock_repos):
        """자격증 목록 조회"""
        mock_cert = Mock()
        mock_cert.to_dict.return_value = {'id': 1, 'name': '정보처리기사'}
        mock_repos.certificate_repo.find_by_employee_id.return_value = [mock_cert]

        result = mock_repos.get_certificate_list(1)
        assert len(result) == 1
        assert result[0]['name'] == '정보처리기사'

    def test_get_family_list_returns_list(self, mock_repos):
        """가족 목록 조회"""
        mock_family = Mock()
        mock_family.to_dict.return_value = {'id': 1, 'relation': '배우자'}
        mock_repos.family_repo.find_by_employee_id.return_value = [mock_family]

        result = mock_repos.get_family_list(1)
        assert len(result) == 1
        assert result[0]['relation'] == '배우자'

    def test_get_military_info_returns_dict(self, mock_repos):
        """병역 정보 조회"""
        mock_military = Mock()
        mock_military.to_dict.return_value = {'id': 1, 'military_status': '군필'}
        mock_repos.military_repo.find_by_employee_id.return_value = mock_military

        result = mock_repos.get_military_info(1)
        assert result['military_status'] == '군필'

    def test_get_military_info_returns_none_when_not_found(self, mock_repos):
        """병역 정보 없을 때 None 반환"""
        mock_repos.military_repo.find_by_employee_id.return_value = None

        result = mock_repos.get_military_info(1)
        assert result is None


class TestEmployeeServiceCRUD:
    """직원 CRUD 테스트"""

    def test_create_employee_direct_calls_repo(self, mock_repos):
        """직원 생성 시 Repository 호출"""
        test_data = {'name': '신규직원', 'department': '개발팀'}
        mock_repos.employee_repo.create.return_value = {'id': 1, **test_data}

        result = mock_repos.create_employee_direct(test_data)
        assert result['name'] == '신규직원'
        mock_repos.employee_repo.create.assert_called_once_with(test_data)

    def test_delete_employee_direct_returns_bool(self, mock_repos):
        """직원 삭제 성공 시 True 반환"""
        mock_repos.employee_repo.delete.return_value = True

        result = mock_repos.delete_employee_direct(1)
        assert result is True

    def test_delete_employee_direct_returns_false_when_not_found(self, mock_repos):
        """직원 삭제 실패 시 False 반환"""
        mock_repos.employee_repo.delete.return_value = False

        result = mock_repos.delete_employee_direct(99999)
        assert result is False


class TestEmployeeServiceAttachments:
    """첨부파일 관리 테스트"""

    def test_get_attachment_list_returns_list(self, mock_repos):
        """첨부파일 목록 조회"""
        mock_attachment = Mock()
        mock_attachment.to_dict.return_value = {'id': 1, 'filename': 'test.pdf'}
        mock_repos.attachment_repo.find_by_employee_id.return_value = [mock_attachment]

        result = mock_repos.get_attachment_list(1)
        assert len(result) == 1
        assert result[0]['filename'] == 'test.pdf'

    def test_create_attachment_calls_repo(self, mock_repos):
        """첨부파일 생성 시 Repository 호출"""
        test_data = {'employee_id': 1, 'filename': 'test.pdf'}
        mock_repos.attachment_repo.create.return_value = {'id': 1, **test_data}

        result = mock_repos.create_attachment(test_data)
        assert result['filename'] == 'test.pdf'

    def test_delete_attachment_returns_bool(self, mock_repos):
        """첨부파일 삭제 성공 시 True 반환"""
        mock_repos.attachment_repo.delete.return_value = True

        result = mock_repos.delete_attachment(1)
        assert result is True


class TestEmployeeServiceStatistics:
    """통계 조회 테스트"""

    def test_get_statistics_calls_repo(self, mock_repos):
        """통계 조회 시 Repository 호출"""
        expected = {'total': 100, 'active': 90, 'resigned': 10}
        mock_repos.employee_repo.get_statistics.return_value = expected

        result = mock_repos.get_statistics(organization_id=1)
        assert result['total'] == 100
        mock_repos.employee_repo.get_statistics.assert_called_once_with(organization_id=1)

    def test_search_employees_calls_repo(self, mock_repos):
        """직원 검색 시 Repository 호출"""
        expected = [{'id': 1, 'name': '홍길동'}]
        mock_repos.employee_repo.search.return_value = expected

        result = mock_repos.search_employees('홍길동', organization_id=1)
        assert len(result) == 1
        assert result[0]['name'] == '홍길동'
