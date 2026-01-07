"""
모듈 Import 테스트

모든 주요 모듈이 import 가능한지 확인하는 테스트
커버리지 향상을 위한 기본 import 테스트
"""
import pytest


class TestServiceImports:
    """서비스 모듈 import 테스트"""

    def test_import_file_storage_service(self):
        """FileStorageService import"""
        from app.services.file_storage_service import FileStorageService
        assert FileStorageService is not None

    def test_import_termination_service(self):
        """TerminationService import"""
        from app.domains.sync.services.termination_service import TerminationService
        assert TerminationService is not None

    def test_import_user_employee_link_service(self):
        """UserEmployeeLinkService import"""
        from app.domains.user.services.user_employee_link_service import UserEmployeeLinkService
        assert UserEmployeeLinkService is not None

    def test_import_contract_filter_service(self):
        """ContractFilterService import"""
        from app.domains.contract.services.contract_filter_service import ContractFilterService
        assert ContractFilterService is not None

    def test_import_corporate_admin_profile_service(self):
        """CorporateAdminProfileService import"""
        from app.domains.user.services.corporate_admin_profile_service import CorporateAdminProfileService
        assert CorporateAdminProfileService is not None

    def test_import_system_setting_service(self):
        """SystemSettingService import"""
        from app.domains.platform.services.system_setting_service import SystemSettingService
        assert SystemSettingService is not None


class TestUtilsImports:
    """유틸리티 모듈 import 테스트"""

    def test_import_contract_helpers(self):
        """contract_helpers import"""
        import app.shared.utils.contract_helpers as helpers
        assert helpers is not None

    def test_import_corporate_helpers(self):
        """corporate_helpers import"""
        import app.shared.utils.corporate_helpers as helpers
        assert helpers is not None

    def test_import_context_processors(self):
        """context_processors import"""
        import app.shared.utils.context_processors as processors
        assert processors is not None

    def test_import_template_helpers(self):
        """template_helpers import"""
        import app.shared.utils.template_helpers as helpers
        assert helpers is not None

class TestRepositoryImports:
    """리포지토리 모듈 import 테스트"""

    def test_import_company_document_repository(self):
        """CompanyDocumentRepository import"""
        from app.repositories.company_document_repository import CompanyDocumentRepository
        assert CompanyDocumentRepository is not None

    def test_import_classification_repository(self):
        """ClassificationOptionsRepository import"""
        from app.domains.company.repositories.classification_repository import ClassificationOptionsRepository
        assert ClassificationOptionsRepository is not None

    def test_import_corporate_admin_profile_repository(self):
        """CorporateAdminProfileRepository import"""
        from app.domains.user.repositories.corporate_admin_profile_repository import CorporateAdminProfileRepository
        assert CorporateAdminProfileRepository is not None


class TestConstants:
    """상수 테스트"""

    def test_file_storage_constants(self):
        """파일 저장 상수"""
        from app.services.file_storage_service import (
            ALLOWED_EXTENSIONS,
            ALLOWED_IMAGE_EXTENSIONS,
            MAX_FILE_SIZE,
            MAX_IMAGE_SIZE,
            CATEGORY_ATTACHMENT,
            CATEGORY_PROFILE_PHOTO
        )
        assert ALLOWED_EXTENSIONS is not None
        assert ALLOWED_IMAGE_EXTENSIONS is not None
        assert MAX_FILE_SIZE > 0
        assert MAX_IMAGE_SIZE > 0
        assert CATEGORY_ATTACHMENT is not None
        assert CATEGORY_PROFILE_PHOTO is not None

    def test_session_keys_constants(self):
        """세션 키 상수"""
        from app.shared.constants.session_keys import SessionKeys
        assert hasattr(SessionKeys, 'USER_ID')
        assert hasattr(SessionKeys, 'COMPANY_ID')

    def test_account_type_constants(self):
        """계정 타입 상수"""
        from app.shared.constants.session_keys import AccountType
        assert hasattr(AccountType, 'CORPORATE')
        assert hasattr(AccountType, 'PERSONAL')


class TestModelImports:
    """모델 import 테스트"""

    def test_import_company_document(self):
        """CompanyDocument 모델 import"""
        from app.models import CompanyDocument
        assert CompanyDocument is not None

    def test_import_company_visibility_settings(self):
        """CompanyVisibilitySettings 모델 import"""
        from app.models import CompanyVisibilitySettings
        assert CompanyVisibilitySettings is not None

    def test_import_company_settings(self):
        """CompanySettings 모델 import"""
        from app.models import CompanySettings
        assert CompanySettings is not None

    def test_import_number_category(self):
        """NumberCategory 모델 import"""
        from app.models import NumberCategory
        assert NumberCategory is not None

    def test_import_system_setting(self):
        """SystemSetting 모델 import"""
        from app.models import SystemSetting
        assert SystemSetting is not None

    def test_import_attachment(self):
        """Attachment 모델 import"""
        from app.domains.employee.models import Attachment
        assert Attachment is not None


class TestBaseClassImports:
    """Base 클래스 import 테스트"""

    def test_import_base_repository(self):
        """BaseRepository import"""
        from app.repositories.base_repository import BaseRepository
        assert BaseRepository is not None

    def test_import_base_relation_repository(self):
        """BaseRelationRepository import"""
        from app.repositories.base_repository import BaseRelationRepository
        assert BaseRelationRepository is not None


class TestExceptionImports:
    """예외 클래스 import 테스트"""

    def test_import_hrm_exceptions(self):
        """HRM 예외 클래스 import"""
        from app.shared.utils.exceptions import (
            HRMException,
            ValidationError,
            NotFoundError,
            PermissionDeniedError
        )
        assert HRMException is not None
        assert ValidationError is not None
        assert NotFoundError is not None
        assert PermissionDeniedError is not None


class TestFormImports:
    """Form 클래스 import 테스트"""

    def test_import_forms_module(self):
        """forms 모듈 import"""
        try:
            import app.forms as forms
            assert forms is not None
        except ImportError:
            pytest.skip("forms module not available")


class TestHelperFunctions:
    """헬퍼 함수 테스트"""

    def test_safe_get_function(self):
        """safe_get 함수"""
        from app.shared.utils.object_helpers import safe_get
        result = safe_get({'key': 'value'}, 'key')
        assert result == 'value'

    def test_safe_get_nested_function(self):
        """safe_get_nested 함수"""
        from app.shared.utils.object_helpers import safe_get_nested
        data = {'a': {'b': 'value'}}
        result = safe_get_nested(data, 'a', 'b')
        assert result == 'value'

    def test_api_success_function(self):
        """api_success 함수"""
        from app.shared.utils.api_helpers import api_success
        assert api_success is not None

    def test_api_error_function(self):
        """api_error 함수"""
        from app.shared.utils.api_helpers import api_error
        assert api_error is not None

