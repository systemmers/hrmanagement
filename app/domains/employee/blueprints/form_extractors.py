"""
폼 데이터 추출 함수

폼 데이터에서 Employee 객체 또는 딕셔너리를 생성하는 헬퍼 함수를 제공합니다.
Phase 9: FieldRegistry 기반 필드명 정규화 적용
Phase 27.1: 관계형 데이터 추출 함수 추가 (DRY 원칙)
Phase 25: 공통 헬퍼 모듈로 이동 (2025-12-29)
"""
from typing import Any, Dict, List, Optional

from app.types import FormData, FieldMapping
from app.shared.constants.status import EmployeeStatus
from app.domains.employee.models import Employee
from app.shared.utils.form_helpers import (
    parse_boolean as _parse_boolean,
    extract_relation_list,  # Phase 31: DRY - 공통 모듈에서 import
)


def extract_employee_from_form(form_data: FormData, employee_id: int = 0) -> Employee:
    """폼 데이터에서 Employee 객체 생성 (Phase 29: 별칭 제거, snake_case 직접 접근)"""
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
        status=form_data.get('status', EmployeeStatus.ACTIVE),
        hire_date=form_data.get('hire_date', ''),
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
        # 확장 필드 - 개인정보 (Phase 29: 직접 접근)
        english_name=form_data.get('english_name'),
        chinese_name=form_data.get('chinese_name'),
        birth_date=form_data.get('birth_date'),
        lunar_birth=_parse_boolean(form_data.get('lunar_birth')),
        gender=form_data.get('gender'),
        address=form_data.get('address'),
        detailed_address=form_data.get('detailed_address'),
        postal_code=form_data.get('postal_code'),
        resident_number=form_data.get('resident_number'),
        mobile_phone=form_data.get('mobile_phone'),
        home_phone=form_data.get('home_phone'),
        nationality=form_data.get('nationality'),
        # Phase 28.3: blood_type, religion 삭제됨
        hobby=form_data.get('hobby'),
        specialty=form_data.get('specialty'),
    )


def extract_basic_fields_from_form(form_data: FormData) -> Dict[str, Any]:
    """폼 데이터에서 기본정보 필드만 추출 (Phase 29: 별칭 제거, snake_case 직접 접근)"""
    return {
        'name': form_data.get('name', ''),
        'photo': form_data.get('photo') or '/static/images/face/face_01_m.png',
        'english_name': form_data.get('english_name'),
        'chinese_name': form_data.get('chinese_name'),
        'birth_date': form_data.get('birth_date'),
        'lunar_birth': _parse_boolean(form_data.get('lunar_birth')),
        'gender': form_data.get('gender'),
        'phone': form_data.get('phone', ''),
        'email': form_data.get('email', ''),
        'mobile_phone': form_data.get('mobile_phone'),
        'home_phone': form_data.get('home_phone'),
        'address': form_data.get('address'),
        'detailed_address': form_data.get('detailed_address'),
        'postal_code': form_data.get('postal_code'),
        'resident_number': form_data.get('resident_number'),
        'nationality': form_data.get('nationality'),
        # Phase 28.3: blood_type, religion 삭제됨
        'hobby': form_data.get('hobby'),
        'specialty': form_data.get('specialty'),
    }


# ========================================
# 관계형 데이터 추출 함수 (Phase 27.1)
# Phase 31: extract_relation_list -> utils/form_helpers.py로 이동
# ========================================

def extract_family_list(form_data: FormData) -> List[Dict[str, Any]]:
    """가족정보 리스트 추출 (Phase 29: 레거시 별칭 제거)"""
    items = extract_relation_list(form_data, 'family_', {
        'relation': 'relation',
        'name': 'name',
        'birth_date': 'birth_date',
        'occupation': 'occupation',
        'phone': 'contact',
        'is_cohabitant': 'is_cohabitant',
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


def extract_education_list(form_data: FormData) -> List[Dict[str, Any]]:
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


def extract_career_list(form_data: FormData) -> List[Dict[str, Any]]:
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


def extract_certificate_list(form_data: FormData) -> List[Dict[str, Any]]:
    """자격증정보 리스트 추출 (Phase 29: 레거시 별칭 제거)"""
    return extract_relation_list(form_data, 'certificate_', {
        'name': 'certificate_name',
        'grade': 'grade',
        'issuing_organization': 'issuing_organization',
        'number': 'certificate_number',
        'acquisition_date': 'acquisition_date',
        'expiry_date': 'expiry_date',
    })


def extract_language_list(form_data: FormData) -> List[Dict[str, Any]]:
    """언어능력정보 리스트 추출 (Phase 29: 레거시 별칭 제거)"""
    return extract_relation_list(form_data, 'language_', {
        'language': 'language_name',
        'level': 'level',
        'test_name': 'exam_name',
        'score': 'score',
        'test_date': 'acquisition_date',
    })


def extract_military_data(form_data: FormData) -> Optional[Dict[str, Any]]:
    """병역정보 추출 (1:1 관계, Phase 30: DB 컬럼명 통일)"""
    military_status = form_data.get('military_status', '').strip()
    if not military_status:
        return None

    return {
        'military_status': military_status,
        'branch': form_data.get('military_branch') or None,
        'rank': form_data.get('military_rank') or None,
        'enlistment_date': form_data.get('military_start_date') or None,
        'discharge_date': form_data.get('military_end_date') or None,
        'service_type': form_data.get('military_duty') or None,           # Phase 30: 추가
        'specialty': form_data.get('military_specialty') or None,         # Phase 30: 추가
        'exemption_reason': form_data.get('military_exemption_reason') or None,  # Phase 30: discharge_reason → exemption_reason
    }


def extract_hr_project_list(form_data: FormData) -> List[Dict[str, Any]]:
    """인사이력 프로젝트 리스트 추출"""
    return extract_relation_list(form_data, 'hr_project_', {
        'name': 'project_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'duty': 'duty',
        'role': 'role',
        'client': 'client',
    })


def extract_project_participation_list(form_data: FormData) -> List[Dict[str, Any]]:
    """프로젝트 참여이력 리스트 추출"""
    return extract_relation_list(form_data, 'participation_', {
        'project_name': 'project_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'duty': 'duty',
        'role': 'role',
        'client': 'client',
    })


def extract_award_list(form_data: FormData) -> List[Dict[str, Any]]:
    """수상정보 리스트 추출 (Phase 30: DB 컬럼명 통일)"""
    return extract_relation_list(form_data, 'award_', {
        'date': 'award_date',
        'name': 'award_name',
        'issuer': 'institution',      # Phase 30: issuer → institution (DB 컬럼명)
        'note': 'note',
    })
