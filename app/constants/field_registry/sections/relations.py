"""
Relation Section Definitions

동적 이력 관련 섹션 정의 (학력, 경력, 자격증, 언어, 가족, 수상, 프로젝트)
이 섹션들은 is_dynamic=True로 동적 추가/삭제가 가능합니다.
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
# 학력 정보 섹션 (education)
# =============================================================================
EDUCATION_FIELDS = [
    create_field(
        name='school_type',
        label='학교구분',
        order=10,
        field_type=FieldType.SELECT,
        aliases=['schoolType'],
        options_category='school_type',
    ),
    create_field(
        name='school_name',
        label='학교명',
        order=20,
        field_type=FieldType.TEXT,
        aliases=['schoolName'],
        required=True,
        max_length=200,
    ),
    create_field(
        name='major',
        label='전공',
        order=30,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='degree',
        label='학위',
        order=40,
        field_type=FieldType.SELECT,
        options_category='degree',
    ),
    create_field(
        name='graduation_status',
        label='졸업구분',
        order=50,
        field_type=FieldType.SELECT,
        aliases=['graduationStatus'],
        options_category='graduation_status',
    ),
    create_field(
        name='graduation_date',
        label='졸업년도',
        order=60,
        field_type=FieldType.TEXT,
        aliases=['graduationDate', 'graduation_year'],
        max_length=20,
        help_text='YYYY 형식 또는 YYYY-MM 형식',
    ),
]

education_section = create_section(
    id='education',
    title='학력사항',
    icon='bi bi-mortarboard',
    fields=EDUCATION_FIELDS,
    order=110,
    is_dynamic=True,
    max_items=10,
)


# =============================================================================
# 경력 정보 섹션 (career)
# =============================================================================
CAREER_FIELDS = [
    create_field(
        name='company_name',
        label='회사명',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['companyName'],
        required=True,
        max_length=200,
    ),
    create_field(
        name='department',
        label='부서',
        order=20,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='position',
        label='직위',
        order=30,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='start_date',
        label='입사일',
        order=40,
        field_type=FieldType.DATE,
        aliases=['startDate'],
    ),
    create_field(
        name='end_date',
        label='퇴사일',
        order=50,
        field_type=FieldType.DATE,
        aliases=['endDate'],
    ),
    create_field(
        name='job_description',
        label='담당업무',
        order=60,
        field_type=FieldType.TEXTAREA,
        aliases=['jobDescription', 'duties'],
    ),
]

career_section = create_section(
    id='career',
    title='경력사항',
    icon='bi bi-briefcase',
    fields=CAREER_FIELDS,
    order=120,
    is_dynamic=True,
    max_items=20,
)


# =============================================================================
# 자격증 정보 섹션 (certificate)
# =============================================================================
CERTIFICATE_FIELDS = [
    create_field(
        name='certificate_name',
        label='자격증명',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['certificateName', 'name'],
        required=True,
        max_length=200,
    ),
    create_field(
        name='grade',
        label='등급',
        order=20,
        field_type=FieldType.TEXT,
        max_length=50,
    ),
    create_field(
        name='issuing_organization',
        label='발급기관',
        order=30,
        field_type=FieldType.TEXT,
        aliases=['issuingOrganization', 'issuer'],
        max_length=200,
    ),
    create_field(
        name='certificate_number',
        label='자격증번호',
        order=40,
        field_type=FieldType.TEXT,
        aliases=['certificateNumber', 'number'],
        max_length=100,
    ),
    create_field(
        name='acquisition_date',
        label='취득일',
        order=50,
        field_type=FieldType.DATE,
        aliases=['acquisitionDate', 'date'],
    ),
]

certificate_section = create_section(
    id='certificate',
    title='자격증',
    icon='bi bi-award',
    fields=CERTIFICATE_FIELDS,
    order=130,
    is_dynamic=True,
    max_items=30,
)


# =============================================================================
# 언어 능력 섹션 (language)
# =============================================================================
LANGUAGE_FIELDS = [
    create_field(
        name='language',
        label='언어',
        order=10,
        field_type=FieldType.SELECT,
        aliases=['name'],
        required=True,
        options_category='language',
    ),
    create_field(
        name='level',
        label='능숙도',
        order=20,
        field_type=FieldType.SELECT,
        options_category='language_level',
    ),
    create_field(
        name='test_name',
        label='시험명',
        order=30,
        field_type=FieldType.TEXT,
        aliases=['testName'],
        max_length=100,
    ),
    create_field(
        name='score',
        label='점수/등급',
        order=40,
        field_type=FieldType.TEXT,
        max_length=50,
    ),
    create_field(
        name='test_date',
        label='응시일',
        order=50,
        field_type=FieldType.DATE,
        aliases=['testDate'],
    ),
]

language_section = create_section(
    id='language',
    title='언어능력',
    icon='bi bi-translate',
    fields=LANGUAGE_FIELDS,
    order=140,
    is_dynamic=True,
    max_items=10,
)


# =============================================================================
# 가족 정보 섹션 (family)
# =============================================================================
FAMILY_FIELDS = [
    create_field(
        name='relation',
        label='관계',
        order=10,
        field_type=FieldType.SELECT,
        options_category='family_relation',
    ),
    create_field(
        name='name',
        label='성명',
        order=20,
        field_type=FieldType.TEXT,
        required=True,
        max_length=100,
    ),
    create_field(
        name='birth_date',
        label='생년월일',
        order=30,
        field_type=FieldType.DATE,
        aliases=['birthDate'],
    ),
    create_field(
        name='occupation',
        label='직업',
        order=40,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='contact',
        label='연락처',
        order=50,
        field_type=FieldType.TEL,
        aliases=['phone'],
        max_length=50,
    ),
    create_field(
        name='is_cohabitant',
        label='동거 여부',
        order=60,
        field_type=FieldType.CHECKBOX,
        aliases=['isCohabitant', 'cohabiting'],
    ),
]

family_section = create_section(
    id='family',
    title='가족사항',
    icon='bi bi-people',
    fields=FAMILY_FIELDS,
    order=150,
    is_dynamic=True,
    max_items=20,
)


# =============================================================================
# 수상 이력 섹션 (award)
# =============================================================================
AWARD_FIELDS = [
    create_field(
        name='award_date',
        label='수상일',
        order=10,
        field_type=FieldType.DATE,
        aliases=['awardDate', 'date'],
    ),
    create_field(
        name='award_name',
        label='수상명',
        order=20,
        field_type=FieldType.TEXT,
        aliases=['awardName', 'name'],
        required=True,
        max_length=200,
    ),
    create_field(
        name='issuer',
        label='수여기관',
        order=30,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
    create_field(
        name='note',
        label='비고',
        order=40,
        field_type=FieldType.TEXTAREA,
    ),
]

award_section = create_section(
    id='award',
    title='수상내역',
    icon='bi bi-trophy',
    fields=AWARD_FIELDS,
    order=160,
    is_dynamic=True,
    max_items=20,
)


# =============================================================================
# 프로젝트 참여 이력 섹션 (project_participation)
# =============================================================================
PROJECT_PARTICIPATION_FIELDS = [
    create_field(
        name='project_name',
        label='프로젝트명',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['projectName', 'name'],
        required=True,
        max_length=200,
    ),
    create_field(
        name='start_date',
        label='시작일',
        order=20,
        field_type=FieldType.DATE,
        aliases=['startDate'],
    ),
    create_field(
        name='end_date',
        label='종료일',
        order=30,
        field_type=FieldType.DATE,
        aliases=['endDate'],
    ),
    create_field(
        name='role',
        label='역할',
        order=40,
        field_type=FieldType.TEXT,
        aliases=['duties'],
        max_length=200,
    ),
    create_field(
        name='client',
        label='고객사',
        order=50,
        field_type=FieldType.TEXT,
        max_length=200,
    ),
]

project_participation_section = create_section(
    id='project_participation',
    title='프로젝트 참여이력',
    icon='bi bi-kanban',
    fields=PROJECT_PARTICIPATION_FIELDS,
    order=170,
    is_dynamic=True,
    max_items=30,
)


# =============================================================================
# 섹션 등록
# =============================================================================
FieldRegistry.register_section(education_section, domain='relation')
FieldRegistry.register_section(career_section, domain='relation')
FieldRegistry.register_section(certificate_section, domain='relation')
FieldRegistry.register_section(language_section, domain='relation')
FieldRegistry.register_section(family_section, domain='relation')
FieldRegistry.register_section(award_section, domain='relation')
FieldRegistry.register_section(project_participation_section, domain='relation')
