"""
직원 관리 헬퍼 함수

폼 데이터 처리, 관계형 데이터 업데이트 등 공통 헬퍼 함수를 제공합니다.

Phase 7: 모듈 분할 - 기능별 하위 모듈로 분리
- form_extractors.py: 폼 데이터 추출
- file_handlers.py: 파일 처리 유틸리티
- relation_updaters.py: 관계형 데이터 업데이트

Phase 3.3: Long Methods 분할
- extract_list_filter_params(): 목록 필터 파라미터 추출
- get_employee_detail_data(): 상세 페이지 데이터 일괄 조회

이 파일은 하위 호환성을 위해 모든 함수를 re-export합니다.
"""
from typing import Dict, Any
from flask import request

# ========================================
# 멀티테넌시 헬퍼 함수
# ========================================

from ...utils.tenant import get_current_organization_id
from ...services.employee_service import employee_service


# ========================================
# 필터/정렬 파라미터 추출 헬퍼
# ========================================

# 정렬 필드 매핑 (camelCase -> snake_case)
SORT_FIELD_MAP = {
    'id': 'id',
    'name': 'name',
    'department': 'department',
    'position': 'position',
    'hireDate': 'hire_date',
    'status': 'status'
}


def extract_list_filter_params() -> Dict[str, Any]:
    """직원 목록 필터/정렬 파라미터 추출

    Returns:
        Dict with keys:
        - departments: List[str] or None
        - positions: List[str] or None
        - statuses: List[str] or None
        - sort_column: str or None
        - sort_order: str ('asc' or 'desc')
    """
    # 다중 필터 파라미터
    departments = request.args.getlist('department') or None
    positions = request.args.getlist('position') or None
    statuses = request.args.getlist('status') or None

    # 단일 값 하위 호환성
    if not departments:
        dept = request.args.get('department')
        departments = [dept] if dept else None
    if not positions:
        pos = request.args.get('position')
        positions = [pos] if pos else None
    if not statuses:
        stat = request.args.get('status')
        statuses = [stat] if stat else None

    # 정렬 파라미터
    sort_by = request.args.get('sort')
    sort_order = request.args.get('order', 'asc')
    sort_column = SORT_FIELD_MAP.get(sort_by) if sort_by else None

    return {
        'departments': departments,
        'positions': positions,
        'statuses': statuses,
        'sort_column': sort_column,
        'sort_order': sort_order
    }


def get_employee_detail_data(employee_id: int) -> Dict[str, Any]:
    """직원 상세 페이지에 필요한 모든 데이터 조회

    Args:
        employee_id: 직원 ID

    Returns:
        Dict with all employee related data for template rendering
    """
    return {
        # 관계형 데이터
        'education_list': employee_service.get_education_list(employee_id),
        'career_list': employee_service.get_career_list(employee_id),
        'certificate_list': employee_service.get_certificate_list(employee_id),
        'family_list': employee_service.get_family_list(employee_id),
        'language_list': employee_service.get_language_list(employee_id),
        'military': employee_service.get_military_info(employee_id),
        # 급여/복리후생
        'salary': employee_service.get_salary_info(employee_id),
        'benefit': employee_service.get_benefit_info(employee_id),
        'contract': employee_service.get_contract_info(employee_id),
        'insurance': employee_service.get_insurance_info(employee_id),
        # 인사기록
        'salary_history_list': employee_service.get_salary_history_list(employee_id),
        'salary_payment_list': employee_service.get_salary_payment_list(employee_id),
        'promotion_list': employee_service.get_promotion_list(employee_id),
        'evaluation_list': employee_service.get_evaluation_list(employee_id),
        'training_list': employee_service.get_training_list(employee_id),
        'attendance_summary': employee_service.get_attendance_summary(employee_id, 2025),
        # 부가 정보
        'hr_project_list': employee_service.get_hr_project_list(employee_id),
        'project_participation_list': employee_service.get_project_participation_list(employee_id),
        'award_list': employee_service.get_award_list(employee_id),
        'asset_list': employee_service.get_asset_list(employee_id),
        # 첨부파일
        'attachment_list': employee_service.get_attachment_list(employee_id),
        'business_card_front': employee_service.get_attachment_by_category(employee_id, 'business_card_front'),
        'business_card_back': employee_service.get_attachment_by_category(employee_id, 'business_card_back'),
    }


# ========================================
# 멀티테넌시 검증
# ========================================

def verify_employee_access(employee_id: int) -> bool:
    """현재 회사가 해당 직원에 접근 가능한지 확인

    Args:
        employee_id: 직원 ID

    Returns:
        접근 가능 여부
    """
    org_id = get_current_organization_id()
    if not org_id:
        return False
    return employee_service.verify_ownership(employee_id, org_id)


# ========================================
# 하위 모듈 re-export (하위 호환성)
# ========================================

# 폼 데이터 추출 함수
from .form_extractors import (
    extract_employee_from_form,
    extract_basic_fields_from_form,
)

# 파일 처리 함수
from .file_handlers import (
    ALLOWED_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE,
    allowed_file,
    allowed_image_file,
    get_file_extension,
    get_upload_folder,
    get_profile_photo_folder,
    get_business_card_folder,
    generate_unique_filename,
    delete_file_if_exists,
)

# 관계형 데이터 업데이트 함수
from .relation_updaters import (
    EmployeeRelationUpdater,
    employee_relation_updater,
    update_family_data,
    update_education_data,
    update_career_data,
    update_certificate_data,
    update_language_data,
    update_military_data,
    update_hr_project_data,
    update_project_participation_data,
    update_award_data,
)

# 하위 호환성 alias (Phase 27.1: RelatedDataUpdater -> EmployeeRelationUpdater)
RelatedDataUpdater = EmployeeRelationUpdater

# __all__ 정의
__all__ = [
    # 멀티테넌시
    'verify_employee_access',
    # 필터/정렬
    'SORT_FIELD_MAP',
    'extract_list_filter_params',
    'get_employee_detail_data',
    # 폼 데이터 추출
    'extract_employee_from_form',
    'extract_basic_fields_from_form',
    # 파일 처리
    'ALLOWED_EXTENSIONS',
    'ALLOWED_IMAGE_EXTENSIONS',
    'MAX_FILE_SIZE',
    'MAX_IMAGE_SIZE',
    'allowed_file',
    'allowed_image_file',
    'get_file_extension',
    'get_upload_folder',
    'get_profile_photo_folder',
    'get_business_card_folder',
    'generate_unique_filename',
    'delete_file_if_exists',
    # 관계형 데이터 업데이트
    'EmployeeRelationUpdater',
    'employee_relation_updater',
    'RelatedDataUpdater',  # 하위 호환성 alias
    'update_family_data',
    'update_education_data',
    'update_career_data',
    'update_certificate_data',
    'update_language_data',
    'update_military_data',
    'update_hr_project_data',
    'update_project_participation_data',
    'update_award_data',
]
