"""
OrganizationRepository 단위 테스트

조직 저장소의 핵심 기능 테스트:
- 조직 CRUD
- 트리 구조 조회
- 멀티테넌시 필터링
"""
import pytest
from app.repositories.organization_repository import OrganizationRepository
from app.models.organization import Organization
from app.models.company import Company


class TestOrganizationRepositoryInit:
    """OrganizationRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = OrganizationRepository()
        assert repo is not None
        assert repo.model_class == Organization


class TestOrganizationRepositoryCRUD:
    """조직 CRUD 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = OrganizationRepository()

    def test_create_organization(self, session):
        """조직 생성"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        data = {
            'name': '인사팀',
            'code': 'HR',
            'org_type': 'department',
            'is_active': True
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['name'] == '인사팀'
        assert result['code'] == 'HR'

    def test_find_by_id(self, session):
        """ID로 조직 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        org = Organization(name='인사팀', code='HR', org_type='department')
        session.add(org)
        session.commit()

        result = self.repo.find_by_id(org.id)

        assert result is not None
        assert isinstance(result, Organization)
        assert result.name == '인사팀'

    def test_get_by_code(self, session):
        """조직 코드로 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        org = Organization(name='인사팀', code='HR', org_type='department', is_active=True)
        session.add(org)
        session.commit()

        result = self.repo.get_by_code('HR')

        assert result is not None
        assert result.name == '인사팀'

    def test_get_all_organizations(self, session):
        """모든 조직 목록 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        org1 = Organization(name='인사팀', code='HR', org_type='department')
        org2 = Organization(name='개발팀', code='DEV', org_type='department')
        session.add_all([org1, org2])
        session.commit()

        result = self.repo.find_all()

        assert len(result) >= 2
        names = [o.name for o in result]
        assert '인사팀' in names
        assert '개발팀' in names

    def test_update_organization(self, session):
        """조직 업데이트"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        org = Organization(name='인사팀', code='HR', org_type='department')
        session.add(org)
        session.commit()

        result = self.repo.update(org.id, {'name': '인사관리팀'})

        assert result is not None
        assert result['name'] == '인사관리팀'
        updated = self.repo.find_by_id(org.id)
        assert updated.name == '인사관리팀'

    def test_delete_organization(self, session):
        """조직 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        org = Organization(name='인사팀', code='HR', org_type='department')
        session.add(org)
        session.commit()

        result = self.repo.delete(org.id)

        assert result is True
        deleted = self.repo.find_by_id(org.id)
        assert deleted is None


class TestOrganizationRepositoryTree:
    """조직 트리 구조 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = OrganizationRepository()

    def test_get_root_organizations(self, session):
        """최상위 조직 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        root_org = Organization(name='본사', code='HQ', org_type='company', parent_id=None)
        session.add(root_org)
        session.commit()

        result = self.repo.get_root_organizations(root_org.id)

        assert len(result) >= 1
        assert any(o['name'] == '본사' for o in result)

    def test_get_children(self, session):
        """하위 조직 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        parent = Organization(name='본사', code='HQ', org_type='company')
        session.add(parent)
        session.commit()

        child1 = Organization(name='인사팀', code='HR', org_type='department', parent_id=parent.id)
        child2 = Organization(name='개발팀', code='DEV', org_type='department', parent_id=parent.id)
        session.add_all([child1, child2])
        session.commit()

        result = self.repo.get_children(parent.id)

        assert len(result) == 2
        assert all(o['parent_id'] == parent.id for o in result)


class TestOrganizationRepositoryTenant:
    """멀티테넌시 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = OrganizationRepository()

    def test_verify_ownership(self, session):
        """조직 소유권 확인"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        root_org = Organization(name='본사', code='HQ', org_type='company', parent_id=None)
        session.add(root_org)
        session.commit()

        child_org = Organization(name='인사팀', code='HR', org_type='department', parent_id=root_org.id)
        session.add(child_org)
        session.commit()

        result = self.repo.verify_ownership(child_org.id, root_org.id)

        assert result is True

    def test_filter_by_tenant(self, session):
        """테넌트 필터링"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        root_org = Organization(name='본사', code='HQ', org_type='company', parent_id=None)
        session.add(root_org)
        session.commit()

        query = Organization.query
        filtered_query = self.repo._filter_by_tenant(query, root_org.id)

        assert filtered_query is not None


