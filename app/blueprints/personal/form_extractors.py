"""
폼 데이터 추출 함수 (Personal Blueprint)

FieldRegistry 기반 필드명 정규화를 적용합니다. (SSOT 원칙)
공통 헬퍼 모듈을 사용합니다. (DRY 원칙)
Phase 25: 공통 헬퍼 모듈로 이동 (2025-12-29)
"""
from typing import Any, Dict, List, Optional

from app.types import FormData
from ...utils.form_helpers import (
    parse_boolean as _parse_boolean,
    extract_relation_list,  # Phase 31: DRY - 공통 모듈에서 import
)


def extract_profile_data(form_data: FormData, existing_profile=None) -> Dict[str, Any]:
    """폼 데이터에서 Profile 데이터 추출 (Phase 29: 별칭 제거, snake_case 직접 접근)

    Args:
        form_data: request.form 데이터
        existing_profile: 기존 프로필 객체 (기본값 유지용)

    Returns:
        dict: 프로필 업데이트용 데이터
    """
    # 기본값 처리
    default_name = existing_profile.name if existing_profile else ''
    default_photo = existing_profile.photo if existing_profile else None

    return {
        # 기본 정보 (Phase 29: 직접 접근)
        'name': form_data.get('name', default_name).strip(),
        'english_name': (form_data.get('english_name', '') or '').strip() or None,
        'chinese_name': form_data.get('chinese_name', '').strip() or None,
        'resident_number': (form_data.get('resident_number', '') or '').strip() or None,
        'birth_date': form_data.get('birth_date', '').strip() or None,
        'lunar_birth': _parse_boolean(form_data.get('lunar_birth')),
        'gender': form_data.get('gender', '').strip() or None,

        # 연락처 (Phase 29: 직접 접근)
        'mobile_phone': (form_data.get('mobile_phone', '') or '').strip() or None,
        'home_phone': (form_data.get('home_phone', '') or '').strip() or None,
        'email': form_data.get('email', '').strip() or None,

        # 주소
        'postal_code': form_data.get('postal_code', '').strip() or None,
        'address': form_data.get('address', '').strip() or None,
        'detailed_address': form_data.get('detailed_address', '').strip() or None,

        # 기타 정보
        'nationality': form_data.get('nationality', '').strip() or None,
        # Phase 28.3: blood_type, religion 삭제됨
        'hobby': form_data.get('hobby', '').strip() or None,
        'specialty': form_data.get('specialty', '').strip() or None,
        'is_public': _parse_boolean(form_data.get('is_public')),

        # 사진은 별도 처리 (파일 업로드)
        'photo': default_photo,
    }


# ========================================
# 섹션별 데이터 추출 함수 (FieldRegistry 기반)
# Phase 31: extract_relation_list -> utils/form_helpers.py로 이동
# ========================================

def extract_education_list(form_data):
    """학력 정보 리스트 추출 (Phase 30: DB 컬럼명 통일)"""
    return extract_relation_list(form_data, 'education_', {
        'school_type': 'school_type',           # Phase 30: 추가
        'school_name': 'school_name',
        'degree': 'degree',
        'major': 'major',
        'graduation_year': 'graduation_date',
        'gpa': 'gpa',
        'graduation_status': 'graduation_status',  # Phase 30: status → graduation_status
        'note': 'note',                            # Phase 30: notes → note
    })


def extract_career_list(form_data):
    """경력 정보 리스트 추출 (Phase 30: DB 컬럼명 통일)"""
    items = extract_relation_list(form_data, 'career_', {
        'company_name': 'company_name',
        'department': 'department',
        'position': 'position',
        'job_grade': 'job_grade',
        'job_title': 'job_title',
        'job_role': 'job_role',
        'duties': 'job_description',           # Phase 30: responsibilities → job_description
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
    """자격증 정보 리스트 추출 (Phase 30: DB 컬럼명 통일)"""
    return extract_relation_list(form_data, 'certificate_', {
        'name': 'certificate_name',            # Phase 30: name → certificate_name
        'issuer': 'issuing_organization',
        'acquisition_date': 'acquisition_date', # Phase 30: issue_date → acquisition_date
        'expiry_date': 'expiry_date',
        'number': 'certificate_number',
        'grade': 'grade',
    })


def extract_language_list(form_data):
    """언어능력 정보 리스트 추출 (Phase 30: DB 컬럼명 통일)"""
    return extract_relation_list(form_data, 'language_', {
        'language': 'language_name',           # Phase 30: language → language_name
        'level': 'level',                      # Phase 30: proficiency → level
        'test_name': 'exam_name',              # Phase 30: test_name → exam_name
        'score': 'score',
        'test_date': 'acquisition_date',       # Phase 30: test_date → acquisition_date
    })


def extract_military_data(form_data):
    """병역 정보 추출 (1:1 관계, Phase 30: DB 컬럼명 통일)"""
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
        'enlistment_date': start_date,         # Phase 30: start_date → enlistment_date
        'discharge_date': end_date,            # Phase 30: end_date → discharge_date
        'service_type': form_data.get('military_duty', '').strip() or None,
        'specialty': form_data.get('military_specialty', '').strip() or None,
        'exemption_reason': form_data.get('military_exemption_reason', '').strip() or None,  # Phase 30: note → exemption_reason
    }
