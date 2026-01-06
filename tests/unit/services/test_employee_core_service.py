"""
EmployeeCoreService 단위 테스트

직원 기본 CRUD 및 멀티테넌시 접근 제어 테스트:
- 직원 조회
- 접근 권한 확인
- 통계 조회
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.employee.services.employee_core_service import (
    EmployeeCoreService,
    employee_core_service
)


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_employee_repo = Mock()
    with patch.object(extensions, 'employee_repo', mock_employee_repo):
        yield employee_core_service


class TestEmployeeCoreServiceInit:
    """EmployeeCoreService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert employee_core_service is not None
        assert isinstance(employee_core_service, EmployeeCoreService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(employee_core_service, 'employee_repo')


class TestEmployeeCoreServiceAccessControl:
    """접근 제어 테스트"""

    def test_get_current_org_id(self, mock_repos):
        """현재 조직 ID 조회"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            org_id = mock_repos.get_current_org_id()
            assert org_id == 1

    def test_verify_access_success(self, mock_repos):
        """접근 권한 확인 - 성공"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            mock_repos.employee_repo.verify_ownership.return_value = True

            result = mock_repos.verify_access(employee_id=1)

            assert result is True
            mock_repos.employee_repo.verify_ownership.assert_called_once_with(1, 1)

    def test_verify_access_no_org(self, mock_repos):
        """접근 권한 확인 - 조직 없음"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=None):
            result = mock_repos.verify_access(employee_id=1)

            assert result is False

    def test_verify_ownership(self, mock_repos):
        """소유권 확인"""
        mock_repos.employee_repo.verify_ownership.return_value = True

        result = mock_repos.verify_ownership(employee_id=1, org_id=1)

        assert result is True


class TestEmployeeCoreServiceQueries:
    """조회 테스트"""

    def test_get_employee_success(self, mock_repos):
        """직원 조회 성공"""
        mock_employee = Mock()
        mock_employee.to_dict.return_value = {'id': 1, 'name': '테스트'}

        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            mock_repos.employee_repo.verify_ownership.return_value = True
            mock_repos.employee_repo.find_by_id.return_value = mock_employee

            result = mock_repos.get_employee(employee_id=1)

            assert result is not None
            assert result['id'] == 1
            assert result['name'] == '테스트'

    def test_get_employee_no_access(self, mock_repos):
        """직원 조회 - 접근 권한 없음"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            mock_repos.employee_repo.verify_ownership.return_value = False

            result = mock_repos.get_employee(employee_id=1)

            assert result is None

    def test_get_employee_not_found(self, mock_repos):
        """직원 조회 - 직원 없음"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            mock_repos.employee_repo.verify_ownership.return_value = True
            mock_repos.employee_repo.find_by_id.return_value = None

            result = mock_repos.get_employee(employee_id=999)

            assert result is None

    def test_get_employees_by_org(self, mock_repos):
        """조직별 직원 목록 조회"""
        mock_employees = [Mock(), Mock()]

        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=1):
            mock_repos.employee_repo.get_by_company_id.return_value = mock_employees

            result = mock_repos.get_employees_by_org()

            assert len(result) == 2
            mock_repos.employee_repo.get_by_company_id.assert_called_once_with(1)

    def test_get_employees_by_org_no_org(self, mock_repos):
        """조직별 직원 목록 조회 - 조직 없음"""
        with patch('app.services.employee.employee_core_service.get_current_organization_id', return_value=None):
            result = mock_repos.get_employees_by_org()

            assert len(result) == 0

    def test_get_employee_by_id(self, mock_repos):
        """ID로 직원 조회"""
        mock_employee = Mock()
        mock_employee.to_dict.return_value = {'id': 1, 'name': '테스트'}
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        result = mock_repos.get_employee_by_id(employee_id=1)

        assert result is not None
        assert result['id'] == 1

    def test_get_employee_model_by_id(self, mock_repos):
        """ID로 직원 모델 조회"""
        mock_employee = Mock()
        mock_repos.employee_repo.find_by_id.return_value = mock_employee

        result = mock_repos.get_employee_model_by_id(employee_id=1)

        assert result is not None
        assert result == mock_employee

    def test_filter_employees(self, mock_repos):
        """직원 필터링"""
        mock_result = [{'id': 1, 'name': '테스트'}]
        mock_repos.employee_repo.filter_employees.return_value = mock_result

        result = mock_repos.filter_employees(status='active')

        assert len(result) == 1
        assert result[0]['id'] == 1

    def test_get_all_employees(self, mock_repos):
        """전체 직원 조회"""
        mock_employees = [Mock(), Mock()]
        for emp in mock_employees:
            emp.to_dict.return_value = {'id': 1}
        mock_repos.employee_repo.find_all.return_value = mock_employees

        result = mock_repos.get_all_employees(organization_id=1)

        assert len(result) == 2
        mock_repos.employee_repo.find_all.assert_called_once_with(organization_id=1)


class TestEmployeeCoreServiceCRUD:
    """CRUD 테스트"""

    def test_create_employee_direct(self, mock_repos):
        """직원 직접 생성"""
        employee_data = {'name': '테스트', 'department': '개발팀'}
        mock_repos.employee_repo.create.return_value = {'id': 1, **employee_data}

        result = mock_repos.create_employee_direct(employee_data)

        assert result['id'] == 1
        assert result['name'] == '테스트'
        mock_repos.employee_repo.create.assert_called_once_with(employee_data)

    def test_update_employee_direct(self, mock_repos):
        """직원 직접 수정"""
        mock_employee = Mock()
        mock_repos.employee_repo.update.return_value = mock_employee

        result = mock_repos.update_employee_direct(employee_id=1, employee=mock_employee)

        assert result is not None
        mock_repos.employee_repo.update.assert_called_once_with(1, mock_employee)

    def test_update_employee_partial(self, mock_repos):
        """직원 부분 수정"""
        fields = {'name': '변경된 이름'}
        mock_employee = Mock()
        mock_repos.employee_repo.update_partial.return_value = mock_employee

        result = mock_repos.update_employee_partial(employee_id=1, fields=fields)

        assert result is not None
        mock_repos.employee_repo.update_partial.assert_called_once_with(1, fields)

    def test_delete_employee_direct(self, mock_repos):
        """직원 직접 삭제"""
        mock_repos.employee_repo.delete.return_value = True

        result = mock_repos.delete_employee_direct(employee_id=1)

        assert result is True
        mock_repos.employee_repo.delete.assert_called_once_with(1)


class TestEmployeeCoreServiceStatistics:
    """통계 테스트"""

    def test_get_statistics(self, mock_repos):
        """직원 통계 조회"""
        mock_stats = {'total': 100, 'active': 90}
        mock_repos.employee_repo.get_statistics.return_value = mock_stats

        result = mock_repos.get_statistics(organization_id=1)

        assert result['total'] == 100
        assert result['active'] == 90

    def test_get_department_statistics(self, mock_repos):
        """부서별 통계 조회"""
        mock_stats = [
            {'department': '개발팀', 'count': 10},
            {'department': '영업팀', 'count': 5}
        ]
        mock_repos.employee_repo.get_department_statistics.return_value = mock_stats

        result = mock_repos.get_department_statistics(organization_id=1)

        assert len(result) == 2
        assert result[0]['department'] == '개발팀'

    def test_get_recent_employees(self, mock_repos):
        """최근 입사 직원 조회"""
        mock_employees = [
            {'id': 1, 'name': '직원1'},
            {'id': 2, 'name': '직원2'}
        ]
        mock_repos.employee_repo.get_recent_employees.return_value = mock_employees

        result = mock_repos.get_recent_employees(organization_id=1, limit=2)

        assert len(result) == 2
        mock_repos.employee_repo.get_recent_employees.assert_called_once_with(
            limit=2,
            organization_id=1
        )

    def test_search_employees(self, mock_repos):
        """직원 검색"""
        mock_results = [{'id': 1, 'name': '검색결과'}]
        mock_repos.employee_repo.search.return_value = mock_results

        result = mock_repos.search_employees(query='검색어', organization_id=1)

        assert len(result) == 1
        mock_repos.employee_repo.search.assert_called_once_with('검색어', organization_id=1)