class TestOrganizationRepositoryAdvanced:
    """조직 고급 기능 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = OrganizationRepository()

    def test_get_tree(self, session):
        """조직 트리 구조 조회"""
        root = Organization(name='본사', code='HQ', org_type='company', parent_id=None)
        session.add(root)
        session.commit()

        child = Organization(name='인사팀', code='HR', org_type='department', parent_id=root.id)
        session.add(child)
        session.commit()

        result = self.repo.get_tree(root.id)

        assert len(result) >= 1
        assert result[0]['name'] == '본사'
        assert 'children' in result[0]

    def test_get_flat_list(self, session):
        """플랫 조직 목록 조회"""
        org1 = Organization(name='본사', code='HQ', org_type='company')
        org2 = Organization(name='인사팀', code='HR', org_type='department')
        session.add_all([org1, org2])
        session.commit()

        result = self.repo.get_flat_list()

        assert len(result) >= 2
        assert any(o['name'] == '본사' for o in result)
        assert any(o['name'] == '인사팀' for o in result)

    def test_get_by_type(self, session):
        """조직 유형별 조회"""
        dept = Organization(name='인사팀', code='HR', org_type='department')
        team = Organization(name='개발팀', code='DEV', org_type='team')
        session.add_all([dept, team])
        session.commit()

        result = self.repo.get_by_type('department')

        assert len(result) >= 1
        assert all(o['org_type'] == 'department' for o in result)

    def test_get_departments(self, session):
        """부서 목록 조회"""
        dept = Organization(name='인사팀', code='HR', org_type='department')
        session.add(dept)
        session.commit()

        result = self.repo.get_departments()

        assert len(result) >= 1
        assert all(o['org_type'] == 'department' for o in result)

    def test_get_teams(self, session):
        """팀 목록 조회"""
        team = Organization(name='개발팀', code='DEV', org_type='team')
        session.add(team)
        session.commit()

        result = self.repo.get_teams()

        assert len(result) >= 1
        assert all(o['org_type'] == 'team' for o in result)

    def test_get_ancestors(self, session):
        """상위 조직 조회"""
        root = Organization(name='본사', code='HQ', org_type='company')
        session.add(root)
        session.commit()

        child = Organization(name='인사팀', code='HR', org_type='department', parent_id=root.id)
        session.add(child)
        session.commit()

        result = self.repo.get_ancestors(child.id)

        assert len(result) >= 1
        assert any(o['name'] == '본사' for o in result)

    def test_get_descendants(self, session):
        """하위 조직 조회"""
        root = Organization(name='본사', code='HQ', org_type='company')
        session.add(root)
        session.commit()

        child = Organization(name='인사팀', code='HR', org_type='department', parent_id=root.id)
        session.add(child)
        session.commit()

        result = self.repo.get_descendants(root.id)

        assert len(result) >= 1
        assert any(o['name'] == '인사팀' for o in result)

    def test_move_organization(self, session):
        """조직 이동"""
        org1 = Organization(name='부서A', code='DEPT_A', org_type='department')
        org2 = Organization(name='부서B', code='DEPT_B', org_type='department')
        session.add_all([org1, org2])
        session.commit()

        target = Organization(name='팀C', code='TEAM_C', org_type='team', parent_id=org1.id)
        session.add(target)
        session.commit()

        result = self.repo.move_organization(target.id, org2.id)

        assert result is True
        updated = self.repo.find_by_id(target.id)
        assert updated.parent_id == org2.id

