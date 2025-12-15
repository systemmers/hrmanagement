"""
Employee Service

법인 직원 관련 비즈니스 로직을 처리합니다.
- 직원 CRUD
- 관계형 데이터 (학력/경력/자격증/어학/병역/프로젝트/수상/가족) 관리
- 멀티테넌시 접근 제어

PersonalService와 동일한 아키텍처 패턴을 적용합니다.
"""
from typing import Dict, Optional, Tuple, List, Any
from flask import request

from app.database import db
from app.models import Employee
from app.utils.tenant import get_current_organization_id
from app.extensions import (
    employee_repo, family_repo, education_repo, career_repo,
    certificate_repo, language_repo, military_repo,
    hr_project_repo, project_participation_repo, award_repo, attachment_repo
)


class EmployeeService:
    """법인 직원 서비스"""

    def __init__(self):
        self.employee_repo = employee_repo
        self.family_repo = family_repo
        self.education_repo = education_repo
        self.career_repo = career_repo
        self.certificate_repo = certificate_repo
        self.language_repo = language_repo
        self.military_repo = military_repo
        self.hr_project_repo = hr_project_repo
        self.project_participation_repo = project_participation_repo
        self.award_repo = award_repo
        self.attachment_repo = attachment_repo

    # ========================================
    # 멀티테넌시 접근 제어
    # ========================================

    def get_current_org_id(self) -> Optional[int]:
        """현재 조직 ID 반환"""
        return get_current_organization_id()

    def verify_access(self, employee_id: int) -> bool:
        """현재 회사가 해당 직원에 접근 가능한지 확인"""
        org_id = self.get_current_org_id()
        if not org_id:
            return False
        return self.employee_repo.verify_ownership(employee_id, org_id)

    # ========================================
    # 직원 CRUD
    # ========================================

    def get_employee(self, employee_id: int) -> Optional[Employee]:
        """직원 조회 (접근 권한 확인 포함)"""
        if not self.verify_access(employee_id):
            return None
        return self.employee_repo.get_by_id(employee_id)

    def get_employees_by_org(self, org_id: int = None) -> List[Employee]:
        """조직별 직원 목록 조회"""
        org_id = org_id or self.get_current_org_id()
        if not org_id:
            return []
        return self.employee_repo.get_by_company_id(org_id)

    def create_employee(self, form_data: Dict) -> Tuple[bool, Optional[Employee], Optional[str]]:
        """직원 생성

        Returns:
            Tuple[성공여부, Employee객체, 에러메시지]
        """
        try:
            org_id = self.get_current_org_id()
            if not org_id:
                return False, None, "조직 정보를 찾을 수 없습니다."

            employee = self._extract_employee_from_form(form_data)
            employee.company_id = org_id

            self.employee_repo.create(employee)
            db.session.flush()

            # 관계형 데이터 업데이트
            self._update_all_related_data(employee.id, form_data)

            return True, employee, None

        except Exception as e:
            db.session.rollback()
            return False, None, str(e)

    def update_employee(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """직원 정보 수정

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            # 기본 필드 업데이트
            updated_employee = self._extract_employee_from_form(form_data, employee_id)
            self.employee_repo.update(employee, updated_employee)

            # 관계형 데이터 업데이트
            self._update_all_related_data(employee_id, form_data)

            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def delete_employee(self, employee_id: int) -> Tuple[bool, Optional[str]]:
        """직원 삭제

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            self.employee_repo.delete(employee)
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # 기본 정보만 수정 (Employee 역할용)
    # ========================================

    def update_basic_info(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """기본 정보만 수정 (연락처, 주소 등)"""
        try:
            employee = self.employee_repo.get_by_id(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            basic_fields = self._extract_basic_fields(form_data)
            for key, value in basic_fields.items():
                if hasattr(employee, key):
                    setattr(employee, key, value)

            db.session.commit()
            return True, None

        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # 관계형 데이터 개별 수정
    # ========================================

    def update_education(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """학력 정보 수정"""
        try:
            self._update_education_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_career(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """경력 정보 수정"""
        try:
            self._update_career_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_certificate(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """자격증 정보 수정"""
        try:
            self._update_certificate_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_language(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """어학 정보 수정"""
        try:
            self._update_language_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_military(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """병역 정보 수정"""
        try:
            self._update_military_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_family(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """가족 정보 수정"""
        try:
            self._update_family_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_project(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """프로젝트 정보 수정"""
        try:
            self._update_project_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    def update_award(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """수상 정보 수정"""
        try:
            self._update_award_data(employee_id, form_data)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)

    # ========================================
    # Private: 폼 데이터 처리
    # ========================================

    def _extract_employee_from_form(self, form_data: Dict, employee_id: int = 0) -> Employee:
        """폼 데이터에서 Employee 객체 생성"""
        org_id = form_data.get('organization_id')
        organization_id = int(org_id) if org_id and str(org_id).strip() else None

        return Employee(
            id=employee_id,
            name=form_data.get('name', ''),
            photo=form_data.get('photo') or '/static/images/face/face_01_m.png',
            department=form_data.get('department', ''),
            position=form_data.get('position', ''),
            status=form_data.get('status', 'active'),
            hire_date=form_data.get('hire_date') or form_data.get('hireDate', ''),
            phone=form_data.get('phone', ''),
            email=form_data.get('email', ''),
            organization_id=organization_id,
            employee_number=form_data.get('employee_number') or None,
            team=form_data.get('team') or None,
            job_title=form_data.get('job_title') or None,
            work_location=form_data.get('work_location') or None,
            internal_phone=form_data.get('internal_phone') or None,
            company_email=form_data.get('company_email') or None,
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

    def _extract_basic_fields(self, form_data: Dict) -> Dict:
        """기본 정보 필드만 추출"""
        return {
            'name': form_data.get('name', ''),
            'english_name': form_data.get('english_name') or None,
            'birth_date': form_data.get('birth_date') or None,
            'gender': form_data.get('gender') or None,
            'phone': form_data.get('phone', ''),
            'email': form_data.get('email', ''),
            'mobile_phone': form_data.get('mobile_phone') or None,
            'home_phone': form_data.get('home_phone') or None,
            'address': form_data.get('address') or None,
            'detailed_address': form_data.get('detailed_address') or None,
            'postal_code': form_data.get('postal_code') or None,
            'nationality': form_data.get('nationality') or None,
            'blood_type': form_data.get('blood_type') or None,
            'religion': form_data.get('religion') or None,
            'hobby': form_data.get('hobby') or None,
            'specialty': form_data.get('specialty') or None,
        }

    # ========================================
    # Private: 관계형 데이터 업데이트
    # ========================================

    def _update_all_related_data(self, employee_id: int, form_data: Dict):
        """모든 관계형 데이터 일괄 업데이트"""
        self._update_family_data(employee_id, form_data)
        self._update_education_data(employee_id, form_data)
        self._update_career_data(employee_id, form_data)
        self._update_certificate_data(employee_id, form_data)
        self._update_language_data(employee_id, form_data)
        self._update_military_data(employee_id, form_data)
        self._update_project_data(employee_id, form_data)
        self._update_award_data(employee_id, form_data)

    def _update_family_data(self, employee_id: int, form_data: Dict):
        """가족 정보 업데이트"""
        from app.models import FamilyMember
        self._update_related_data(
            employee_id, form_data,
            model_class=FamilyMember,
            repository=self.family_repo,
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

    def _update_education_data(self, employee_id: int, form_data: Dict):
        """학력 정보 업데이트"""
        from app.models import Education
        self._update_related_data(
            employee_id, form_data,
            model_class=Education,
            repository=self.education_repo,
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

    def _update_career_data(self, employee_id: int, form_data: Dict):
        """경력 정보 업데이트"""
        from app.models import Career
        self._update_related_data(
            employee_id, form_data,
            model_class=Career,
            repository=self.career_repo,
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

    def _update_certificate_data(self, employee_id: int, form_data: Dict):
        """자격증 정보 업데이트"""
        from app.models import Certificate
        self._update_related_data(
            employee_id, form_data,
            model_class=Certificate,
            repository=self.certificate_repo,
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

    def _update_language_data(self, employee_id: int, form_data: Dict):
        """어학 정보 업데이트"""
        from app.models import Language
        self._update_related_data(
            employee_id, form_data,
            model_class=Language,
            repository=self.language_repo,
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

    def _update_military_data(self, employee_id: int, form_data: Dict):
        """병역 정보 업데이트"""
        from app.models import MilitaryService
        self.military_repo.delete_by_employee_id(employee_id)

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
            self.military_repo.create(military)

    def _update_project_data(self, employee_id: int, form_data: Dict):
        """프로젝트 정보 업데이트"""
        from app.models import Project
        self._update_related_data(
            employee_id, form_data,
            model_class=Project,
            repository=self.project_repo,
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

    def _update_award_data(self, employee_id: int, form_data: Dict):
        """수상 정보 업데이트"""
        from app.models import Award
        self._update_related_data(
            employee_id, form_data,
            model_class=Award,
            repository=self.award_repo,
            form_prefix='award_',
            required_field='name',
            field_mapping={
                'date': 'award_date',
                'name': 'award_name',
                'issuer': 'issuer',
                'note': 'note',
            }
        )

    def _update_related_data(self, employee_id: int, form_data: Dict,
                             model_class, repository, form_prefix: str,
                             required_field: str, field_mapping: Dict,
                             converters: Dict = None):
        """관계형 데이터 범용 업데이트"""
        converters = converters or {}

        # 기존 데이터 삭제
        repository.delete_by_employee_id(employee_id)

        # 폼 데이터 추출
        form_lists = {}
        for field_suffix in field_mapping.keys():
            form_key = f"{form_prefix}{field_suffix}[]"
            form_lists[field_suffix] = form_data.getlist(form_key)

        # 필수 필드 리스트를 기준으로 반복
        required_values = form_lists.get(required_field, [])

        for i in range(len(required_values)):
            if required_values[i]:
                model_data = {'employee_id': employee_id}

                for field_suffix, model_attr in field_mapping.items():
                    values = form_lists.get(field_suffix, [])
                    value = values[i] if i < len(values) else None

                    if model_attr in converters and value is not None:
                        value = converters[model_attr](value)

                    model_data[model_attr] = value

                instance = model_class(**model_data)
                repository.create(instance)


# 싱글턴 인스턴스
employee_service = EmployeeService()
