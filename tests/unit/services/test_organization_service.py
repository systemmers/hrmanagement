"""
OrganizationService 단위 테스트

조직 서비스의 핵심 비즈니스 로직 테스트:
- 조직 트리 조회
- 조직 검색
- 조직 통계
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.company.services.organization_service import OrganizationService, organization_service


@pytest.fixture
def mock_repos(app):
    """Service의 Repository를 Mock으로 대체하는 fixture"""
    from app import extensions

    mock_org_repo = Mock()
    with patch.object(extensions, 'organization_repo', mock_org_repo):
        yield organization_service


class TestOrganizationServiceInit:
    """OrganizationService 초기화 테스트"""

    def test_service_instance_exists(self, app):
        """서비스 인스턴스 존재 확인"""
        assert organization_service is not None
        assert isinstance(organization_service, OrganizationService)

    def test_service_has_repo_property(self, app):
        """Service에 repository 속성 존재 확인"""
        assert hasattr(organization_service, 'organization_repo')


class TestOrganizationServiceQueries:
    """조직 조회 테스트"""

    def test_get_tree_success(self, mock_repos):
        """조직 트리 조회 성공"""
        expected = [{'id': 1, 'name': '본사', 'children': []}]
        mock_repos.organization_repo.get_tree.return_value = expected

        result = mock_repos.get_tree(root_organization_id=1)

        assert result == expected
        mock_repos.organization_repo.get_tree.assert_called_once_with(root_organization_id=1)

    def test_get_flat_list_success(self, mock_repos):
        """조직 평탄화 목록 조회 성공"""
        expected = [{'id': 1, 'name': '본사'}, {'id': 2, 'name': '개발팀'}]
        mock_repos.organization_repo.get_flat_list.return_value = expected

        result = mock_repos.get_flat_list(root_organization_id=1)

        assert result == expected

    def test_get_by_id_success(self, mock_repos):
        """조직 ID로 조회 성공"""
        mock_org = Mock()
        mock_org.to_dict.return_value = {'id': 1, 'name': '본사'}
        mock_repos.organization_repo.find_by_id.return_value = mock_org

        result = mock_repos.get_by_id(org_id=1)

        assert result is not None
        assert result['id'] == 1

    def test_get_by_id_not_found(self, mock_repos):
        """조직을 찾을 수 없을 때"""
        mock_repos.organization_repo.find_by_id.return_value = None

        result = mock_repos.get_by_id(org_id=999)

        assert result is None

    def test_get_children_success(self, mock_repos):
        """하위 조직 조회 성공"""
        expected = [{'id': 2, 'name': '개발팀'}]
        mock_repos.organization_repo.get_children.return_value = expected

        result = mock_repos.get_children(org_id=1)

        assert result == expected

    def test_search_success(self, mock_repos):
        """조직 검색 성공"""
        expected = [{'id': 1, 'name': '개발팀'}]
        mock_repos.organization_repo.search.return_value = expected

        result = mock_repos.search(query='개발', root_organization_id=1)

        assert len(result) == 1
        assert '개발' in result[0]['name']


class TestOrganizationServiceStatistics:
    """조직 통계 테스트"""

    def test_get_organization_statistics_success(self, mock_repos):
        """조직 통계 조회 성공"""
        expected = {'total': 10, 'departments': 5}
        mock_repos.organization_repo.get_organization_statistics.return_value = expected

        result = mock_repos.get_organization_statistics(root_organization_id=1)

        assert result == expected
        assert result['total'] == 10


class TestOrganizationServiceCRUD:
    """조직 CRUD 테스트"""

    def test_create_organization_success(self, mock_repos):
        """조직 생성 성공"""
        expected = Mock(id=1, name='신규팀')
        mock_repos.organization_repo.create_organization.return_value = expected

        result = mock_repos.create_organization(
            name='신규팀',
            org_type='department',
            parent_id=1
        )

        assert result.id == 1
        mock_repos.organization_repo.create_organization.assert_called_once()

    def test_update_organization_success(self, mock_repos):
        """조직 수정 성공"""
        expected = Mock()
        expected.id = 1
        expected.name = '수정된팀'
        mock_repos.organization_repo.update_organization.return_value = expected

        result = mock_repos.update_organization(
            org_id=1,
            data={'name': '수정된팀'}
        )

        assert result is not None
        assert result.name == '수정된팀'

    def test_update_organization_not_found(self, mock_repos):
        """존재하지 않는 조직 수정"""
        mock_repos.organization_repo.update_organization.return_value = None

        result = mock_repos.update_organization(org_id=999, data={})

        assert result is None

    def test_deactivate_organization_success(self, mock_repos):
        """조직 비활성화 성공"""
        mock_repos.organization_repo.deactivate.return_value = True

        result = mock_repos.deactivate(org_id=1, cascade=False)

        assert result is True
        mock_repos.organization_repo.deactivate.assert_called_once_with(
            1, cascade=False, root_organization_id=None
        )

    def test_deactivate_organization_with_cascade(self, mock_repos):
        """하위 조직 포함 비활성화"""
        mock_repos.organization_repo.deactivate.return_value = True

        result = mock_repos.deactivate(org_id=1, cascade=True)

        assert result is True

    def test_move_organization_success(self, mock_repos):
        """조직 이동 성공"""
        mock_repos.organization_repo.move_organization.return_value = True

        result = mock_repos.move_organization(
            org_id=1,
            new_parent_id=2
        )

        assert result is True


class TestOrganizationServiceValidation:
    """조직 검증 테스트"""

    def test_verify_ownership_success(self, mock_repos):
        """조직 소유권 검증 성공"""
        mock_repos.organization_repo.verify_ownership.return_value = True

        result = mock_repos.verify_ownership(org_id=1, root_organization_id=10)

        assert result is True

    def test_verify_ownership_fail(self, mock_repos):
        """조직 소유권 검증 실패"""
        mock_repos.organization_repo.verify_ownership.return_value = False

        result = mock_repos.verify_ownership(org_id=1, root_organization_id=10)

        assert result is False

    def test_code_exists_true(self, mock_repos):
        """조직 코드 중복 존재"""
        mock_repos.organization_repo.code_exists.return_value = True

        result = mock_repos.code_exists(code='DEPT001')

        assert result is True

    def test_code_exists_false(self, mock_repos):
        """조직 코드 중복 없음"""
        mock_repos.organization_repo.code_exists.return_value = False

        result = mock_repos.code_exists(code='DEPT999')

        assert result is False

    def test_code_exists_with_exclude(self, mock_repos):
        """특정 조직 제외하고 코드 중복 검사"""
        mock_repos.organization_repo.code_exists.return_value = False

        result = mock_repos.code_exists(code='DEPT001', exclude_id=1)

        assert result is False
        mock_repos.organization_repo.code_exists.assert_called_once_with(
            'DEPT001', exclude_id=1, root_organization_id=None
        )