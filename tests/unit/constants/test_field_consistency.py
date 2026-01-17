"""
필드 일관성 검증 테스트

Phase 0.8: FieldRegistry와 각 컴포넌트 간의 필드 일관성을 검증합니다.

테스트 대상:
1. ProfileAdapter.get_basic_info() 필드가 FieldRegistry에 정의되어 있는지
2. InlineEditService.STATIC_SECTIONS 필드가 FieldRegistry와 일치하는지
3. 모델 필드가 FieldRegistry 필드와 일치하는지
"""
import pytest


class TestFieldRegistryConsistency:
    """FieldRegistry 필드 정의 일관성 테스트"""

    def test_personal_basic_section_exists(self):
        """personal_basic 섹션이 FieldRegistry에 존재하는지 확인"""
        from app.shared.constants.field_registry import FieldRegistry

        section = FieldRegistry.get_section('personal_basic')
        assert section is not None, "personal_basic 섹션이 FieldRegistry에 없습니다"
        assert section.title == '기본 개인정보'

    def test_personal_basic_has_age_field(self):
        """personal_basic 섹션에 age 필드가 정의되어 있는지 확인"""
        from app.shared.constants.field_registry import FieldRegistry

        section = FieldRegistry.get_section('personal_basic')
        age_field = section.get_field('age')

        assert age_field is not None, "age 필드가 personal_basic 섹션에 없습니다"
        assert age_field.readonly is True, "age 필드는 readonly여야 합니다"
        assert age_field.label == '나이'

    def test_personal_basic_has_foreign_name_field(self):
        """personal_basic 섹션에 foreign_name 필드가 정의되어 있는지 확인"""
        from app.shared.constants.field_registry import FieldRegistry

        section = FieldRegistry.get_section('personal_basic')
        foreign_name_field = section.get_field('foreign_name')

        assert foreign_name_field is not None, "foreign_name 필드가 personal_basic 섹션에 없습니다"
        assert foreign_name_field.label == '외국어 이름'

    def test_get_visible_field_names_returns_list(self):
        """get_visible_field_names가 문자열 리스트를 반환하는지 확인"""
        from app.shared.constants.field_registry import FieldRegistry

        field_names = FieldRegistry.get_visible_field_names('personal_basic', 'corporate')

        assert isinstance(field_names, list)
        assert all(isinstance(name, str) for name in field_names)
        assert 'name' in field_names
        assert 'age' in field_names

    def test_get_editable_field_names_excludes_readonly(self):
        """get_editable_field_names가 readonly 필드를 제외하는지 확인"""
        from app.shared.constants.field_registry import FieldRegistry

        editable_fields = FieldRegistry.get_editable_field_names('personal_basic', 'corporate')
        readonly_fields = FieldRegistry.get_readonly_field_names('personal_basic', 'corporate')

        # age, birth_date, gender는 readonly
        assert 'age' not in editable_fields
        assert 'birth_date' not in editable_fields
        assert 'gender' not in editable_fields

        assert 'age' in readonly_fields
        assert 'birth_date' in readonly_fields
        assert 'gender' in readonly_fields


