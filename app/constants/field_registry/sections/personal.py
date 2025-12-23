"""
Personal Section Definitions

개인 프로필 관련 섹션 정의 (기본정보, 연락처, 주소 등)
"""
from ..base import (
    FieldDefinition,
    SectionDefinition,
    FieldType,
    Visibility,
    create_field,
    create_section,
)
from .. import FieldRegistry


# =============================================================================
# 기본 개인정보 섹션 (personal_basic)
# =============================================================================
PERSONAL_BASIC_FIELDS = [
    create_field(
        name='name',
        label='성명',
        order=10,
        field_type=FieldType.TEXT,
        required=True,
        max_length=100,
    ),
    create_field(
        name='english_name',
        label='영문명',
        order=20,
        field_type=FieldType.TEXT,
        aliases=['name_en', 'englishName'],
        max_length=100,
    ),
    create_field(
        name='chinese_name',
        label='한자명',
        order=30,
        field_type=FieldType.TEXT,
        aliases=['chineseName'],
        max_length=100,
    ),
    create_field(
        name='birth_date',
        label='생년월일',
        order=40,
        field_type=FieldType.DATE,
        aliases=['birthDate'],
    ),
    create_field(
        name='lunar_birth',
        label='음력 여부',
        order=50,
        field_type=FieldType.CHECKBOX,
        aliases=['lunarBirth'],
    ),
    create_field(
        name='gender',
        label='성별',
        order=60,
        field_type=FieldType.SELECT,
        options_category='gender',  # ClassificationOption 참조
    ),
    create_field(
        name='nationality',
        label='국적',
        order=70,
        field_type=FieldType.SELECT,
        options_category='nationality',
    ),
    create_field(
        name='resident_number',
        label='주민등록번호',
        order=80,
        field_type=FieldType.TEXT,
        aliases=['rrn', 'residentNumber'],
        max_length=20,
        help_text='개인정보 보호를 위해 암호화 저장됩니다.',
    ),
]

personal_basic_section = create_section(
    id='personal_basic',
    title='기본 개인정보',
    icon='bi bi-person',
    fields=PERSONAL_BASIC_FIELDS,
    order=10,
)


# =============================================================================
# 연락처 정보 섹션 (contact)
# =============================================================================
CONTACT_FIELDS = [
    create_field(
        name='mobile_phone',
        label='휴대전화',
        order=10,
        field_type=FieldType.TEL,
        aliases=['phone', 'mobilePhone'],
        max_length=50,
    ),
    create_field(
        name='home_phone',
        label='자택전화',
        order=20,
        field_type=FieldType.TEL,
        aliases=['homePhone'],
        max_length=50,
    ),
    create_field(
        name='email',
        label='이메일',
        order=30,
        field_type=FieldType.EMAIL,
        max_length=200,
    ),
    create_field(
        name='emergency_contact',
        label='비상연락처',
        order=40,
        field_type=FieldType.TEL,
        aliases=['emergencyContact'],
        max_length=50,
    ),
    create_field(
        name='emergency_relation',
        label='비상연락처 관계',
        order=50,
        field_type=FieldType.TEXT,
        aliases=['emergencyRelation'],
        max_length=50,
    ),
]

contact_section = create_section(
    id='contact',
    title='연락처 정보',
    icon='bi bi-telephone',
    fields=CONTACT_FIELDS,
    order=20,
)


# =============================================================================
# 주민등록상 주소 섹션 (address)
# =============================================================================
ADDRESS_FIELDS = [
    create_field(
        name='postal_code',
        label='우편번호',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['postalCode'],
        max_length=20,
    ),
    create_field(
        name='address',
        label='주소',
        order=20,
        field_type=FieldType.TEXT,
        max_length=500,
    ),
    create_field(
        name='detailed_address',
        label='상세주소',
        order=30,
        field_type=FieldType.TEXT,
        aliases=['detailedAddress'],
        max_length=500,
    ),
]

address_section = create_section(
    id='address',
    title='주민등록상 주소',
    icon='bi bi-house',
    fields=ADDRESS_FIELDS,
    order=30,
)


