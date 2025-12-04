"""
직원 관리 헬퍼 함수

폼 데이터 처리, 관계형 데이터 업데이트 등 공통 헬퍼 함수를 제공합니다.
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


# ========================================
# 파일 업로드 설정
# ========================================

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'gif', 'doc', 'docx', 'xls', 'xlsx'}
ALLOWED_IMAGE_EXTENSIONS = {'jpg', 'jpeg', 'png', 'gif', 'webp'}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB
MAX_IMAGE_SIZE = 5 * 1024 * 1024  # 5MB


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
# 파일 유틸리티 함수
# ========================================

def allowed_file(filename):
    """허용된 파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def allowed_image_file(filename):
    """허용된 이미지 파일 확장자 검사"""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_IMAGE_EXTENSIONS


def get_file_extension(filename):
    """파일 확장자 추출"""
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else ''


def get_upload_folder():
    """업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'attachments')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_profile_photo_folder():
    """프로필 사진 업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'profile_photos')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def get_business_card_folder():
    """명함 이미지 업로드 폴더 경로 반환 및 생성"""
    upload_folder = os.path.join(current_app.root_path, 'static', 'uploads', 'business_cards')
    os.makedirs(upload_folder, exist_ok=True)
    return upload_folder


def generate_unique_filename(employee_id, original_filename, prefix=''):
    """고유한 파일명 생성"""
    filename = secure_filename(original_filename)
    ext = get_file_extension(filename)
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    if prefix:
        return f"{employee_id}_{prefix}_{timestamp}.{ext}"
    return f"{employee_id}_{timestamp}_{filename}"


def delete_file_if_exists(file_path):
    """파일이 존재하면 삭제"""
    if file_path:
        full_path = os.path.join(current_app.root_path, file_path.lstrip('/'))
        if os.path.exists(full_path):
            os.remove(full_path)
            return True
    return False


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
# 관계형 데이터 업데이트 헬퍼 함수
# ========================================

def update_family_data(employee_id, form_data):
    """가족정보 업데이트"""
    from ...models import Family

    # 기존 데이터 삭제 후 새로 입력
    family_repo.delete_by_employee_id(employee_id)

    # 폼에서 가족정보 추출
    relations = form_data.getlist('family_relation[]')
    names = form_data.getlist('family_name[]')
    birth_dates = form_data.getlist('family_birth_date[]')
    occupations = form_data.getlist('family_occupation[]')
    phones = form_data.getlist('family_phone[]')
    cohabitings = form_data.getlist('family_cohabiting[]')

    for i in range(len(relations)):
        if relations[i] and names[i]:  # 필수 필드가 있는 경우만
            family = Family(
                employee_id=employee_id,
                relation=relations[i],
                name=names[i],
                birth_date=birth_dates[i] if i < len(birth_dates) else None,
                occupation=occupations[i] if i < len(occupations) else None,
                phone=phones[i] if i < len(phones) else None,
                cohabiting=cohabitings[i] if i < len(cohabitings) else None
            )
            family_repo.create(family)


def update_education_data(employee_id, form_data):
    """학력정보 업데이트"""
    from ...models import Education

    education_repo.delete_by_employee_id(employee_id)

    school_types = form_data.getlist('education_school_type[]')
    school_names = form_data.getlist('education_school_name[]')
    graduation_years = form_data.getlist('education_graduation_year[]')
    majors = form_data.getlist('education_major[]')
    degrees = form_data.getlist('education_degree[]')
    gpas = form_data.getlist('education_gpa[]')
    graduation_statuses = form_data.getlist('education_graduation_status[]')

    for i in range(len(school_names)):
        if school_names[i]:
            education = Education(
                employee_id=employee_id,
                school_type=school_types[i] if i < len(school_types) else None,
                school_name=school_names[i],
                graduation_year=graduation_years[i] if i < len(graduation_years) else None,
                major=majors[i] if i < len(majors) else None,
                degree=degrees[i] if i < len(degrees) else None,
                gpa=gpas[i] if i < len(gpas) else None,
                graduation_status=graduation_statuses[i] if i < len(graduation_statuses) else None
            )
            education_repo.create(education)


