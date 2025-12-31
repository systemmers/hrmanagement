"""
Organization Section Definitions

법인 소속 관련 섹션 정의 (소속정보, 계약정보, 급여정보 등)
법인 계정(corporate)에서만 표시됨.
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
# 소속 정보 섹션 (organization)
# =============================================================================
ORGANIZATION_FIELDS = [
    create_field(
        name='employee_number',
        label='사번',
        order=10,
        field_type=FieldType.TEXT,
        aliases=['employeeNumber'],
        max_length=50,
    ),
    create_field(
        name='organization_id',
        label='소속 조직',
        order=20,
        field_type=FieldType.SELECT,
        aliases=['organizationId'],
    ),
    create_field(
        name='department',
        label='부서명',  # Phase 28: 부서 → 부서명 (Edit 폼 라벨과 통일)
        order=30,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='team',
        label='팀',
        order=40,
        field_type=FieldType.TEXT,
        max_length=100,
    ),
    create_field(
        name='position',
        label='직위',
        order=50,
        field_type=FieldType.SELECT,
        options_category='position',
    ),
    create_field(
        name='job_title',
        label='직책',
        order=60,
        field_type=FieldType.TEXT,
        aliases=['jobTitle'],
        max_length=100,
    ),
    create_field(
        name='hire_date',
        label='입사일',
        order=70,
        field_type=FieldType.DATE,
        aliases=['hireDate'],
    ),
    create_field(
        name='status',
        label='재직상태',
        order=80,
        field_type=FieldType.SELECT,
        options_category='employment_status',
    ),
    create_field(
        name='work_location',
        label='근무지',
        order=90,
        field_type=FieldType.TEXT,
        aliases=['workLocation'],
        max_length=200,
    ),
    create_field(
        name='internal_phone',
        label='내선번호',
        order=100,
        field_type=FieldType.TEL,
        aliases=['internalPhone'],
        max_length=20,
    ),
    create_field(
        name='company_email',
        label='사내 이메일',
        order=110,
        field_type=FieldType.EMAIL,
        aliases=['companyEmail'],
        max_length=200,
    ),
]

organization_section = create_section(
    id='organization',
    title='소속정보',
    icon='bi bi-building',
    fields=ORGANIZATION_FIELDS,
    order=60,
    visibility=Visibility.CORPORATE,
)


# =============================================================================
# 계약 정보 섹션 (contract)
# =============================================================================
CONTRACT_FIELDS = [
    create_field(
        name='contract_type',
        label='계약유형',
        order=10,
        field_type=FieldType.SELECT,
        aliases=['contractType'],
        options_category='contract_type',
    ),
    create_field(
        name='contract_start',
        label='계약시작일',
        order=20,
        field_type=FieldType.DATE,
        aliases=['contractStart', 'start_date'],
    ),
    create_field(
        name='contract_end',
        label='계약종료일',
        order=30,
        field_type=FieldType.DATE,
        aliases=['contractEnd', 'end_date'],
    ),
    create_field(
        name='probation_period',
        label='수습기간',
        order=40,
        field_type=FieldType.NUMBER,
        aliases=['probationPeriod'],
        help_text='개월 수',
    ),
    create_field(
        name='probation_end',
        label='수습종료일',
        order=50,
        field_type=FieldType.DATE,
        aliases=['probationEnd'],
    ),
    create_field(
        name='working_hours',
        label='근무시간',
        order=60,
        field_type=FieldType.TEXT,
        aliases=['workingHours'],
        max_length=100,
    ),
    create_field(
        name='work_type',
        label='근무형태',
        order=70,
        field_type=FieldType.SELECT,
        aliases=['workType'],
        options_category='work_type',
    ),
]

contract_section = create_section(
    id='contract',
    title='계약정보',
    icon='bi bi-file-earmark-text',
    fields=CONTRACT_FIELDS,
    order=70,
    visibility=Visibility.CORPORATE,
)


# =============================================================================
# 급여 정보 섹션 (salary)
# =============================================================================
SALARY_FIELDS = [
    create_field(
        name='base_salary',
        label='기본급',
        order=10,
        field_type=FieldType.NUMBER,
        aliases=['baseSalary'],
    ),
    create_field(
        name='salary_type',
        label='급여유형',
        order=20,
        field_type=FieldType.SELECT,
        aliases=['salaryType'],
        options_category='salary_type',
    ),
    create_field(
        name='payment_method',
        label='지급방법',
        order=30,
        field_type=FieldType.SELECT,
        aliases=['paymentMethod'],
        options_category='payment_method',
    ),
    create_field(
        name='bank_name',
        label='은행명',
        order=40,
        field_type=FieldType.SELECT,
        aliases=['bankName'],
        options_category='bank',
    ),
    create_field(
        name='account_number',
        label='계좌번호',
        order=50,
        field_type=FieldType.TEXT,
        aliases=['accountNumber'],
        max_length=50,
    ),
    create_field(
        name='account_holder',
        label='예금주',
        order=60,
        field_type=FieldType.TEXT,
        aliases=['accountHolder'],
        max_length=50,
    ),
]

salary_section = create_section(
    id='salary',
    title='급여정보',
    icon='bi bi-cash',
    fields=SALARY_FIELDS,
    order=80,
    visibility=Visibility.CORPORATE,
)


# =============================================================================
# 복리후생 정보 섹션 (benefit)
# =============================================================================
BENEFIT_FIELDS = [
    create_field(
        name='annual_leave',
        label='연차',
        order=10,
        field_type=FieldType.NUMBER,
        aliases=['annualLeave'],
    ),
    create_field(
        name='used_leave',
        label='사용연차',
        order=20,
        field_type=FieldType.NUMBER,
        aliases=['usedLeave'],
    ),
    create_field(
        name='remaining_leave',
        label='잔여연차',
        order=30,
        field_type=FieldType.NUMBER,
        aliases=['remainingLeave'],
    ),
    create_field(
        name='meal_allowance',
        label='식대',
        order=40,
        field_type=FieldType.NUMBER,
        aliases=['mealAllowance'],
    ),
    create_field(
        name='transportation_allowance',
        label='교통비',
        order=50,
        field_type=FieldType.NUMBER,
        aliases=['transportationAllowance'],
    ),
]

benefit_section = create_section(
    id='benefit',
    title='복리후생',
    icon='bi bi-gift',
    fields=BENEFIT_FIELDS,
    order=90,
    visibility=Visibility.CORPORATE,
)


# =============================================================================
# 4대보험 정보 섹션 (insurance)
# =============================================================================
INSURANCE_FIELDS = [
    create_field(
        name='national_pension',
        label='국민연금',
        order=10,
        field_type=FieldType.CHECKBOX,
        aliases=['nationalPension'],
    ),
    create_field(
        name='health_insurance',
        label='건강보험',
        order=20,
        field_type=FieldType.CHECKBOX,
        aliases=['healthInsurance'],
    ),
    create_field(
        name='employment_insurance',
        label='고용보험',
        order=30,
        field_type=FieldType.CHECKBOX,
        aliases=['employmentInsurance'],
    ),
    create_field(
        name='industrial_insurance',
        label='산재보험',
        order=40,
        field_type=FieldType.CHECKBOX,
        aliases=['industrialInsurance'],
    ),
    create_field(
        name='national_pension_number',
        label='국민연금 번호',
        order=50,
        field_type=FieldType.TEXT,
        aliases=['nationalPensionNumber'],
        max_length=50,
    ),
    create_field(
        name='health_insurance_number',
        label='건강보험 번호',
        order=60,
        field_type=FieldType.TEXT,
        aliases=['healthInsuranceNumber'],
        max_length=50,
    ),
]

insurance_section = create_section(
    id='insurance',
    title='4대보험',
    icon='bi bi-shield-check',
    fields=INSURANCE_FIELDS,
    order=95,
    visibility=Visibility.CORPORATE,
)


# =============================================================================
# 섹션 등록
# =============================================================================
FieldRegistry.register_section(organization_section, domain='employee')
FieldRegistry.register_section(contract_section, domain='employee')
FieldRegistry.register_section(salary_section, domain='employee')
FieldRegistry.register_section(benefit_section, domain='employee')
FieldRegistry.register_section(insurance_section, domain='employee')
