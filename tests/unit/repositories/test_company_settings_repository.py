"""
CompanySettingsRepository 단위 테스트

법인별 설정 정보 관리 기능 테스트
"""
import pytest
from app.domains.company.repositories.company_settings_repository import CompanySettingsRepository
from app.domains.company.models import CompanySettings
from app.domains.company.models import Company


class TestCompanySettingsRepositoryInit:
    """CompanySettingsRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = CompanySettingsRepository()
        assert repo is not None
        assert repo.model_class == CompanySettings


class TestCompanySettingsRepositoryGet:
    """설정 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanySettingsRepository()

    def test_get_by_company(self, session):
        """법인별 모든 설정 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting1 = CompanySettings(
            company_id=company.id,
            key='test.key1',
            value='value1',
            value_type='string'
        )
        setting2 = CompanySettings(
            company_id=company.id,
            key='test.key2',
            value='100',
            value_type='integer'
        )
        session.add_all([setting1, setting2])
        session.commit()

        result = self.repo.get_by_company(company.id)

        assert len(result) >= 2
        assert 'test.key1' in result
        assert result['test.key1'] == 'value1'

    def test_get_by_company_and_category(self, session):
        """법인별 카테고리 설정 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting1 = CompanySettings(
            company_id=company.id,
            key='email.domain',
            value='example.com',
            value_type='string',
            category='email'
        )
        setting2 = CompanySettings(
            company_id=company.id,
            key='payroll.day',
            value='25',
            value_type='integer',
            category='payroll'
        )
        session.add_all([setting1, setting2])
        session.commit()

        result = self.repo.get_by_company_and_category(company.id, 'email')

        assert len(result) == 1
        assert 'email.domain' in result

    def test_get_setting_exists(self, session):
        """단일 설정값 조회 (존재)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting = CompanySettings(
            company_id=company.id,
            key='test.key',
            value='test_value',
            value_type='string'
        )
        session.add(setting)
        session.commit()

        result = self.repo.get_setting(company.id, 'test.key')
        assert result == 'test_value'

    def test_get_setting_not_exists(self, session):
        """단일 설정값 조회 (미존재, 기본값 반환)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_setting(company.id, 'nonexistent.key')
        # 기본값이 없으면 None
        assert result is None


class TestCompanySettingsRepositorySet:
    """설정 저장 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanySettingsRepository()

    def test_set_setting_new(self, session):
        """새 설정 저장"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.set_setting(
            company.id,
            'test.new_key',
            'new_value',
            value_type='string',
            category='test'
        )

        assert result is not None
        assert result['key'] == 'test.new_key'
        assert result['value'] == 'new_value'

    def test_set_setting_update(self, session):
        """기존 설정 업데이트"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting = CompanySettings(
            company_id=company.id,
            key='test.key',
            value='old_value',
            value_type='string'
        )
        session.add(setting)
        session.commit()

        result = self.repo.set_setting(company.id, 'test.key', 'new_value')

        assert result['value'] == 'new_value'

    def test_set_bulk_settings(self, session):
        """여러 설정값 일괄 저장"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings_dict = {
            'test.key1': 'value1',
            'test.key2': 'value2',
            'test.key3': 'value3'
        }

        results = self.repo.set_bulk_settings(company.id, settings_dict, category='test')

        assert len(results) == 3
        assert all(r['category'] == 'test' for r in results)


class TestCompanySettingsRepositoryDelete:
    """설정 삭제 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanySettingsRepository()

    def test_delete_setting_exists(self, session):
        """기존 설정 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting = CompanySettings(
            company_id=company.id,
            key='test.key',
            value='value',
            value_type='string'
        )
        session.add(setting)
        session.commit()

        result = self.repo.delete_setting(company.id, 'test.key')
        assert result is True

        # 실제로 삭제되었는지 확인
        deleted = CompanySettings.query.filter_by(
            company_id=company.id,
            key='test.key'
        ).first()
        assert deleted is None

    def test_delete_setting_not_exists(self, session):
        """존재하지 않는 설정 삭제"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.delete_setting(company.id, 'nonexistent.key')
        assert result is False


class TestCompanySettingsRepositorySpecific:
    """특정 설정 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanySettingsRepository()

    def test_get_all_settings_full(self, session):
        """모든 설정 전체 정보 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        setting1 = CompanySettings(
            company_id=company.id,
            key='test.key1',
            value='value1',
            value_type='string'
        )
        setting2 = CompanySettings(
            company_id=company.id,
            key='test.key2',
            value='value2',
            value_type='string'
        )
        session.add_all([setting1, setting2])
        session.commit()

        result = self.repo.get_all_settings_full(company.id)

        assert len(result) >= 2
        assert all('key' in s and 'value' in s for s in result)

    def test_get_employee_number_settings(self, session):
        """사번 설정 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_employee_number_settings(company.id)

        assert 'companyCode' in result
        assert 'separator' in result
        assert 'digits' in result

    def test_get_email_settings(self, session):
        """이메일 설정 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_email_settings(company.id)

        assert 'domain' in result
        assert 'autoGenerate' in result
        assert 'format' in result

    def test_get_payroll_settings(self, session):
        """급여 설정 조회"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_payroll_settings(company.id)

        assert 'paymentDay' in result
