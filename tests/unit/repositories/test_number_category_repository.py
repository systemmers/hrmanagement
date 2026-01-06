"""
NumberCategoryRepository 단위 테스트

번호 체계 분류코드 관리 기능 테스트
"""
import pytest
from app.repositories.number_category_repository import NumberCategoryRepository
from app.models import NumberCategory
from app.models import Company


class TestNumberCategoryRepositoryInit:
    """NumberCategoryRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = NumberCategoryRepository()
        assert repo is not None
        assert repo.model_class == NumberCategory


class TestNumberCategoryRepositoryQuery:
    """분류코드 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = NumberCategoryRepository()

    def test_get_by_company(self, session):
        """법인별 분류코드 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category1 = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='EMP',
            name='직원',
            is_active=True
        )
        category2 = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_ASSET,
            code='PC',
            name='컴퓨터',
            is_active=True
        )
        session.add_all([category1, category2])
        session.commit()

        result = self.repo.get_by_company(company.id)

        assert len(result) >= 2

    def test_get_by_company_with_type_filter(self, session):
        """법인별 특정 타입 분류코드 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category1 = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='EMP',
            name='직원',
            is_active=True
        )
        category2 = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_ASSET,
            code='PC',
            name='컴퓨터',
            is_active=True
        )
        session.add_all([category1, category2])
        session.commit()

        result = self.repo.get_by_company(company.id, NumberCategory.TYPE_EMPLOYEE)

        assert len(result) >= 1
        assert all(c['type'] == NumberCategory.TYPE_EMPLOYEE for c in result)

    def test_get_employee_categories(self, session):
        """사번 분류코드 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='EMP',
            name='직원',
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.get_employee_categories(company.id)

        assert len(result) >= 1
        assert all(c['type'] == NumberCategory.TYPE_EMPLOYEE for c in result)

    def test_get_asset_categories(self, session):
        """자산번호 분류코드 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_ASSET,
            code='PC',
            name='컴퓨터',
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.get_asset_categories(company.id)

        assert len(result) >= 1
        assert all(c['type'] == NumberCategory.TYPE_ASSET for c in result)

    def test_get_by_code(self, session):
        """코드로 분류 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='EMP',
            name='직원',
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.get_by_code(company.id, NumberCategory.TYPE_EMPLOYEE, 'emp')

        assert result is not None
        assert result['code'] == 'EMP'

    def test_get_by_code_not_found(self, session):
        """코드로 분류 조회 (미존재)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_by_code(company.id, NumberCategory.TYPE_EMPLOYEE, 'NONE')
        assert result is None


class TestNumberCategoryRepositoryCreate:
    """분류코드 생성 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = NumberCategoryRepository()

    def test_create_category(self, session):
        """분류코드 생성"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.create_category(
            company_id=company.id,
            type_code=NumberCategory.TYPE_EMPLOYEE,
            code='TEST',
            name='테스트',
            description='테스트 분류'
        )

        assert result is not None
        assert result['code'] == 'TEST'
        assert result['name'] == '테스트'

    def test_create_category_duplicate(self, session):
        """중복 분류코드 생성 (기존 반환)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        # 첫 생성
        result1 = self.repo.create_category(
            company_id=company.id,
            type_code=NumberCategory.TYPE_EMPLOYEE,
            code='DUP',
            name='중복'
        )

        # 중복 생성
        result2 = self.repo.create_category(
            company_id=company.id,
            type_code=NumberCategory.TYPE_EMPLOYEE,
            code='DUP',
            name='중복2'
        )

        assert result1['id'] == result2['id']


class TestNumberCategoryRepositoryUpdate:
    """분류코드 수정 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = NumberCategoryRepository()

    def test_update_category(self, session):
        """분류코드 수정"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='UPD',
            name='수정전',
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.update_category(
            category_id=category.id,
            company_id=company.id,
            data={'name': '수정후', 'isActive': False}
        )

        assert result is not None
        assert result['name'] == '수정후'
        assert result['isActive'] is False

    def test_update_category_not_found(self, session):
        """존재하지 않는 분류코드 수정"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.update_category(
            category_id=999,
            company_id=company.id,
            data={'name': '수정'}
        )

        assert result is None


class TestNumberCategoryRepositoryDelete:
    """분류코드 삭제 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = NumberCategoryRepository()

    def test_delete_category(self, session):
        """분류코드 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='DEL',
            name='삭제',
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.delete_category(category.id, company.id)

        assert result is True

        # 실제로 삭제되었는지 확인
        deleted = NumberCategory.query.get(category.id)
        assert deleted is None

    def test_delete_category_not_found(self, session):
        """존재하지 않는 분류코드 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.delete_category(999, company.id)

        assert result is False


class TestNumberCategoryRepositoryNumber:
    """번호 생성 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = NumberCategoryRepository()

    def test_preview_next_number(self, session):
        """다음 번호 미리보기"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        category = NumberCategory(
            company_id=company.id,
            type=NumberCategory.TYPE_EMPLOYEE,
            code='EMP',
            name='직원',
            current_sequence=10,
            is_active=True
        )
        session.add(category)
        session.commit()

        result = self.repo.preview_next_number(category.id, 'TEST', '-', 4)

        assert result == 'TEST-EMP-0011'

    def test_preview_next_number_not_found(self, session):
        """존재하지 않는 카테고리 번호 미리보기"""
        result = self.repo.preview_next_number(999, 'TEST', '-', 4)
        assert result is None

