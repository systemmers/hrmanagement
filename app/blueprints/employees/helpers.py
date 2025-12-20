"""
직원 관리 헬퍼 함수

폼 데이터 처리, 관계형 데이터 업데이트 등 공통 헬퍼 함수를 제공합니다.

Phase 7: 모듈 분할 - 기능별 하위 모듈로 분리
- form_extractors.py: 폼 데이터 추출
- file_handlers.py: 파일 처리 유틸리티
- relation_updaters.py: 관계형 데이터 업데이트

이 파일은 하위 호환성을 위해 모든 함수를 re-export합니다.
"""

# ========================================
# 멀티테넌시 헬퍼 함수
# ========================================

from ...utils.tenant import get_current_organization_id
from ...services.employee_service import employee_service


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
    RelatedDataUpdater,
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

# __all__ 정의
__all__ = [
    # 멀티테넌시
    'verify_employee_access',
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
    'RelatedDataUpdater',
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
