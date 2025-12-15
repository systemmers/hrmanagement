"""
폼 데이터 추출 함수

폼 데이터에서 Employee 객체 또는 딕셔너리를 생성하는 헬퍼 함수를 제공합니다.
"""
from ...models import Employee


def extract_employee_from_form(form_data, employee_id=0):
    """폼 데이터에서 Employee 객체 생성 (SSOT 헬퍼 함수)"""
    # organization_id 처리
    org_id = form_data.get('organization_id')
    organization_id = int(org_id) if org_id and org_id.strip() else None

    return Employee(
        id=employee_id,
        # 기본 필드
        name=form_data.get('name', ''),
        photo=form_data.get('photo') or '/static/images/face/face_01_m.png',
        department=form_data.get('department', ''),
        position=form_data.get('position', ''),
        status=form_data.get('status', 'active'),
        hire_date=form_data.get('hire_date') or form_data.get('hireDate', ''),
        phone=form_data.get('phone', ''),
        email=form_data.get('email', ''),
        # 조직 연결
        organization_id=organization_id,
        # 소속정보 추가 필드
        employee_number=form_data.get('employee_number') or None,
        team=form_data.get('team') or None,
        job_title=form_data.get('job_title') or None,
        work_location=form_data.get('work_location') or None,
        internal_phone=form_data.get('internal_phone') or None,
        company_email=form_data.get('company_email') or None,
        # 확장 필드 - 개인정보
        english_name=form_data.get('english_name') or form_data.get('name_en') or None,
        birth_date=form_data.get('birth_date') or None,
        gender=form_data.get('gender') or None,
        address=form_data.get('address') or None,
        detailed_address=form_data.get('detailed_address') or None,
        postal_code=form_data.get('postal_code') or None,
        resident_number=form_data.get('resident_number') or form_data.get('rrn') or None,
        mobile_phone=form_data.get('mobile_phone') or None,
        home_phone=form_data.get('home_phone') or None,
        nationality=form_data.get('nationality') or None,
        blood_type=form_data.get('blood_type') or None,
        religion=form_data.get('religion') or None,
        hobby=form_data.get('hobby') or None,
        specialty=form_data.get('specialty') or None,
    )


def extract_basic_fields_from_form(form_data):
    """폼 데이터에서 기본정보 필드만 추출"""
    return {
        'name': form_data.get('name', ''),
        'photo': form_data.get('photo') or '/static/images/face/face_01_m.png',
        'english_name': form_data.get('english_name') or form_data.get('name_en') or None,
        'birth_date': form_data.get('birth_date') or None,
        'gender': form_data.get('gender') or None,
        'phone': form_data.get('phone', ''),
        'email': form_data.get('email', ''),
        'mobile_phone': form_data.get('mobile_phone') or None,
        'home_phone': form_data.get('home_phone') or None,
        'address': form_data.get('address') or None,
        'detailed_address': form_data.get('detailed_address') or None,
        'postal_code': form_data.get('postal_code') or None,
        'resident_number': form_data.get('resident_number') or form_data.get('rrn') or None,
        'nationality': form_data.get('nationality') or None,
        'blood_type': form_data.get('blood_type') or None,
        'religion': form_data.get('religion') or None,
        'hobby': form_data.get('hobby') or None,
        'specialty': form_data.get('specialty') or None,
    }
