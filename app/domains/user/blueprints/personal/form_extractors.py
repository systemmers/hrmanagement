"""
Form Data Extraction Functions (Personal Blueprint)

FieldRegistry-based field name normalization (SSOT principle)
Uses common helper modules (DRY principle)
Phase 1 Migration: domains/user/blueprints/personal/form_extractors.py
"""
from typing import Any, Dict, List, Optional

from app.types import FormData
from app.shared.utils.form_helpers import (
    parse_boolean as _parse_boolean,
    extract_relation_list,
)


def extract_profile_data(form_data: FormData, existing_profile=None) -> Dict[str, Any]:
    """Extract Profile data from form data

    Args:
        form_data: request.form data
        existing_profile: Existing profile object (for default values)

    Returns:
        dict: Profile update data
    """
    # Default value handling
    default_name = existing_profile.name if existing_profile else ''
    default_photo = existing_profile.photo if existing_profile else None

    return {
        # Basic info
        'name': form_data.get('name', default_name).strip(),
        'english_name': (form_data.get('english_name', '') or '').strip() or None,
        'chinese_name': form_data.get('chinese_name', '').strip() or None,
        'resident_number': (form_data.get('resident_number', '') or '').strip() or None,
        'birth_date': form_data.get('birth_date', '').strip() or None,
        'lunar_birth': _parse_boolean(form_data.get('lunar_birth')),
        'gender': form_data.get('gender', '').strip() or None,

        # Contact info
        'mobile_phone': (form_data.get('mobile_phone', '') or '').strip() or None,
        'home_phone': (form_data.get('home_phone', '') or '').strip() or None,
        'email': form_data.get('email', '').strip() or None,

        # Address
        'postal_code': form_data.get('postal_code', '').strip() or None,
        'address': form_data.get('address', '').strip() or None,
        'detailed_address': form_data.get('detailed_address', '').strip() or None,

        # Other info
        'nationality': form_data.get('nationality', '').strip() or None,
        'hobby': form_data.get('hobby', '').strip() or None,
        'specialty': form_data.get('specialty', '').strip() or None,
        'is_public': _parse_boolean(form_data.get('is_public')),

        # Photo handled separately (file upload)
        'photo': default_photo,
    }


# ========================================
# Section-specific data extraction functions (FieldRegistry based)
# ========================================

def extract_education_list(form_data):
    """Extract education info list"""
    return extract_relation_list(form_data, 'education_', {
        'school_type': 'school_type',
        'school_name': 'school_name',
        'degree': 'degree',
        'major': 'major',
        'graduation_year': 'graduation_date',
        'gpa': 'gpa',
        'graduation_status': 'graduation_status',
        'note': 'note',
    })


def extract_career_list(form_data):
    """Extract career info list"""
    items = extract_relation_list(form_data, 'career_', {
        'company_name': 'company_name',
        'department': 'department',
        'position': 'position',
        'job_grade': 'job_grade',
        'job_title': 'job_title',
        'job_role': 'job_role',
        'duties': 'job_description',
        'salary_type': 'salary_type',
        'salary': 'salary',
        'monthly_salary': 'monthly_salary',
        'pay_step': 'pay_step',
        'start_date': 'start_date',
        'end_date': 'end_date',
    })

    # Convert numeric fields
    for item in items:
        for field in ['salary', 'monthly_salary', 'pay_step']:
            if item.get(field):
                try:
                    item[field] = int(item[field])
                except (ValueError, TypeError):
                    item[field] = None

    return items


def extract_certificate_list(form_data):
    """Extract certificate info list"""
    return extract_relation_list(form_data, 'certificate_', {
        'name': 'certificate_name',
        'issuer': 'issuing_organization',
        'acquisition_date': 'acquisition_date',
        'expiry_date': 'expiry_date',
        'number': 'certificate_number',
        'grade': 'grade',
    })


def extract_language_list(form_data):
    """Extract language proficiency info list"""
    return extract_relation_list(form_data, 'language_', {
        'language': 'language_name',
        'level': 'level',
        'test_name': 'exam_name',
        'score': 'score',
        'test_date': 'acquisition_date',
    })


def extract_military_data(form_data):
    """Extract military service info (1:1 relation)"""
    military_status = form_data.get('military_status', '').strip()
    if not military_status:
        return None

    # Parse service period (YYYY-MM-DD ~ YYYY-MM-DD or YYYY.MM ~ YYYY.MM format)
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
        'enlistment_date': start_date,
        'discharge_date': end_date,
        'service_type': form_data.get('military_duty', '').strip() or None,
        'specialty': form_data.get('military_specialty', '').strip() or None,
        'exemption_reason': form_data.get('military_exemption_reason', '').strip() or None,
    }
