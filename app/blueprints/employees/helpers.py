"""
직원 관리 헬퍼 함수

폼 데이터 처리, 관계형 데이터 업데이트 등 공통 헬퍼 함수를 제공합니다.
Sprint 2: 파일 유틸리티는 FileStorageService로 이동, 하위 호환성 유지를 위해 re-export
"""
import os
from datetime import datetime
from werkzeug.utils import secure_filename
from flask import current_app

from ...utils.tenant import get_current_organization_id
from ...extensions import (
    employee_repo, family_repo, education_repo, career_repo,
    certificate_repo, language_repo, military_repo,
    project_repo, award_repo, attachment_repo
)
from ...models import Employee
from ...services.file_storage_service import (
    file_storage,
    ALLOWED_EXTENSIONS,
    ALLOWED_IMAGE_EXTENSIONS,
    MAX_FILE_SIZE,
    MAX_IMAGE_SIZE
)


# ========================================
# 멀티테넌시 헬퍼 함수
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
    return employee_repo.verify_ownership(employee_id, org_id)


# ========================================
# 파일 유틸리티 함수 (FileStorageService 위임)
# 기존 API 호환성을 위해 래퍼 함수 유지
# ========================================

def allowed_file(filename):
    """허용된 파일 확장자 검사 (FileStorageService 위임)"""
    return file_storage.allowed_file(filename)


def allowed_image_file(filename):
    """허용된 이미지 파일 확장자 검사 (FileStorageService 위임)"""
    return file_storage.allowed_image_file(filename)


def get_file_extension(filename):
    """파일 확장자 추출 (FileStorageService 위임)"""
    return file_storage.get_file_extension(filename)