# =============================================================================
# 실제 거주 주소 섹션 (actual_address)
# =============================================================================
ACTUAL_ADDRESS_FIELDS = [
    create_field(
        name='actual_postal_code',
        label='우편번호',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['actualPostalCode'],
        max_length=20,
    ),
    create_field(
        name='actual_address',
        label='주소',
        order=20,
        field_type=FieldType.TEXT,
        aliases=['actualAddress'],
        max_length=500,
    ),
    create_field(
        name='actual_detailed_address',
        label='상세주소',
        order=30,
        field_type=FieldType.TEXT,
        aliases=['actualDetailedAddress'],
        max_length=500,
    ),
]

actual_address_section = create_section(
    id='actual_address',
    title='실제 거주 주소',
    icon='bi bi-geo-alt',
    fields=ACTUAL_ADDRESS_FIELDS,
    order=40,
)


# =============================================================================
# 기타 개인정보 섹션 (personal_extended)
# =============================================================================
PERSONAL_EXTENDED_FIELDS = [
    create_field(
        name='blood_type',
        label='혈액형',
        order=10,
        field_type=FieldType.SELECT,
        aliases=['bloodType'],
        options_category='blood_type',
    ),
    create_field(
        name='marital_status',
        label='결혼 여부',
        order=20,
        field_type=FieldType.SELECT,
        aliases=['maritalStatus'],
        options_category='marital_status',
    ),
    create_field(
        name='religion',
        label='종교',
        order=30,
        field_type=FieldType.SELECT,
        options_category='religion',
    ),
    create_field(
        name='hobby',
        label='취미',
        order=40,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='specialty',
        label='특기',
        order=50,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='disability_info',
        label='장애 정보',
        order=60,
        field_type=FieldType.TEXTAREA,
        aliases=['disabilityInfo'],
    ),
]

personal_extended_section = create_section(
    id='personal_extended',
    title='기타 개인정보',
    icon='bi bi-info-circle',
    fields=PERSONAL_EXTENDED_FIELDS,
    order=50,
)


# =============================================================================
# 병역 정보 섹션 (military)
# =============================================================================
MILITARY_FIELDS = [
    create_field(
        name='military_status',
        label='병역구분',
        order=10,
        field_type=FieldType.SELECT,
        aliases=['militaryStatus'],
        options_category='military_status',
    ),
    create_field(
        name='service_type',
        label='복무 형태',
        order=20,
        field_type=FieldType.SELECT,
        aliases=['serviceType'],
        options_category='service_type',
    ),
    create_field(
        name='branch',
        label='군별',
        order=30,
        field_type=FieldType.SELECT,
        options_category='military_branch',
    ),
    create_field(
        name='rank',
        label='계급',
        order=40,
        field_type=FieldType.TEXT,
        max_length=50,
    ),
    create_field(
        name='service_start',
        label='복무 시작일',
        order=50,
        field_type=FieldType.DATE,
        aliases=['serviceStart', 'enlistment_date'],
    ),
    create_field(
        name='service_end',
        label='복무 종료일',
        order=60,
        field_type=FieldType.DATE,
        aliases=['serviceEnd', 'discharge_date'],
    ),
    create_field(
        name='exemption_reason',
        label='면제 사유',
        order=70,
        field_type=FieldType.TEXT,
        aliases=['exemptionReason'],
        max_length=200,
    ),
]

military_section = create_section(
    id='military',
    title='병역사항',
    icon='bi bi-shield',
    fields=MILITARY_FIELDS,
    order=100,
)


# =============================================================================
# 섹션 등록
# =============================================================================
FieldRegistry.register_section(personal_basic_section, domain='profile')
FieldRegistry.register_section(contact_section, domain='profile')
FieldRegistry.register_section(address_section, domain='profile')
FieldRegistry.register_section(actual_address_section, domain='profile')
FieldRegistry.register_section(personal_extended_section, domain='profile')
FieldRegistry.register_section(military_section, domain='profile')
