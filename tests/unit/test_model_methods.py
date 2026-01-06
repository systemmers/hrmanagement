"""
모델 메서드 기본 테스트

주요 모델들의 기본 메서드 테스트
"""
import pytest
from datetime import datetime


class TestCompanyVisibilitySettingsModel:
    """CompanyVisibilitySettings 모델 테스트"""

    def test_model_defaults(self, session):
        """기본값 테스트"""
        from app.models.company_visibility_settings import CompanyVisibilitySettings
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        settings = CompanyVisibilitySettings(company_id=company.id)
        session.add(settings)
        session.commit()
        
        assert settings.id is not None

    def test_model_to_dict(self, session):
        """to_dict 메서드 테스트"""
        from app.models.company_visibility_settings import CompanyVisibilitySettings
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        settings = CompanyVisibilitySettings(
            company_id=company.id,
            salary_visibility='admin'
        )
        session.add(settings)
        session.commit()
        
        result = settings.to_dict()
        assert 'companyId' in result
        assert 'salaryVisibility' in result


class TestCompanySettingsModel:
    """CompanySettings 모델 테스트"""

    def test_model_creation(self, session):
        """모델 생성 테스트"""
        from app.models.company_settings import CompanySettings
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
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
        
        assert setting.id is not None

    def test_get_typed_value(self, session):
        """타입 변환 값 조회"""
        from app.models.company_settings import CompanySettings
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        setting = CompanySettings(
            company_id=company.id,
            key='test.int',
            value='42',
            value_type='integer'
        )
        session.add(setting)
        session.commit()
        
        result = setting.get_typed_value()
        assert result == 42
        assert isinstance(result, int)

    def test_set_typed_value(self, session):
        """타입 변환 값 설정"""
        from app.models.company_settings import CompanySettings
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        setting = CompanySettings(
            company_id=company.id,
            key='test.bool',
            value_type='boolean'
        )
        setting.set_typed_value(True)
        session.add(setting)
        session.commit()
        
        assert setting.value in ('True', 'true')  # JSON 직렬화에 따라 다를 수 있음
        assert setting.get_typed_value() is True


class TestSystemSettingModel:
    """SystemSetting 모델 테스트"""

    def test_model_creation(self, session):
        """모델 생성"""
        from app.models.system_setting import SystemSetting
        
        setting = SystemSetting(
            key='system.test',
            value='test',
            value_type='string'
        )
        session.add(setting)
        session.commit()
        
        assert setting.id is not None

    def test_to_dict(self, session):
        """to_dict 메서드"""
        from app.models.system_setting import SystemSetting
        
        setting = SystemSetting(
            key='system.test',
            value='test',
            value_type='string'
        )
        session.add(setting)
        session.commit()
        
        result = setting.to_dict()
        assert 'key' in result
        assert 'value' in result


class TestNumberCategoryModel:
    """NumberCategory 모델 테스트"""

    def test_model_creation(self, session):
        """모델 생성"""
        from app.models.number_category import NumberCategory
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        category = NumberCategory(
            company_id=company.id,
            type='employee',
            code='EMP',
            name='직원'
        )
        session.add(category)
        session.commit()
        
        assert category.id is not None

    def test_peek_next_sequence(self, session):
        """다음 시퀀스 미리보기"""
        from app.models.number_category import NumberCategory
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        category = NumberCategory(
            company_id=company.id,
            type='employee',
            code='EMP',
            name='직원',
            current_sequence=10
        )
        session.add(category)
        session.commit()
        
        next_seq = category.peek_next_sequence()
        assert next_seq == 11


class TestAttachmentModel:
    """Attachment 모델 테스트"""

    def test_model_creation(self, session):
        """모델 생성"""
        from app.domains.employee.models import Attachment
        from app.domains.employee.models import Employee
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        employee = Employee(name='직원', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()
        
        attachment = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume.pdf',
            file_path='/uploads/resume.pdf',
            upload_date=datetime.now()
        )
        session.add(attachment)
        session.commit()
        
        assert attachment.id is not None

    def test_to_dict(self, session):
        """to_dict 메서드"""
        from app.domains.employee.models import Attachment
        from app.domains.employee.models import Employee
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        employee = Employee(name='직원', employee_number='EMP001', company_id=company.id)
        session.add(employee)
        session.commit()
        
        attachment = Attachment(
            employee_id=employee.id,
            category='resume',
            file_name='resume.pdf',
            file_path='/uploads/resume.pdf',
            upload_date=datetime.now()
        )
        session.add(attachment)
        session.commit()
        
        result = attachment.to_dict()
        assert 'file_name' in result
        assert 'category' in result


class TestCompanyDocumentModel:
    """CompanyDocument 모델 테스트"""

    def test_model_creation(self, session):
        """모델 생성"""
        from app.models.company_document import CompanyDocument
        from app.models.company import Company
        
        company = Company(name='테스트', business_number='123', representative='대표')
        session.add(company)
        session.commit()
        
        doc = CompanyDocument(
            company_id=company.id,
            category='license',
            document_type='사업자등록증',
            title='사업자등록증',  # title은 NOT NULL 필드
            file_name='license.pdf',
            file_path='/docs/license.pdf',
            uploaded_at=datetime.now()
        )
        session.add(doc)
        session.commit()
        
        assert doc.id is not None


class TestModelConstants:
    """모델 상수 테스트"""

    def test_company_settings_constants(self):
        """CompanySettings 상수"""
        from app.models.company_settings import CompanySettings
        
        assert hasattr(CompanySettings, 'TYPE_STRING')
        assert hasattr(CompanySettings, 'TYPE_INTEGER')
        assert hasattr(CompanySettings, 'TYPE_BOOLEAN')

    def test_number_category_constants(self):
        """NumberCategory 상수"""
        from app.models.number_category import NumberCategory
        
        assert hasattr(NumberCategory, 'TYPE_EMPLOYEE')
        assert hasattr(NumberCategory, 'TYPE_ASSET')

    def test_company_visibility_defaults(self):
        """CompanyVisibilitySettings 기본값"""
        from app.models.company_visibility_settings import CompanyVisibilitySettings
        
        assert hasattr(CompanyVisibilitySettings, 'DEFAULTS')
        assert CompanyVisibilitySettings.DEFAULTS is not None

