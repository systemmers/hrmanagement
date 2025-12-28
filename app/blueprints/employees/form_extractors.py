"""
폼 데이터 추출 함수

폼 데이터에서 Employee 객체 또는 딕셔너리를 생성하는 헬퍼 함수를 제공합니다.
Phase 9: FieldRegistry 기반 필드명 정규화 적용
Phase 27.1: 관계형 데이터 추출 함수 추가 (DRY 원칙)
Phase 25: 공통 헬퍼 모듈로 이동 (2025-12-29)
"""
from typing import Any, Dict, List, Optional

from ...models import Employee
from ...utils.form_helpers import parse_boolean as _parse_boolean, normalize_form_field


def extract_employee_from_form(form_data, employee_id=0):
    """폼 데이터에서 Employee 객체 생성 (Phase 9: FieldRegistry 기반)"""
    # organization_id 처리
    org_id = form_data.get('organization_id')
    organization_id = int(org_id) if org_id and org_id.strip() else None

    # 섹션 ID 상수
    BASIC = 'personal_basic'
    CONTACT = 'contact'
    ORG = 'organization'

    return Employee(
        id=employee_id,
        # 기본 필드
        name=form_data.get('name', ''),
        photo=form_data.get('photo') or '/static/images/face/face_01_m.png',
        department=form_data.get('department', ''),
        position=form_data.get('position', ''),
        status=form_data.get('status', 'active'),
        # hire_date: FieldRegistry 별칭 적용 (hireDate -> hire_date)
        hire_date=normalize_form_field(form_data, ORG, 'hire_date', ''),
        phone=form_data.get('phone', ''),
        email=form_data.get('email', ''),
        # 조직 연결
        organization_id=organization_id,
        # 소속정보 추가 필드
        employee_number=form_data.get('employee_number'),
        team=form_data.get('team'),
        # 직급 체계 (Career 모델과 일관성)
        job_grade=form_data.get('job_grade'),
        job_title=form_data.get('job_title'),
        job_role=form_data.get('job_role'),
        work_location=form_data.get('work_location'),
        internal_phone=form_data.get('internal_phone'),
        company_email=form_data.get('company_email'),
        # 확장 필드 - 개인정보 (FieldRegistry 별칭 적용)
        english_name=normalize_form_field(form_data, BASIC, 'english_name'),
        chinese_name=form_data.get('chinese_name'),
        birth_date=form_data.get('birth_date'),
        lunar_birth=_parse_boolean(form_data.get('lunar_birth')),
        gender=form_data.get('gender'),
        address=form_data.get('address'),
        detailed_address=form_data.get('detailed_address'),
        postal_code=form_data.get('postal_code'),
        # resident_number: FieldRegistry 별칭 적용 (rrn -> resident_number)
        resident_number=normalize_form_field(form_data, BASIC, 'resident_number'),
        mobile_phone=normalize_form_field(form_data, CONTACT, 'mobile_phone'),
        home_phone=normalize_form_field(form_data, CONTACT, 'home_phone'),
        nationality=form_data.get('nationality'),
        blood_type=form_data.get('blood_type'),
        religion=form_data.get('religion'),
        hobby=form_data.get('hobby'),
        specialty=form_data.get('specialty'),
    )


def extract_basic_fields_from_form(form_data):
    """폼 데이터에서 기본정보 필드만 추출 (Phase 9: FieldRegistry 기반)"""
    # 섹션 ID 상수
    BASIC = 'personal_basic'
    CONTACT = 'contact'

    return {
        'name': form_data.get('name', ''),
        'photo': form_data.get('photo') or '/static/images/face/face_01_m.png',
        # FieldRegistry 별칭 적용
        'english_name': normalize_form_field(form_data, BASIC, 'english_name'),
        'chinese_name': form_data.get('chinese_name'),
        'birth_date': form_data.get('birth_date'),
        'lunar_birth': _parse_boolean(form_data.get('lunar_birth')),
        'gender': form_data.get('gender'),
        'phone': form_data.get('phone', ''),
        'email': form_data.get('email', ''),
        'mobile_phone': normalize_form_field(form_data, CONTACT, 'mobile_phone'),
        'home_phone': normalize_form_field(form_data, CONTACT, 'home_phone'),
        'address': form_data.get('address'),
        'detailed_address': form_data.get('detailed_address'),
        'postal_code': form_data.get('postal_code'),
        # FieldRegistry 별칭 적용 (rrn -> resident_number)
        'resident_number': normalize_form_field(form_data, BASIC, 'resident_number'),
        'nationality': form_data.get('nationality'),
        'blood_type': form_data.get('blood_type'),
        'religion': form_data.get('religion'),
        'hobby': form_data.get('hobby'),
        'specialty': form_data.get('specialty'),
    }


# ========================================
# 관계형 데이터 추출 함수 (Phase 27.1)
# ========================================

