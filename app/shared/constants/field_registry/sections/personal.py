"""
Personal Section Definitions

개인 프로필 관련 섹션 정의 (기본정보, 연락처, 주소 등)

Phase 29 (2026-01-05): aliases 시스템 제거 - snake_case 직접 사용
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
# Phase 28: 필드 순서 재배치, 필수화, 신규 필드 추가
# =============================================================================
PERSONAL_BASIC_FIELDS = [
    # Phase 28: 라벨 통일 (Edit 폼 기준 SSOT)
    create_field(
        name='name',
        label='이름',  # Phase 28: 성명 → 이름
        order=10,
        field_type=FieldType.TEXT,
        required=True,
        max_length=100,
    ),
    create_field(
        name='english_name',
        label='영문 이름',  # Phase 28: 영문명 → 영문 이름
        order=20,
        field_type=FieldType.TEXT,
        required=True,  # Phase 28: 필수화
        max_length=100,
    ),
    create_field(
        name='chinese_name',
        label='한자 이름',  # Phase 28: 한자명 → 한자 이름
        order=30,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='foreign_name',
        label='외국어 이름',  # Phase 28: 외국어명 → 외국어 이름
        order=35,
        field_type=FieldType.TEXT,
        max_length=100,
        help_text='영문 외 추가 외국어 이름',
    ),
    create_field(
        name='resident_number',
        label='주민등록번호',
        order=40,
        field_type=FieldType.TEXT,
        required=True,  # Phase 28: 필수화
        max_length=20,
        help_text='입력 시 생년월일/나이/성별 자동 입력',
    ),
    create_field(
        name='birth_date',
        label='생년월일',
        order=50,
        field_type=FieldType.DATE,
        readonly=True,  # Phase 28: RRN 자동입력
        help_text='주민등록번호 입력 시 자동 입력됩니다.',
    ),
    create_field(
        name='age',
        label='나이',
        order=55,
        field_type=FieldType.NUMBER,
        readonly=True,  # Phase 28: 자동계산 (만 나이)
        help_text='주민등록번호 입력 시 자동 계산됩니다.',
    ),
    create_field(
        name='gender',
        label='성별',
        order=60,
        field_type=FieldType.SELECT,
        options_category='gender',
        readonly=True,  # Phase 28: RRN 자동입력
        help_text='주민등록번호 입력 시 자동 입력됩니다.',
    ),
    create_field(
        name='lunar_birth',
        label='음력 여부',
        order=65,
        field_type=FieldType.CHECKBOX,
    ),
    create_field(
        name='marital_status',
        label='결혼여부',  # Phase 28: 결혼 여부 → 결혼여부 (공백 제거)
        order=70,
        field_type=FieldType.SELECT,
        options_category='marital_status',
    ),
    create_field(
        name='nationality',
        label='국적',
        order=80,
        field_type=FieldType.SELECT,
        options_category='nationality',
        help_text='기본값: 대한민국',  # Phase 28: 기본값은 서비스에서 처리
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
# Phase 28: 필수 필드 설정
# =============================================================================
CONTACT_FIELDS = [
    create_field(
        name='mobile_phone',
        label='휴대전화',
        order=10,
        field_type=FieldType.TEL,
        required=True,  # Phase 28: 필수화
        max_length=50,
    ),
    create_field(
        name='home_phone',
        label='자택전화',
        order=20,
        field_type=FieldType.TEL,
        max_length=50,
    ),
    create_field(
        name='email',
        label='이메일',
        order=30,
        field_type=FieldType.EMAIL,
        required=True,  # Phase 28: 필수화
        max_length=200,
    ),
    create_field(
        name='emergency_contact',
        label='비상연락처',
        order=40,
        field_type=FieldType.TEL,
        max_length=50,
    ),
    create_field(
        name='emergency_relation',
        label='비상연락처 관계',
        order=50,
        field_type=FieldType.TEXT,
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
# Phase 28: 주소 필수화
# =============================================================================
ADDRESS_FIELDS = [
    create_field(
        name='postal_code',
        label='우편번호',
        order=10,
        field_type=FieldType.TEXT,
        max_length=20,
    ),
    create_field(
        name='address',
        label='주소',
        order=20,
        field_type=FieldType.TEXT,
        required=True,  # Phase 28: 필수화
        max_length=500,
    ),
    create_field(
        name='detailed_address',
        label='상세주소',
        order=30,
        field_type=FieldType.TEXT,
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
# Phase 28: 실제거주주소 필수화
# =============================================================================
ACTUAL_ADDRESS_FIELDS = [
    create_field(
        name='actual_postal_code',
        label='우편번호',
        order=10,
        field_type=FieldType.TEXT,
        max_length=20,
    ),
    create_field(
        name='actual_address',
        label='주소',
        order=20,
        field_type=FieldType.TEXT,
        required=True,  # Phase 28: 필수화
        max_length=500,
    ),
    create_field(
        name='actual_detailed_address',
        label='상세주소',
        order=30,
        field_type=FieldType.TEXT,
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
# Phase 28: blood_type, religion 삭제 / marital_status는 personal_basic으로 이동
#           disability_info 필드 타입 TEXT로 변경
# =============================================================================
PERSONAL_EXTENDED_FIELDS = [
    create_field(
        name='hobby',
        label='취미',
        order=10,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='specialty',
        label='특기',
        order=20,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='disability_info',
        label='장애정보',  # Phase 28: 장애 정보 → 장애정보 (공백 제거)
        order=30,
        field_type=FieldType.TEXT,  # Phase 28: TEXTAREA -> TEXT 변경
        max_length=200,
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
# 계좌 정보 섹션 (bank_info)
# Phase 28: 급여정보 섹션에서 기본정보로 이동
# =============================================================================
BANK_INFO_FIELDS = [
    create_field(
        name='bank_name',
        label='은행명',
        order=10,
        field_type=FieldType.SELECT,
        options_category='bank',
    ),
    create_field(
        name='account_number',
        label='계좌번호',
        order=20,
        field_type=FieldType.TEXT,
        max_length=50,
    ),
    create_field(
        name='account_holder',
        label='예금주',
        order=30,
        field_type=FieldType.TEXT,
        max_length=50,
    ),
]

bank_info_section = create_section(
    id='bank_info',
    title='계좌 정보',
    icon='bi bi-bank',
    fields=BANK_INFO_FIELDS,
    order=55,
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
        options_category='military_status',
    ),
    create_field(
        name='service_type',
        label='복무 형태',
        order=20,
        field_type=FieldType.SELECT,
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
    ),
    create_field(
        name='service_end',
        label='복무 종료일',
        order=60,
        field_type=FieldType.DATE,
    ),
    create_field(
        name='exemption_reason',
        label='면제 사유',
        order=70,
        field_type=FieldType.TEXT,
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
FieldRegistry.register_section(bank_info_section, domain='profile')  # Phase 28
FieldRegistry.register_section(personal_extended_section, domain='profile')
FieldRegistry.register_section(military_section, domain='profile')
