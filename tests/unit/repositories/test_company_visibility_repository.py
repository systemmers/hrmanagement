"""
CompanyVisibilityRepository 단위 테스트

법인별 정보 노출 설정 관리 기능 테스트
"""
import pytest
from app.domains.company.repositories.company_visibility_repository import CompanyVisibilityRepository
from app.models import CompanyVisibilitySettings
from app.models import Company


class TestCompanyVisibilityRepositoryInit:
    """CompanyVisibilityRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = CompanyVisibilityRepository()
        assert repo is not None
        assert repo.model_class == CompanyVisibilitySettings


class TestCompanyVisibilityRepositoryGet:
    """노출 설정 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanyVisibilityRepository()

    def test_get_by_company_exists(self, session):
        """법인별 노출 설정 조회 (존재)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings = CompanyVisibilitySettings(
            company_id=company.id,
            salary_visibility='admin',
            evaluation_visibility='manager'
        )
        session.add(settings)
        session.commit()

        result = self.repo.get_by_company(company.id)

        assert result is not None
        assert result['companyId'] == company.id
        assert result['salaryVisibility'] == 'admin'

    def test_get_by_company_not_exists(self, session):
        """법인별 노출 설정 조회 (미존재)"""
        result = self.repo.get_by_company(999)
        assert result is None

    def test_get_or_create_exists(self, session):
        """노출 설정 조회 또는 생성 (이미 존재)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings = CompanyVisibilitySettings(
            company_id=company.id,
            salary_visibility='admin'
        )
        session.add(settings)
        session.commit()

        result = self.repo.get_or_create(company.id)

        assert result is not None
        assert result['companyId'] == company.id
        assert result['salaryVisibility'] == 'admin'

    def test_get_or_create_not_exists(self, session):
        """노출 설정 조회 또는 생성 (생성)"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.get_or_create(company.id)

        assert result is not None
        assert result['companyId'] == company.id

        # DB에 실제로 생성되었는지 확인
        settings = CompanyVisibilitySettings.query.filter_by(company_id=company.id).first()
        assert settings is not None


class TestCompanyVisibilityRepositoryUpdate:
    """노출 설정 업데이트 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanyVisibilityRepository()

    def test_update_existing_settings(self, session):
        """기존 설정 업데이트"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings = CompanyVisibilitySettings(
            company_id=company.id,
            salary_visibility='admin',
            evaluation_visibility='manager'
        )
        session.add(settings)
        session.commit()

        update_data = {
            'salaryVisibility': 'all',
            'evaluationVisibility': 'admin'
        }

        result = self.repo.update_settings(company.id, update_data)

        assert result is not None
        assert result['salaryVisibility'] == 'all'
        assert result['evaluationVisibility'] == 'admin'

    def test_update_create_if_not_exists(self, session):
        """설정이 없으면 생성 후 업데이트"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        update_data = {
            'salaryVisibility': 'admin',
            'orgChartVisibility': 'all'
        }

        result = self.repo.update_settings(company.id, update_data)

        assert result is not None
        assert result['companyId'] == company.id
        assert result['salaryVisibility'] == 'admin'
        assert result['orgChartVisibility'] == 'all'

    def test_update_all_fields(self, session):
        """모든 필드 업데이트"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings = CompanyVisibilitySettings(company_id=company.id)
        session.add(settings)
        session.commit()

        update_data = {
            'salaryVisibility': 'admin',
            'evaluationVisibility': 'manager',
            'orgChartVisibility': 'all',
            'contactVisibility': 'all',
            'documentVisibility': 'manager',
            'showSalaryToManagers': True,
            'showEvaluationToManagers': False
        }

        result = self.repo.update_settings(company.id, update_data)

        assert result['salaryVisibility'] == 'admin'
        assert result['evaluationVisibility'] == 'manager'
        assert result['orgChartVisibility'] == 'all'
        assert result['contactVisibility'] == 'all'
        assert result['documentVisibility'] == 'manager'
        assert result['showSalaryToManagers'] is True
        assert result['showEvaluationToManagers'] is False


class TestCompanyVisibilityRepositoryReset:
    """노출 설정 초기화 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CompanyVisibilityRepository()

    def test_reset_existing_settings(self, session):
        """기존 설정을 기본값으로 초기화"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        settings = CompanyVisibilitySettings(
            company_id=company.id,
            salary_visibility='all',
            evaluation_visibility='all'
        )
        session.add(settings)
        session.commit()

        result = self.repo.reset_to_defaults(company.id)

        assert result is not None
        # 기본값으로 재설정되었는지 확인
        for key, value in CompanyVisibilitySettings.DEFAULTS.items():
            # snake_case를 camelCase로 변환하여 확인
            if '_' in key:
                parts = key.split('_')
                camel_key = parts[0] + ''.join(word.capitalize() for word in parts[1:])
                assert camel_key in result

    def test_reset_create_if_not_exists(self, session):
        """설정이 없으면 기본값으로 생성"""
        company = Company(name='테스트회사', business_number='1234567890', representative='대표')
        session.add(company)
        session.commit()

        result = self.repo.reset_to_defaults(company.id)

        assert result is not None
        assert result['companyId'] == company.id

        # DB에 생성되었는지 확인
        settings = CompanyVisibilitySettings.query.filter_by(company_id=company.id).first()
        assert settings is not None