def update_career_data(employee_id, form_data):
    """경력정보 업데이트"""
    from ...models import Career

    career_repo.delete_by_employee_id(employee_id)

    company_names = form_data.getlist('career_company_name[]')
    start_dates = form_data.getlist('career_start_date[]')
    end_dates = form_data.getlist('career_end_date[]')
    departments = form_data.getlist('career_department[]')
    positions = form_data.getlist('career_position[]')
    duties = form_data.getlist('career_duties[]')

    for i in range(len(company_names)):
        if company_names[i]:
            career = Career(
                employee_id=employee_id,
                company_name=company_names[i],
                start_date=start_dates[i] if i < len(start_dates) else None,
                end_date=end_dates[i] if i < len(end_dates) else None,
                department=departments[i] if i < len(departments) else None,
                position=positions[i] if i < len(positions) else None,
                duties=duties[i] if i < len(duties) else None
            )
            career_repo.create(career)


def update_certificate_data(employee_id, form_data):
    """자격증정보 업데이트"""
    from ...models import Certificate

    certificate_repo.delete_by_employee_id(employee_id)

    cert_types = form_data.getlist('certificate_type[]')
    cert_names = form_data.getlist('certificate_name[]')
    cert_grades = form_data.getlist('certificate_grade[]')
    cert_issuers = form_data.getlist('certificate_issuer[]')
    cert_dates = form_data.getlist('certificate_date[]')

    for i in range(len(cert_names)):
        if cert_names[i]:
            certificate = Certificate(
                employee_id=employee_id,
                cert_type=cert_types[i] if i < len(cert_types) else None,
                cert_name=cert_names[i],
                grade=cert_grades[i] if i < len(cert_grades) else None,
                issuer=cert_issuers[i] if i < len(cert_issuers) else None,
                acquisition_date=cert_dates[i] if i < len(cert_dates) else None
            )
            certificate_repo.create(certificate)


def update_language_data(employee_id, form_data):
    """언어능력정보 업데이트"""
    from ...models import Language

    language_repo.delete_by_employee_id(employee_id)

    languages = form_data.getlist('language_name[]')
    levels = form_data.getlist('language_level[]')
    test_names = form_data.getlist('language_test_name[]')
    scores = form_data.getlist('language_score[]')
    test_dates = form_data.getlist('language_test_date[]')

    for i in range(len(languages)):
        if languages[i]:
            language = Language(
                employee_id=employee_id,
                language=languages[i],
                level=levels[i] if i < len(levels) else None,
                test_name=test_names[i] if i < len(test_names) else None,
                score=scores[i] if i < len(scores) else None,
                test_date=test_dates[i] if i < len(test_dates) else None
            )
            language_repo.create(language)


def update_military_data(employee_id, form_data):
    """병역정보 업데이트"""
    from ...models import Military

    military_repo.delete_by_employee_id(employee_id)

    military_status = form_data.get('military_status')
    if military_status:
        military = Military(
            employee_id=employee_id,
            military_status=military_status,
            branch=form_data.get('military_branch') or None,
            start_date=form_data.get('military_start_date') or None,
            end_date=form_data.get('military_end_date') or None,
            rank=form_data.get('military_rank') or None,
            specialty=form_data.get('military_specialty') or None,
            discharge_reason=form_data.get('military_discharge_reason') or None
        )
        military_repo.create(military)


def update_project_data(employee_id, form_data):
    """프로젝트정보 업데이트"""
    from ...models import Project

    project_repo.delete_by_employee_id(employee_id)

    project_names = form_data.getlist('project_name[]')
    start_dates = form_data.getlist('project_start_date[]')
    end_dates = form_data.getlist('project_end_date[]')
    duties = form_data.getlist('project_duties[]')
    roles = form_data.getlist('project_role[]')
    clients = form_data.getlist('project_client[]')

    for i in range(len(project_names)):
        if project_names[i]:
            project = Project(
                employee_id=employee_id,
                project_name=project_names[i],
                start_date=start_dates[i] if i < len(start_dates) else None,
                end_date=end_dates[i] if i < len(end_dates) else None,
                duties=duties[i] if i < len(duties) else None,
                role=roles[i] if i < len(roles) else None,
                client=clients[i] if i < len(clients) else None
            )
            project_repo.create(project)


def update_award_data(employee_id, form_data):
    """수상정보 업데이트"""
    from ...models import Award

    award_repo.delete_by_employee_id(employee_id)

    award_dates = form_data.getlist('award_date[]')
    award_names = form_data.getlist('award_name[]')
    award_issuers = form_data.getlist('award_issuer[]')
    award_notes = form_data.getlist('award_note[]')

    for i in range(len(award_names)):
        if award_names[i]:
            award = Award(
                employee_id=employee_id,
                award_date=award_dates[i] if i < len(award_dates) else None,
                award_name=award_names[i],
                issuer=award_issuers[i] if i < len(award_issuers) else None,
                note=award_notes[i] if i < len(award_notes) else None
            )
            award_repo.create(award)
