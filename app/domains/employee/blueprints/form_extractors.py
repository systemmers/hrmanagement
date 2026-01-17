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
        birth_date=form_data.get('birth_date'),
        is_lunar_birth=_parse_boolean(form_data.get('is_lunar_birth')),
        gender=form_data.get('gender'),
        address=form_data.get('address'),
        detailed_address=form_data.get('detailed_address'),
        resident_number=form_data.get('resident_number'),
        mobile_phone=form_data.get('mobile_phone'),
        nationality=form_data.get('nationality'),
        # Phase 28.3: blood_type, religion 삭제됨
        # Phase 0.7: chinese_name, home_phone, postal_code 삭제됨
        hobby=form_data.get('hobby'),
        specialty=form_data.get('specialty'),
        # 병역 및 비고 (Phase 0.7: MilitaryService → 기본정보 통합)
        military_status=form_data.get('military_status'),
        note=form_data.get('note'),
    )


def extract_basic_fields_from_form(form_data: FormData) -> Dict[str, Any]:
    """폼 데이터에서 기본정보 필드만 추출

    Phase 29: 별칭 제거, snake_case 직접 접근
    Phase 0.6 (2026-01-16): 11개 미매핑 필드 추가 (inline_edit_service SSOT 동기화)
    Phase 0.7 (2026-01-16): chinese_name, home_phone, postal_code, account_holder 삭제
                           military_status, note 추가 (MilitaryService 통합)
    """
    return {
        # 기본 정보
        'name': form_data.get('name', ''),
        'photo': form_data.get('photo') or '/static/images/face/face_01_m.png',
        'english_name': form_data.get('english_name'),
        'foreign_name': form_data.get('foreign_name'),
        'birth_date': form_data.get('birth_date'),
        'is_lunar_birth': _parse_boolean(form_data.get('is_lunar_birth')),
        'gender': form_data.get('gender'),
        'marital_status': form_data.get('marital_status'),
        # 연락처
        'phone': form_data.get('phone', ''),
        'email': form_data.get('email', ''),
        'mobile_phone': form_data.get('mobile_phone'),
        'emergency_contact': form_data.get('emergency_contact'),
        'emergency_relation': form_data.get('emergency_relation'),
        # 등록 주소
        'address': form_data.get('address'),
        'detailed_address': form_data.get('detailed_address'),
        # 실거주 주소
        'actual_address': form_data.get('actual_address'),
        'actual_detailed_address': form_data.get('actual_detailed_address'),
        'actual_postal_code': form_data.get('actual_postal_code'),
        # 기타 개인정보
        'resident_number': form_data.get('resident_number'),
        'nationality': form_data.get('nationality'),
        'hobby': form_data.get('hobby'),
        'specialty': form_data.get('specialty'),
        'disability_info': form_data.get('disability_info'),
        # 급여 계좌 정보
        'bank_name': form_data.get('bank_name'),
        'account_number': form_data.get('account_number'),
        # 병역 및 비고 (Phase 0.7: MilitaryService 통합)
        'military_status': form_data.get('military_status'),
        'note': form_data.get('note'),
    }


# ========================================
# 관계형 데이터 추출 함수 (Phase 27.1)
# Phase 31: extract_relation_list -> utils/form_helpers.py로 이동
# ========================================

def extract_family_list(form_data: FormData) -> List[Dict[str, Any]]:
    """가족정보 리스트 추출 (Phase 0.7: 폼 필드명 → 모델 필드명 통일)"""
    items = extract_relation_list(form_data, 'family_', {
        'relation': 'relation',
        'name': 'name',
        'birth_date': 'birth_date',
        'occupation': 'occupation',
        'contact': 'contact',  # Phase 0.7: phone → contact
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
    """학력정보 리스트 추출

    Note: First field must exist in HTML form (determines record count)
    """
    return extract_relation_list(form_data, 'education_', {
        'school_name': 'school_name',  # First: exists in HTML form
        'school_type': 'school_type',
        'graduation_year': 'graduation_date',
        'major': 'major',
        'degree': 'degree',
        'graduation_status': 'graduation_status',
        'gpa': 'gpa',
        'note': 'note',
    })


def extract_career_list(form_data: FormData) -> List[Dict[str, Any]]:
    """경력정보 리스트 추출 (Phase 0.7: 폼 필드명 → 모델 필드명 통일)"""
    items = extract_relation_list(form_data, 'career_', {
        'company_name': 'company_name',
        'start_date': 'start_date',
        'end_date': 'end_date',
        'department': 'department',
        'position': 'position',
        'job_grade': 'job_grade',
        'job_title': 'job_title',
        'job_role': 'job_role',
        'job_description': 'job_description',  # Phase 0.7: duties → job_description
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
    """자격증정보 리스트 추출 (Phase 0.7: 폼 필드명 → 모델 필드명 통일)"""
    return extract_relation_list(form_data, 'certificate_', {
        'certificate_name': 'certificate_name',  # Phase 0.7: name → certificate_name
        'grade': 'grade',
        'issuing_organization': 'issuing_organization',
        'certificate_number': 'certificate_number',  # Phase 0.7: number → certificate_number
        'acquisition_date': 'acquisition_date',
        'expiry_date': 'expiry_date',
    })


def extract_language_list(form_data: FormData) -> List[Dict[str, Any]]:
    """언어능력정보 리스트 추출 (Phase 0.7: 폼 필드명 → 모델 필드명 통일)"""
    return extract_relation_list(form_data, 'language_', {
        'language_name': 'language_name',  # Phase 0.7: language → language_name
        'level': 'level',
        'exam_name': 'exam_name',  # Phase 0.7: test_name → exam_name
        'score': 'score',
        'acquisition_date': 'acquisition_date',  # Phase 0.7: test_date → acquisition_date
    })


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
    """수상정보 리스트 추출 (Phase 0.7: 폼 필드명 → 모델 필드명 통일)"""
    return extract_relation_list(form_data, 'award_', {
        'date': 'award_date',
        'name': 'award_name',
        'institution': 'institution',  # Phase 0.7: issuer → institution
        'note': 'note',
    })