class TestProfileAdapterFieldConsistency:
    """ProfileAdapter 필드 일관성 테스트"""

    def test_employee_adapter_has_age_field(self):
        """EmployeeProfileAdapter.get_basic_info()에 age 필드가 있는지 확인"""
        from unittest.mock import Mock
        from app.shared.adapters.profile_adapter import EmployeeProfileAdapter

        # Mock Employee 객체
        mock_employee = Mock()
        mock_employee.age = 30
        mock_employee.id = 1
        mock_employee.name = 'Test'

        adapter = EmployeeProfileAdapter(mock_employee)
        basic_info = adapter.get_basic_info()

        assert 'age' in basic_info, "EmployeeProfileAdapter.get_basic_info()에 age 필드가 없습니다"
        assert basic_info['age'] == 30

    def test_personal_adapter_has_age_field(self):
        """PersonalProfileAdapter.get_basic_info()에 age 필드가 있는지 확인"""
        from unittest.mock import Mock
        from app.shared.adapters.profile_adapter import PersonalProfileAdapter

        # Mock Profile 객체
        mock_profile = Mock()
        mock_profile.age = 25
        mock_profile.id = 1
        mock_profile.name = 'Test'
        mock_profile.__class__.__name__ = 'Profile'

        adapter = PersonalProfileAdapter(mock_profile)
        basic_info = adapter.get_basic_info()

        assert 'age' in basic_info, "PersonalProfileAdapter.get_basic_info()에 age 필드가 없습니다"
        assert basic_info['age'] == 25

    def test_personal_adapter_has_foreign_name_field(self):
        """PersonalProfileAdapter.get_basic_info()에 foreign_name 필드가 있는지 확인"""
        from unittest.mock import Mock
        from app.shared.adapters.profile_adapter import PersonalProfileAdapter

        # Mock Profile 객체
        mock_profile = Mock()
        mock_profile.foreign_name = 'Foreigner Name'
        mock_profile.id = 1
        mock_profile.name = 'Test'
        mock_profile.__class__.__name__ = 'Profile'

        adapter = PersonalProfileAdapter(mock_profile)
        basic_info = adapter.get_basic_info()

        assert 'foreign_name' in basic_info, "PersonalProfileAdapter.get_basic_info()에 foreign_name 필드가 없습니다"


class TestInlineEditServiceFieldConsistency:
    """InlineEditService 필드 일관성 테스트"""

    def test_static_sections_has_personal(self):
        """STATIC_SECTIONS에 personal 섹션이 있는지 확인"""
        from app.domains.employee.services.inline_edit_service import InlineEditService

        assert 'personal' in InlineEditService.STATIC_SECTIONS
        assert 'fields' in InlineEditService.STATIC_SECTIONS['personal']

    def test_get_section_fields_from_registry(self):
        """FieldRegistry에서 섹션 필드를 가져오는 메서드 테스트"""
        from app.domains.employee.services.inline_edit_service import inline_edit_service

        fields = inline_edit_service.get_section_fields_from_registry('personal', 'corporate')

        assert isinstance(fields, list)
        assert len(fields) > 0
        # 편집 가능한 필드만 포함되어야 함
        assert 'name' in fields
        assert 'english_name' in fields

    def test_get_readonly_fields_from_registry(self):
        """FieldRegistry에서 readonly 필드를 가져오는 메서드 테스트"""
        from app.domains.employee.services.inline_edit_service import inline_edit_service

        readonly_fields = inline_edit_service.get_readonly_fields_from_registry('personal', 'corporate')

        assert isinstance(readonly_fields, list)
        # age, birth_date, gender는 readonly
        assert 'age' in readonly_fields
        assert 'birth_date' in readonly_fields


class TestModelFieldConsistency:
    """Model 필드 일관성 테스트"""

    def test_personal_profile_has_age_property(self):
        """PersonalProfile 모델에 age property가 있는지 확인"""
        from app.domains.user.models.personal.profile import PersonalProfile

        assert hasattr(PersonalProfile, 'age'), "PersonalProfile에 age property가 없습니다"

    def test_personal_profile_has_foreign_name_column(self):
        """PersonalProfile 모델에 foreign_name 컬럼이 있는지 확인"""
        from app.domains.user.models.personal.profile import PersonalProfile

        # 모델 컬럼 확인
        columns = [c.name for c in PersonalProfile.__table__.columns]
        assert 'foreign_name' in columns, "PersonalProfile에 foreign_name 컬럼이 없습니다"

    def test_employee_has_age_property(self):
        """Employee 모델에 age property가 있는지 확인"""
        from app.domains.employee.models.employee import Employee

        assert hasattr(Employee, 'age'), "Employee에 age property가 없습니다"

    def test_employee_has_foreign_name_column(self):
        """Employee 모델에 foreign_name 컬럼이 있는지 확인"""
        from app.domains.employee.models.employee import Employee

        columns = [c.name for c in Employee.__table__.columns]
        assert 'foreign_name' in columns, "Employee에 foreign_name 컬럼이 없습니다"


