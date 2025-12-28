"""
폼 데이터 추출 함수 (Personal Blueprint)

FieldRegistry 기반 필드명 정규화를 적용합니다. (SSOT 원칙)
공통 헬퍼 모듈을 사용합니다. (DRY 원칙)
Phase 25: 공통 헬퍼 모듈로 이동 (2025-12-29)
"""
from ...utils.form_helpers import parse_boolean as _parse_boolean, normalize_form_field


def extract_profile_data(form_data, existing_profile=None):
    """폼 데이터에서 Profile 데이터 추출 (FieldRegistry 기반)

    Args:
        form_data: request.form 데이터
        existing_profile: 기존 프로필 객체 (기본값 유지용)

    Returns:
        dict: 프로필 업데이트용 데이터
    """
    # 섹션 ID 상수
    BASIC = 'personal_basic'
    CONTACT = 'contact'

    # 기본값 처리
    default_name = existing_profile.name if existing_profile else ''
    default_photo = existing_profile.photo if existing_profile else None

    return {
        # 기본 정보 - FieldRegistry 별칭 적용
        'name': form_data.get('name', default_name).strip(),
        'english_name': normalize_form_field(form_data, BASIC, 'english_name'),
        'chinese_name': form_data.get('chinese_name', '').strip() or None,
        'resident_number': normalize_form_field(form_data, BASIC, 'resident_number'),
        'birth_date': form_data.get('birth_date', '').strip() or None,
        'lunar_birth': _parse_boolean(form_data.get('lunar_birth')),
        'gender': form_data.get('gender', '').strip() or None,

        # 연락처 - FieldRegistry 별칭 적용
        'mobile_phone': normalize_form_field(form_data, CONTACT, 'mobile_phone'),
        'home_phone': normalize_form_field(form_data, CONTACT, 'home_phone'),
        'email': form_data.get('email', '').strip() or None,

        # 주소
        'postal_code': form_data.get('postal_code', '').strip() or None,
        'address': form_data.get('address', '').strip() or None,
        'detailed_address': form_data.get('detailed_address', '').strip() or None,

        # 기타 정보
        'nationality': form_data.get('nationality', '').strip() or None,
        'blood_type': form_data.get('blood_type', '').strip() or None,
        'religion': form_data.get('religion', '').strip() or None,
        'hobby': form_data.get('hobby', '').strip() or None,
        'specialty': form_data.get('specialty', '').strip() or None,
        'is_public': _parse_boolean(form_data.get('is_public')),

        # 사진은 별도 처리 (파일 업로드)
        'photo': default_photo,
    }


def extract_relation_list(form_data, prefix, fields):
    """동적 관계형 데이터 리스트 추출 (범용)

    Args:
        form_data: request.form 데이터
        prefix: 폼 필드 접두사 (예: 'education_', 'career_')
        fields: 추출할 필드 매핑 {form_suffix: model_field}

    Returns:
        list[dict]: 관계형 데이터 리스트
    """
    # 폼 리스트 데이터 수집
    form_lists = {}
    for form_suffix in fields.keys():
        form_key = f"{prefix}{form_suffix}[]"
        form_lists[form_suffix] = form_data.getlist(form_key)

    # 첫 번째 필드를 기준으로 레코드 수 결정
    first_field = list(fields.keys())[0]
    count = len(form_lists.get(first_field, []))

    result = []
    for i in range(count):
        record = {}
        for form_suffix, model_field in fields.items():
            values = form_lists.get(form_suffix, [])
            value = values[i] if i < len(values) else None
            if value:
                value = value.strip() if isinstance(value, str) else value
            record[model_field] = value or None
        result.append(record)

    return result


# ========================================
# 섹션별 데이터 추출 함수 (FieldRegistry 기반)
# ========================================

def extract_education_list(form_data):
    """학력 정보 리스트 추출"""
    return extract_relation_list(form_data, 'education_', {
        'school_name': 'school_name',
        'degree': 'degree',
        'major': 'major',
        'graduation_year': 'graduation_date',
        'gpa': 'gpa',
        'graduation_status': 'status',
        'note': 'notes',
    })


def extract_career_list(form_data):
    """경력 정보 리스트 추출"""
    items = extract_relation_list(form_data, 'career_', {
        'company_name': 'company_name',
        'department': 'department',
        'position': 'position',
        'job_grade': 'job_grade',
        'job_title': 'job_title',
        'job_role': 'job_role',
        'duties': 'responsibilities',
        'salary_type': 'salary_type',
        'salary': 'salary',
        'monthly_salary': 'monthly_salary',
        'pay_step': 'pay_step',
        'start_date': 'start_date',
        'end_date': 'end_date',
    })

    # 숫자 필드 변환
    for item in items:
        for field in ['salary', 'monthly_salary', 'pay_step']:
            if item.get(field):
                try:
                    item[field] = int(item[field])
                except (ValueError, TypeError):
                    item[field] = None

    return items


def extract_certificate_list(form_data):
    """자격증 정보 리스트 추출"""
    return extract_relation_list(form_data, 'certificate_', {
        'name': 'name',
        'issuer': 'issuing_organization',
        'acquisition_date': 'issue_date',
        'expiry_date': 'expiry_date',
        'number': 'certificate_number',
        'grade': 'grade',
    })


def extract_language_list(form_data):
    """언어능력 정보 리스트 추출"""
    return extract_relation_list(form_data, 'language_', {
        'language': 'language',
        'level': 'proficiency',
        'test_name': 'test_name',
        'score': 'score',
        'test_date': 'test_date',
    })


def extract_military_data(form_data):
    """병역 정보 추출 (1:1 관계)"""
    military_status = form_data.get('military_status', '').strip()
    if not military_status:
        return None

    # 복무기간 파싱 (YYYY-MM-DD ~ YYYY-MM-DD 또는 YYYY.MM ~ YYYY.MM 형식)
    military_period = form_data.get('military_period', '').strip()
    start_date = None
    end_date = None
    if military_period and '~' in military_period:
        parts = military_period.split('~')
        if len(parts) == 2:
            start_date = parts[0].strip()
            end_date = parts[1].strip()

    return {
        'military_status': military_status,
        'branch': form_data.get('military_branch', '').strip() or None,
        'rank': form_data.get('military_rank', '').strip() or None,
        'start_date': start_date,
        'end_date': end_date,
        'specialty': form_data.get('military_specialty', '').strip() or None,
        'service_type': form_data.get('military_duty', '').strip() or None,
        'notes': form_data.get('military_exemption_reason', '').strip() or None,
    }
