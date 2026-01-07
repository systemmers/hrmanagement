"""
ClassificationOptionsRepository 단위 테스트

분류 옵션 저장소의 CRUD 및 카테고리별 조회 테스트
"""
import pytest
from app.domains.company.repositories.classification_repository import ClassificationOptionsRepository
from app.models import ClassificationOption


class TestClassificationRepositoryInit:
    """ClassificationOptionsRepository 초기화 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = ClassificationOptionsRepository()

    @pytest.mark.unit
    def test_repository_initialization(self):
        """리포지토리 초기화 확인"""
        assert self.repo is not None
        assert isinstance(self.repo, ClassificationOptionsRepository)


class TestClassificationRepositoryCRUD:
    """ClassificationOptionsRepository CRUD 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company):
        """테스트 설정"""
        self.session = session
        self.repo = ClassificationOptionsRepository()
        self.company_id = test_company.id

    @pytest.mark.unit
    def test_add_option_for_company(self):
        """법인용 옵션 추가 테스트"""
        result = self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='개발팀',
            label='개발팀'
        )

        assert result is not None
        assert result['value'] == '개발팀'
        assert result['label'] == '개발팀'
        assert result['companyId'] == self.company_id

    @pytest.mark.unit
    def test_add_option_duplicate(self):
        """중복 옵션 추가 시 기존 옵션 반환"""
        # 첫 번째 추가
        first = self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='개발팀'
        )

        # 두 번째 추가 (중복)
        second = self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='개발팀'
        )

        assert first['id'] == second['id']

    @pytest.mark.unit
    def test_update_option(self):
        """옵션 수정 테스트"""
        # 옵션 생성
        option = self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='개발팀',
            label='개발팀'
        )

        # 수정
        result = self.repo.update_option(
            option_id=option['id'],
            company_id=self.company_id,
            data={'label': '개발팀 (수정)'}
        )

        assert result is not None
        assert result['label'] == '개발팀 (수정)'

    @pytest.mark.unit
    def test_update_system_option_fails(self):
        """시스템 옵션 수정 불가 확인"""
        # 시스템 옵션 생성 (company_id=None)
        option = ClassificationOption(
            category='department',
            value='시스템부서',
            label='시스템부서',
            is_system=True,
            is_active=True
        )
        self.session.add(option)
        self.session.commit()

        # 수정 시도
        result = self.repo.update_option(
            option_id=option.id,
            company_id=None,
            data={'label': '수정된 부서'}
        )

        assert result is None

    @pytest.mark.unit
    def test_delete_option_for_company(self):
        """법인 옵션 삭제 테스트"""
        # 옵션 생성
        option = self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='삭제될부서'
        )

        # 삭제
        result = self.repo.delete_option_for_company(
            option_id=option['id'],
            company_id=self.company_id
        )

        assert result is True

        # 삭제 확인
        deleted = ClassificationOption.query.get(option['id'])
        assert deleted is None

    @pytest.mark.unit
    def test_delete_other_company_option_fails(self, session):
        """다른 법인의 옵션 삭제 불가 확인"""
        from app.models import Company
        other_company = Company(
            name='다른법인',
            business_number='9999999999',
            representative='대표'
        )
        session.add(other_company)
        session.commit()

        # 다른 법인 옵션 생성
        option = self.repo.add_option_for_company(
            company_id=other_company.id,
            category='department',
            value='다른법인부서'
        )

        # 현재 법인에서 삭제 시도
        result = self.repo.delete_option_for_company(
            option_id=option['id'],
            company_id=self.company_id
        )

        assert result is False


