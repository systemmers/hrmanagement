"""
CompanyRepository 단위 테스트
"""
import pytest
from app.domains.company.repositories.company_repository import CompanyRepository
from app.domains.company.models import Company


class TestCompanyRepository:
    """CompanyRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanyRepository()

    @pytest.mark.unit
    def test_create_company(self, session):
        """법인 생성 테스트"""
        data = {
            'name': '테스트법인',
            'business_number': '1234567890',
            'representative': '홍길동',
            'business_type': '서비스업',
            'address': '서울시 강남구'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['name'] == '테스트법인'
        assert result['business_number'] == '1234567890'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_id(self, session):
        """ID로 법인 조회 테스트"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동'
        )
        session.add(company)
        session.commit()

        result = self.repo.find_by_id(company.id)

        assert result is not None
        assert isinstance(result, Company)
        assert result.name == '테스트법인'

    @pytest.mark.unit
    def test_get_by_business_number(self, session):
        """사업자등록번호로 법인 조회"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동'
        )
        session.add(company)
        session.commit()

        result = self.repo.get_by_business_number('123-456-7890')

        assert result is not None
        assert result['name'] == '테스트법인'

    @pytest.mark.unit
    def test_get_by_name(self, session):
        """법인명으로 검색"""
        company1 = Company(name='테스트법인1', business_number='1111111111', representative='대표1')
        company2 = Company(name='테스트법인2', business_number='2222222222', representative='대표2')
        session.add_all([company1, company2])
        session.commit()

        result = self.repo.get_by_name('테스트법인')

        assert len(result) >= 2

    @pytest.mark.unit
    def test_get_active_companies(self, session):
        """활성화된 법인 목록 조회"""
        company1 = Company(name='활성법인', business_number='1111111111', representative='대표1', is_active=True)
        company2 = Company(name='비활성법인', business_number='2222222222', representative='대표2', is_active=False)
        session.add_all([company1, company2])
        session.commit()

        result = self.repo.get_active_companies()

        assert all(c['is_active'] is True for c in result)
        assert any(c['name'] == '활성법인' for c in result)

    @pytest.mark.unit
    def test_verify_company(self, session):
        """법인 인증 처리"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동',
            is_verified=False
        )
        session.add(company)
        session.commit()

        result = self.repo.verify_company(company.id)

        assert result is not None
        assert result['is_verified'] is True

    @pytest.mark.unit
    def test_create_with_organization(self, session):
        """조직과 함께 법인 생성"""
        data = {
            'name': '테스트법인',
            'business_number': '1234567890',
            'representative': '홍길동'
        }
        organization_data = {
            'name': '테스트조직',
            'code': 'ORG001'
        }
        result = self.repo.create_with_organization(data, organization_data=organization_data)

        assert result is not None
        assert result['name'] == '테스트법인'
        assert result.get('root_organization_id') is not None

    @pytest.mark.unit
    def test_update_plan(self, session):
        """법인 플랜 변경"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동',
            plan_type='basic'
        )
        session.add(company)
        session.commit()

        result = self.repo.update_plan(company.id, 'premium', max_employees=100)

        assert result is not None
        assert result['plan_type'] == 'premium'
        assert result.get('max_employees') == 100

    @pytest.mark.unit
    def test_update_plan_invalid_type(self, session):
        """유효하지 않은 플랜 타입"""
        company = Company(
            name='테스트법인',
            business_number='1234567890',
            representative='홍길동'
        )
        session.add(company)
        session.commit()

        with pytest.raises(ValueError):
            self.repo.update_plan(company.id, 'invalid_plan')

    @pytest.mark.unit
    def test_update_plan_not_found(self, session):
        """존재하지 않는 법인 플랜 변경"""
        result = self.repo.update_plan(999, 'premium')

        assert result is None

    @pytest.mark.unit
    def test_verify_company_not_found(self, session):
        """존재하지 않는 법인 인증"""
        result = self.repo.verify_company(999)

        assert result is None

    @pytest.mark.unit
    def test_get_verified_companies(self, session):
        """인증된 법인 목록 조회"""
        company1 = Company(name='인증법인', business_number='1111111111', representative='대표1', is_active=True, is_verified=True)
        company2 = Company(name='미인증법인', business_number='2222222222', representative='대표2', is_active=True, is_verified=False)
        session.add_all([company1, company2])
        session.commit()

        result = self.repo.get_verified_companies()

        assert all(c['is_verified'] is True for c in result)
        assert all(c['is_active'] is True for c in result)

    @pytest.mark.unit
    def test_get_by_plan_type(self, session):
        """플랜 유형별 법인 목록 조회"""
        company1 = Company(name='프리미엄법인', business_number='1111111111', representative='대표1', plan_type='premium', is_active=True)
        company2 = Company(name='베이직법인', business_number='2222222222', representative='대표2', plan_type='basic', is_active=True)
        session.add_all([company1, company2])
        session.commit()

        result = self.repo.get_by_plan_type('premium')

        assert all(c['plan_type'] == 'premium' for c in result)
        assert all(c['is_active'] is True for c in result)

    @pytest.mark.unit
    def test_deactivate(self, session):
        """법인 비활성화"""
        company = Company(name='테스트법인', business_number='1234567890', representative='홍길동', is_active=True)
        session.add(company)
        session.commit()

        result = self.repo.deactivate(company.id)

        assert result is True
        company = self.repo.find_by_id(company.id)
        assert company.is_active is False

    @pytest.mark.unit
    def test_activate(self, session):
        """법인 활성화"""
        company = Company(name='테스트법인', business_number='1234567890', representative='홍길동', is_active=False)
        session.add(company)
        session.commit()

        result = self.repo.activate(company.id)

        assert result is True
        company = self.repo.find_by_id(company.id)
        assert company.is_active is True

    @pytest.mark.unit
    def test_get_with_stats(self, session):
        """통계 정보 포함 법인 조회"""
        company = Company(name='테스트법인', business_number='1234567890', representative='홍길동')
        session.add(company)
        session.commit()

        result = self.repo.get_with_stats(company.id)

        assert result is not None
        assert isinstance(result, dict)

    @pytest.mark.unit
    def test_exists_by_business_number(self, session):
        """사업자등록번호 중복 확인"""
        company = Company(name='테스트법인', business_number='1234567890', representative='홍길동')
        session.add(company)
        session.commit()

        assert self.repo.exists_by_business_number('123-456-7890') is True
        assert self.repo.exists_by_business_number('9999999999') is False