def extract_relation_list(
    form_data,
    prefix: str,
    field_mapping: Dict[str, str]
) -> List[Dict[str, Any]]:
    """동적 관계형 데이터 리스트 추출 (범용, DRY 원칙)

    Args:
        form_data: request.form 데이터
        prefix: 폼 필드 접두사 (예: 'family_', 'education_')
        field_mapping: {form_suffix: model_field} 매핑

    Returns:
        list[dict]: 관계형 데이터 리스트
    """
    # 폼 리스트 데이터 수집
    form_lists = {}
    for form_suffix in field_mapping.keys():
        form_key = f"{prefix}{form_suffix}[]"
        form_lists[form_suffix] = form_data.getlist(form_key)

    # 첫 번째 필드를 기준으로 레코드 수 결정
    first_field = list(field_mapping.keys())[0]
    count = len(form_lists.get(first_field, []))

    result = []
    for i in range(count):
        record = {}
        for form_suffix, model_field in field_mapping.items():
            values = form_lists.get(form_suffix, [])
            value = values[i] if i < len(values) else None
            if value:
                value = value.strip() if isinstance(value, str) else value
            record[model_field] = value or None
        result.append(record)

    return result


def extract_family_list(form_data) -> List[Dict[str, Any]]:
    """가족정보 리스트 추출"""
    items = extract_relation_list(form_data, 'family_', {
        'relation': 'relation',
        'name': 'name',
        'birth_date': 'birth_date',
        'occupation': 'occupation',
        'phone': 'contact',
        'is_cohabitant': 'is_cohabitant',
        'living_together': 'is_cohabitant',  # 레거시 별칭
    })

    # is_cohabitant boolean 변환
    for item in items:
        cohabitant = item.get('is_cohabitant')
        if cohabitant is not None:
            # SSOT 값: '동거'/'별거', 레거시 값: 'true'/'false'
            item['is_cohabitant'] = cohabitant in ('동거', 'true', True)
        else:
            item['is_cohabitant'] = False

    return items


def extract_education_list(form_data) -> List[Dict[str, Any]]:
    """학력정보 리스트 추출"""
    return extract_relation_list(form_data, 'education_', {
        'school_type': 'school_type',
        'school_name': 'school_name',
        'graduation_year': 'graduation_date',
        'major': 'major',
        'degree': 'degree',
        'graduation_status': 'graduation_status',
        'gpa': 'gpa',
        'note': 'note',
    })


def extract_career_list(form_data) -> List[Dict[str, Any]]:
    """경력정보 리스트 추출"""
    items = extract_relation_list(form_data, 'career_', {
        'company_name': 'company_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'department': 'department',
        'position': 'position',
        'job_grade': 'job_grade',
        'job_title': 'job_title',
        'job_role': 'job_role',
        'duties': 'job_description',
        'salary': 'salary',
        'salary_type': 'salary_type',
        'monthly_salary': 'monthly_salary',
        'pay_step': 'pay_step',
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


def extract_certificate_list(form_data) -> List[Dict[str, Any]]:
    """자격증정보 리스트 추출"""
    return extract_relation_list(form_data, 'certificate_', {
        'name': 'certificate_name',
        'grade': 'grade',
        'issuing_organization': 'issuing_organization',
        'issuer': 'issuing_organization',  # 레거시 별칭
        'number': 'certificate_number',
        'acquisition_date': 'acquisition_date',
        'date': 'acquisition_date',  # 레거시 별칭
        'expiry_date': 'expiry_date',
    })


def extract_language_list(form_data) -> List[Dict[str, Any]]:
    """언어능력정보 리스트 추출"""
    return extract_relation_list(form_data, 'language_', {
        'language': 'language_name',
        'name': 'language_name',  # 레거시 별칭
        'level': 'level',
        'test_name': 'exam_name',
        'score': 'score',
        'test_date': 'acquisition_date',
    })


def extract_military_data(form_data) -> Optional[Dict[str, Any]]:
    """병역정보 추출 (1:1 관계)"""
    military_status = form_data.get('military_status', '').strip()
    if not military_status:
        return None

    return {
        'military_status': military_status,
        'branch': form_data.get('military_branch') or None,
        'enlistment_date': form_data.get('military_start_date') or None,
        'discharge_date': form_data.get('military_end_date') or None,
        'rank': form_data.get('military_rank') or None,
        'discharge_reason': form_data.get('military_discharge_reason') or None,
    }


def extract_hr_project_list(form_data) -> List[Dict[str, Any]]:
    """인사이력 프로젝트 리스트 추출"""
    return extract_relation_list(form_data, 'hr_project_', {
        'name': 'project_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'duty': 'duty',
        'role': 'role',
        'client': 'client',
    })


def extract_project_participation_list(form_data) -> List[Dict[str, Any]]:
    """프로젝트 참여이력 리스트 추출"""
    return extract_relation_list(form_data, 'participation_', {
        'project_name': 'project_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'duty': 'duty',
        'role': 'role',
        'client': 'client',
    })


def extract_award_list(form_data) -> List[Dict[str, Any]]:
    """수상정보 리스트 추출"""
    return extract_relation_list(form_data, 'award_', {
        'date': 'award_date',
        'name': 'award_name',
        'issuer': 'issuer',
        'note': 'note',
    })