class TestFieldOptionsConsistency:
    """FieldOptions 일관성 테스트"""

    def test_options_category_map_exists(self):
        """OPTIONS_CATEGORY_MAP이 정의되어 있는지 확인"""
        from app.shared.constants.field_options import FieldOptions

        assert hasattr(FieldOptions, 'OPTIONS_CATEGORY_MAP')
        assert 'gender' in FieldOptions.OPTIONS_CATEGORY_MAP
        assert 'marital_status' in FieldOptions.OPTIONS_CATEGORY_MAP

    def test_get_by_category_returns_options(self):
        """get_by_category가 옵션 리스트를 반환하는지 확인"""
        from app.shared.constants.field_options import FieldOptions

        gender_options = FieldOptions.get_by_category('gender')
        assert len(gender_options) > 0
        assert gender_options[0].value == '남'

    def test_get_by_category_returns_empty_for_db_options(self):
        """DB 동적 옵션은 빈 리스트를 반환하는지 확인"""
        from app.shared.constants.field_options import FieldOptions

        # bank는 DB에서 동적으로 로드되므로 FieldOptions에 없음
        bank_options = FieldOptions.get_by_category('bank')
        assert bank_options == []

    def test_has_category_returns_correct_value(self):
        """has_category가 올바른 값을 반환하는지 확인"""
        from app.shared.constants.field_options import FieldOptions

        assert FieldOptions.has_category('gender') is True
        assert FieldOptions.has_category('bank') is False
        assert FieldOptions.has_category('position') is False

    def test_work_type_options_exist(self):
        """WORK_TYPE 옵션이 정의되어 있는지 확인 (Phase 0.8)"""
        from app.shared.constants.field_options import FieldOptions

        assert hasattr(FieldOptions, 'WORK_TYPE')
        assert len(FieldOptions.WORK_TYPE) > 0

    def test_school_type_options_exist(self):
        """SCHOOL_TYPE 옵션이 정의되어 있는지 확인 (Phase 0.8)"""
        from app.shared.constants.field_options import FieldOptions

        assert hasattr(FieldOptions, 'SCHOOL_TYPE')
        assert len(FieldOptions.SCHOOL_TYPE) > 0


class TestCrossComponentConsistency:
    """컴포넌트 간 필드 일관성 테스트"""

    def test_basic_info_fields_match_across_adapters(self):
        """EmployeeProfileAdapter와 PersonalProfileAdapter의 get_basic_info() 필드가 일치하는지 확인"""
        from unittest.mock import Mock
        from app.shared.adapters.profile_adapter import EmployeeProfileAdapter, PersonalProfileAdapter

        # Mock 객체
        mock_employee = Mock()
        mock_profile = Mock()
        mock_profile.__class__.__name__ = 'Profile'

        employee_adapter = EmployeeProfileAdapter(mock_employee)
        personal_adapter = PersonalProfileAdapter(mock_profile)

        # 공통 필드 정의 (둘 다 있어야 하는 필드)
        common_fields = [
            'id', 'name', 'english_name', 'foreign_name',
            'birth_date', 'age', 'gender', 'mobile_phone', 'email',
            'address', 'detailed_address', 'nationality',
            'marital_status', 'hobby', 'specialty', 'disability_info',
            'emergency_contact', 'emergency_relation',
            'military_status', 'note'
        ]

        employee_info = employee_adapter.get_basic_info()
        personal_info = personal_adapter.get_basic_info()

        missing_in_employee = []
        missing_in_personal = []

        for field in common_fields:
            if field not in employee_info:
                missing_in_employee.append(field)
            if field not in personal_info:
                missing_in_personal.append(field)

        assert not missing_in_employee, f"EmployeeProfileAdapter에 누락된 필드: {missing_in_employee}"
        assert not missing_in_personal, f"PersonalProfileAdapter에 누락된 필드: {missing_in_personal}"
