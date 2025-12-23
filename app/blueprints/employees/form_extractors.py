"""
폼 데이터 추출 함수

폼 데이터에서 Employee 객체 또는 딕셔너리를 생성하는 헬퍼 함수를 제공합니다.
Phase 9: FieldRegistry 기반 필드명 정규화 적용
"""
from typing import Any, Optional

from ...models import Employee
from ...constants.field_registry import FieldRegistry


def _parse_boolean(value) -> bool:
    """폼 데이터 boolean 변환 헬퍼 (DRY 원칙)"""
    return value in ('true', 'True', '1', True)


def normalize_form_field(
    form_data: dict,
    section_id: str,
    field_name: str,
    default: Any = None
) -> Optional[Any]:
    """FieldRegistry 기반 폼 필드값 추출 (SSOT 원칙)

    정규 필드명과 별칭을 모두 검색하여 값을 반환합니다.

    Args:
        form_data: request.form 데이터
        section_id: FieldRegistry 섹션 ID
        field_name: 정규 필드명
        default: 기본값 (기본: None)

    Returns:
        필드값 또는 default
    """
    # 정규 필드명으로 먼저 시도
    value = form_data.get(field_name)
    if value:
        return value

    # FieldRegistry에서 별칭 조회
    section = FieldRegistry.get_section(section_id)
    if section:
        field = section.get_field(field_name)
        if field and field.aliases:
            for alias in field.aliases:
                value = form_data.get(alias)
                if value:
                    return value

    return default


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
