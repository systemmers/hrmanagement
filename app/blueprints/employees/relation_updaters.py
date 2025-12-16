"""
관계형 데이터 업데이트 함수

직원의 가족, 학력, 경력, 자격증 등 관계형 데이터 업데이트를 처리합니다.
"""
from ...extensions import (
    family_repo, education_repo, career_repo,
    certificate_repo, language_repo, military_repo,
    hr_project_repo, project_participation_repo, award_repo
)


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

    def parse_living_together(value):
        """living_together 값을 boolean으로 변환"""
        if value is None or value == '':
            return False
        return value == 'true' or value is True

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
            'living_together': 'is_cohabitant',
        },
        converters={'is_cohabitant': parse_living_together}
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
            'gpa': 'gpa',
            'note': 'note',
        }
    )


def _get_career_updater():
    """경력정보 Updater 생성"""
    from ...models import Career

    def parse_int(value):
        """정수 값으로 변환"""
        if value is None or value == '':
            return None
        try:
            return int(value)
        except (ValueError, TypeError):
            return None

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
            # 직급 체계
            'position': 'position',  # 직위
            'job_grade': 'job_grade',  # 직급
            'job_title': 'job_title',  # 직책
            'job_role': 'job_role',  # 직무
            'duties': 'job_description',  # 담당업무 상세
            # 급여 체계
            'salary': 'salary',  # 연봉
            'salary_type': 'salary_type',  # 급여유형
            'monthly_salary': 'monthly_salary',  # 월급
            'pay_step': 'pay_step',  # 호봉
        },
        converters={
            'salary': parse_int,
            'monthly_salary': parse_int,
            'pay_step': parse_int,
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
            'expiry_date': 'expiry_date',
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
            'name': 'language_name',
            'level': 'level',
            'test_name': 'exam_name',
            'score': 'score',
            'test_date': 'acquisition_date',
        }
    )


def _get_hr_project_updater():
    """인사이력 프로젝트 Updater 생성"""
    from ...models import HrProject
    return RelatedDataUpdater(
        model_class=HrProject,
        repository=hr_project_repo,
        form_prefix='hr_project_',
        required_field='name',
        field_mapping={
            'name': 'project_name',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'duty': 'duty',
            'role': 'role',
            'client': 'client',
        }
    )


def _get_project_participation_updater():
    """프로젝트 참여이력 Updater 생성"""
    from ...models import ProjectParticipation
    return RelatedDataUpdater(
        model_class=ProjectParticipation,
        repository=project_participation_repo,
        form_prefix='participation_',
        required_field='project_name',
        field_mapping={
            'project_name': 'project_name',
            'start_date': 'start_date',
            'end_date': 'end_date',
            'duty': 'duty',
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


def update_hr_project_data(employee_id, form_data):
    """인사이력 프로젝트 업데이트 (RelatedDataUpdater 사용)"""
    _get_hr_project_updater().update(employee_id, form_data)


def update_project_participation_data(employee_id, form_data):
    """프로젝트 참여이력 업데이트 (RelatedDataUpdater 사용)"""
    _get_project_participation_updater().update(employee_id, form_data)


def update_award_data(employee_id, form_data):
    """수상정보 업데이트 (RelatedDataUpdater 사용)"""
    _get_award_updater().update(employee_id, form_data)