def get_upload_folder():
    """업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_profile_photo_folder():
    """프로필 사진 업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_photos')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_business_card_folder():
    """명함 이미지 업로드 폴더 경로 반환 및 생성 (레거시 호환)"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'business_cards')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(employee_id, original_filename, prefix=''):
    """고유한 파일명 생성 (FileStorageService 위임)"""
    return file_storage.generate_filename(original_filename, prefix, employee_id)


def delete_file_if_exists(file_path):
    """파일이 존재하면 삭제 (FileStorageService 위임)"""
    return file_storage.delete_file(file_path)


# ========================================
# 폼 데이터 처리 함수
# ========================================

def extract_employee_from_form(form_data, employee_id=0):
    """폼 데이터에서 Employee 객체 생성 (SSOT 헬퍼 함수)"""
    # organization_id 처리
    org_id = form_data.get('organization_id')
    organization_id = int(org_id) if org_id and org_id.strip() else None

    return Employee(
        id=employee_id,
        # 기본 필드
        name=form_data.get('name', ''),
        photo=form_data.get('photo') or 'https://i.pravatar.cc/150',
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
        'photo': form_data.get('photo') or 'https://i.pravatar.cc/150',
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


# ========================================
# 관계형 데이터 업데이트 - 범용 클래스
# ========================================

class RelatedDataUpdater:
    """관계형 데이터 업데이트를 위한 범용 헬퍼 클래스

    반복적인 update_*_data() 함수들의 공통 패턴을 추상화합니다.
    """

    def __init__(self, model_class, repository, form_prefix, required_field, field_mapping, converters=None):
        """
        Args:
            model_class: SQLAlchemy 모델 클래스
            repository: 레포지토리 인스턴스
            form_prefix: 폼 필드 접두사 (예: 'family_', 'education_')
            required_field: 필수 필드 suffix (이 필드가 있어야 레코드 생성)
            field_mapping: {form_field_suffix: model_attribute} 매핑
            converters: {model_attribute: converter_func} 타입 변환 함수
        """
        self.model_class = model_class
        self.repository = repository
        self.form_prefix = form_prefix
        self.required_field = required_field
        self.field_mapping = field_mapping
        self.converters = converters or {}

    def update(self, employee_id, form_data):
        """관계형 데이터 업데이트 실행"""
        # 기존 데이터 삭제
        self.repository.delete_by_employee_id(employee_id)

        # 폼 데이터 추출
        form_lists = {}
        for field_suffix in self.field_mapping.keys():
            form_key = f"{self.form_prefix}{field_suffix}[]"
            form_lists[field_suffix] = form_data.getlist(form_key)

        # 필수 필드 리스트를 기준으로 반복
        required_values = form_lists.get(self.required_field, [])

        for i in range(len(required_values)):
            if required_values[i]:  # 필수 필드가 있는 경우만
                model_data = {'employee_id': employee_id}

                for field_suffix, model_attr in self.field_mapping.items():
                    values = form_lists.get(field_suffix, [])
                    value = values[i] if i < len(values) else None

                    # 타입 변환 적용
                    if model_attr in self.converters and value is not None:
                        value = self.converters[model_attr](value)

                    model_data[model_attr] = value

                instance = self.model_class(**model_data)
                self.repository.create(instance)


# ========================================
# 관계형 데이터 Updater 인스턴스 생성 함수
# ========================================

def _get_family_updater():
    """가족정보 Updater 생성"""
    from ...models import FamilyMember
    return RelatedDataUpdater(
        model_class=FamilyMember,
        repository=family_repo,
        form_prefix='family_',
        required_field='name',
        field_mapping={
            'relation': 'relation',
            'name': 'name',
            'birth_date': 'birth_date',
            'occupation': 'occupation',
            'phone': 'contact',
            'cohabiting': 'is_cohabitant',
        },
        converters={'is_cohabitant': bool}
    )


def _get_education_updater():
    """학력정보 Updater 생성"""
    from ...models import Education
    return RelatedDataUpdater(
        model_class=Education,
        repository=education_repo,
        form_prefix='education_',
        required_field='school_name',
        field_mapping={
            'school_type': 'school_type',
            'school_name': 'school_name',
            'graduation_year': 'graduation_date',
            'major': 'major',
            'degree': 'degree',
            'graduation_status': 'graduation_status',
        }
    )


def _get_career_updater():
    """경력정보 Updater 생성"""
    from ...models import Career
    return RelatedDataUpdater(
        model_class=Career,
        repository=career_repo,
        form_prefix='career_',
        required_field='company_name',
        field_mapping={
            'company_name': 'company_name',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'department': 'department',
            'position': 'position',
            'duties': 'job_description',
        }
    )


def _get_certificate_updater():
    """자격증정보 Updater 생성"""
    from ...models import Certificate
    return RelatedDataUpdater(
        model_class=Certificate,
        repository=certificate_repo,
        form_prefix='certificate_',
        required_field='name',
        field_mapping={
            'name': 'certificate_name',
            'grade': 'grade',
            'issuer': 'issuing_organization',
            'number': 'certificate_number',
            'date': 'acquisition_date',
        }
    )


def _get_language_updater():
    """언어능력정보 Updater 생성"""
    from ...models import Language
    return RelatedDataUpdater(
        model_class=Language,
        repository=language_repo,
        form_prefix='language_',
        required_field='name',
        field_mapping={
            'name': 'language',
            'level': 'level',
            'test_name': 'test_name',
            'score': 'score',
            'test_date': 'test_date',
        }
    )


def _get_project_updater():
    """프로젝트정보 Updater 생성"""
    from ...models import Project
    return RelatedDataUpdater(
        model_class=Project,
        repository=project_repo,
        form_prefix='project_',
        required_field='name',
        field_mapping={
            'name': 'project_name',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'duties': 'duties',
            'role': 'role',
            'client': 'client',
        }
    )


def _get_award_updater():
    """수상정보 Updater 생성"""
    from ...models import Award
    return RelatedDataUpdater(
        model_class=Award,
        repository=award_repo,
        form_prefix='award_',
        required_field='name',
        field_mapping={
            'date': 'award_date',
            'name': 'award_name',
            'issuer': 'issuer',
            'note': 'note',
        }
    )


# ========================================
# 관계형 데이터 업데이트 래퍼 함수 (기존 API 호환)
# ========================================

def update_family_data(employee_id, form_data):
    """가족정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_family_updater().update(employee_id, form_data)


def update_education_data(employee_id, form_data):
    """학력정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_education_updater().update(employee_id, form_data)


def update_career_data(employee_id, form_data):
    """경력정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_career_updater().update(employee_id, form_data)


def update_certificate_data(employee_id, form_data):
    """자격증정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_certificate_updater().update(employee_id, form_data)


def update_language_data(employee_id, form_data):
    """언어능력정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_language_updater().update(employee_id, form_data)


def update_military_data(employee_id, form_data):
    """병역정보 업데이트"""
    from ...models import MilitaryService

    military_repo.delete_by_employee_id(employee_id)

    military_status = form_data.get('military_status')
    if military_status:
        military = MilitaryService(
            employee_id=employee_id,
            military_status=military_status,
            branch=form_data.get('military_branch') or None,
            enlistment_date=form_data.get('military_start_date') or None,
            discharge_date=form_data.get('military_end_date') or None,
            rank=form_data.get('military_rank') or None,
            discharge_reason=form_data.get('military_discharge_reason') or None
        )
        military_repo.create(military)


def update_project_data(employee_id, form_data):
    """프로젝트정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_project_updater().update(employee_id, form_data)


def update_award_data(employee_id, form_data):
    """수상정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_award_updater().update(employee_id, form_data)