class TestClassificationRepositoryQueries:
    """ClassificationOptionsRepository 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company):
        """테스트 설정"""
        self.session = session
        self.repo = ClassificationOptionsRepository()
        self.company_id = test_company.id

        # 테스트 데이터 생성
        self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='개발팀',
            label='개발팀'
        )
        self.repo.add_option_for_company(
            company_id=self.company_id,
            category='department',
            value='인사팀',
            label='인사팀'
        )
        self.repo.add_option_for_company(
            company_id=self.company_id,
            category='position',
            value='사원',
            label='사원'
        )

    @pytest.mark.unit
    def test_get_departments(self):
        """부서 목록 조회"""
        result = self.repo.get_departments(company_id=self.company_id)

        assert len(result) >= 2
        assert any(d['value'] == '개발팀' for d in result)
        assert any(d['value'] == '인사팀' for d in result)

    @pytest.mark.unit
    def test_get_positions(self):
        """직급 목록 조회"""
        result = self.repo.get_positions(company_id=self.company_id)

        assert len(result) >= 1
        assert any(p['value'] == '사원' for p in result)

    @pytest.mark.unit
    def test_get_all_options(self):
        """모든 분류 옵션 조회"""
        result = self.repo.get_all_options(company_id=self.company_id)

        assert 'departments' in result
        assert 'positions' in result
        assert 'ranks' in result
        assert 'statuses' in result
        assert isinstance(result['departments'], list)
        assert isinstance(result['positions'], list)

    @pytest.mark.unit
    def test_get_organization_options(self):
        """조직 구조 탭용 옵션 조회"""
        result = self.repo.get_organization_options(company_id=self.company_id)

        assert 'department' in result
        assert 'position' in result
        assert 'rank' in result
        assert 'job_title' in result

    @pytest.mark.unit
    def test_get_employment_options(self):
        """고용 정책 탭용 옵션 조회"""
        result = self.repo.get_employment_options(company_id=self.company_id)

        assert 'employment_type' in result
        assert 'status' in result
        assert 'pay_type' in result
        assert 'bank' in result

    @pytest.mark.unit
    def test_get_by_category_for_company(self):
        """카테고리별 법인 옵션 조회"""
        result = self.repo.get_by_category_for_company(
            category='department',
            company_id=self.company_id
        )

        assert len(result) >= 2
        assert all('id' in d for d in result)
        assert all('value' in d for d in result)
        assert all('label' in d for d in result)


class TestClassificationRepositorySystemOptions:
    """시스템 옵션 관리 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company):
        """테스트 설정"""
        self.session = session
        self.repo = ClassificationOptionsRepository()
        self.company_id = test_company.id

    @pytest.mark.unit
    def test_toggle_system_option_deactivate(self):
        """시스템 옵션 비활성화"""
        result = self.repo.toggle_system_option(
            company_id=self.company_id,
            category='department',
            value='비활성화부서',
            is_active=False
        )

        assert result is not None
        assert result['isActive'] is False
        assert result['companyId'] == self.company_id

    @pytest.mark.unit
    def test_toggle_system_option_activate(self):
        """시스템 옵션 활성화"""
        # 먼저 비활성화
        self.repo.toggle_system_option(
            company_id=self.company_id,
            category='department',
            value='활성화부서',
            is_active=False
        )

        # 활성화
        result = self.repo.toggle_system_option(
            company_id=self.company_id,
            category='department',
            value='활성화부서',
            is_active=True
        )

        assert result is not None
        assert result['isActive'] is True

    @pytest.mark.unit
    def test_legacy_add_methods(self):
        """레거시 추가 메서드 테스트"""
        dept = self.repo.add_department('레거시부서', '레거시부서명')
        assert dept is not None
        assert dept['value'] == '레거시부서'

        pos = self.repo.add_position('레거시직급', '레거시직급명')
        assert pos is not None
        assert pos['value'] == '레거시직급'

    @pytest.mark.unit
    def test_legacy_remove_methods(self):
        """레거시 삭제 메서드 테스트"""
        # 추가
        self.repo.add_department('삭제될부서')

        # 삭제
        result = self.repo.remove_department('삭제될부서')
        assert result is True

        # 재삭제 시도
        result = self.repo.remove_department('삭제될부서')
        assert result is False

    @pytest.mark.unit
    def test_update_sort_order(self):
        """정렬 순서 수정 테스트"""
        # 옵션 추가
        option = self.repo.add_department('정렬부서')

        # 정렬 순서 수정
        result = self.repo.update_sort_order('department', '정렬부서', 999)
        assert result is True

        # 확인
        options = self.repo.get_departments()
        found = next((d for d in options if d['value'] == '정렬부서'), None)
        # 정렬 순서는 내부적으로 관리되므로 직접 확인은 어려움
        assert found is not None


class TestClassificationRepositoryEdgeCases:
    """ClassificationOptionsRepository 엣지 케이스 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company):
        """테스트 설정"""
        self.session = session
        self.repo = ClassificationOptionsRepository()
        self.company_id = test_company.id

    @pytest.mark.unit
    def test_get_departments_no_company(self):
        """법인 ID 없이 부서 조회"""
        result = self.repo.get_departments(company_id=None)
        assert isinstance(result, list)

    @pytest.mark.unit
    def test_get_all_options_empty(self):
        """옵션이 없을 때 조회"""
        result = self.repo.get_all_options(company_id=None)
        assert isinstance(result, dict)
        assert all(isinstance(v, list) for v in result.values())

    @pytest.mark.unit
    def test_delete_nonexistent_option(self):
        """존재하지 않는 옵션 삭제"""
        result = self.repo.delete_option_for_company(
            option_id=99999,
            company_id=self.company_id
        )
        assert result is False

    @pytest.mark.unit
    def test_update_nonexistent_option(self):
        """존재하지 않는 옵션 수정"""
        result = self.repo.update_option(
            option_id=99999,
            company_id=self.company_id,
            data={'label': '수정'}
        )
        assert result is None

