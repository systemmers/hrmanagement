"""
Employee Service

법인 직원 관련 비즈니스 로직을 처리합니다.
- 직원 CRUD
- 관계형 데이터 (학력/경력/자격증/어학/병역/프로젝트/수상/가족) 관리
- 멀티테넌시 접근 제어

PersonalService와 동일한 아키텍처 패턴을 적용합니다.
Phase 2: Service 계층 표준화 - 조회 메서드 추가
Phase 4.2: SOLID 원칙 적용 - RelationDataUpdater 통합
Phase 24: Option A 레이어 분리 - Service는 Dict 반환 표준화
"""
from typing import Any, Dict, List, Optional, Tuple
from flask import request

from app.database import db
from app.models import Employee
from app.utils.transaction import atomic_transaction
from app.models.military_service import MilitaryService
from app.utils.tenant import get_current_organization_id
from app.extensions import (
    employee_repo, family_repo, education_repo, career_repo,
    certificate_repo, language_repo, military_repo,
    hr_project_repo, project_participation_repo, award_repo, attachment_repo,
    salary_repo, benefit_repo, contract_repo, salary_history_repo,
    promotion_repo, evaluation_repo, training_repo, attendance_repo,
    insurance_repo, asset_repo, salary_payment_repo, classification_repo
)
from app.services.base import relation_updater, get_relation_config, SUPPORTED_RELATION_TYPES


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
        self.salary_repo = salary_repo
        self.benefit_repo = benefit_repo
        self.contract_repo = contract_repo
        self.salary_history_repo = salary_history_repo
        self.promotion_repo = promotion_repo
        self.evaluation_repo = evaluation_repo
        self.training_repo = training_repo
        self.attendance_repo = attendance_repo
        self.insurance_repo = insurance_repo
        self.asset_repo = asset_repo
        self.salary_payment_repo = salary_payment_repo
        self.classification_repo = classification_repo

    def _get_repositories(self) -> Dict[str, Any]:
        """RelationDataUpdater용 Repository 딕셔너리 반환"""
        return {
            'education': self.education_repo,
            'career': self.career_repo,
            'certificate': self.certificate_repo,
            'language': self.language_repo,
            'family': self.family_repo,
            'award': self.award_repo,
            'project_participation': self.project_participation_repo,
        }

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

    def get_employee(self, employee_id: int) -> Optional[Dict]:
        """직원 조회 (접근 권한 확인 포함, Dict 반환)"""
        if not self.verify_access(employee_id):
            return None
        model = self.employee_repo.find_by_id(employee_id)
        return model.to_dict() if model else None

    def _get_employee_model(self, employee_id: int) -> Optional[Employee]:
        """내부용: Model이 필요한 경우 (수정/삭제 작업용)"""
        return self.employee_repo.find_by_id(employee_id)

    def get_employees_by_org(self, org_id: int = None) -> List[Employee]:
        """조직별 직원 목록 조회"""
        org_id = org_id or self.get_current_org_id()
        if not org_id:
            return []
        return self.employee_repo.get_by_company_id(org_id)

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict]:
        """직원 ID로 조회 (Dict 반환)

        Phase 24: find_by_id() + to_dict() 패턴 적용
        """
        model = self.employee_repo.find_by_id(employee_id)
        return model.to_dict() if model else None

    def get_employee_model_by_id(self, employee_id: int) -> Optional[Employee]:
        """직원 ID로 모델 조회 (템플릿 렌더링용)"""
        return self.employee_repo.find_by_id(employee_id)

    def filter_employees(self, **kwargs) -> List[Dict]:
        """직원 필터링 조회"""
        return self.employee_repo.filter_employees(**kwargs)

    def get_all_employees(self, organization_id: int = None) -> List[Dict]:
        """전체 직원 조회"""
        models = self.employee_repo.find_all(organization_id=organization_id)
        return [m.to_dict() for m in models]

    def verify_ownership(self, employee_id: int, org_id: int) -> bool:
        """직원 소유권 확인"""
        return self.employee_repo.verify_ownership(employee_id, org_id)

    # ========================================
    # 직원 CRUD (직접 호출 - Blueprint용)
    # ========================================

    def create_employee_direct(self, employee_data: Dict) -> Dict:
        """직원 생성 (Dict 데이터로 직접 생성)

        Args:
            employee_data: 직원 정보 Dict

        Returns:
            생성된 직원 Dict
        """
        return self.employee_repo.create(employee_data)

    def update_employee_direct(self, employee_id: int, employee: Any) -> Optional[Any]:
        """직원 수정 (모델 객체로 직접 수정)

        Args:
            employee_id: 직원 ID
            employee: Employee 모델 객체

        Returns:
            수정된 Employee 또는 None
        """
        return self.employee_repo.update(employee_id, employee)

    def update_employee_partial(self, employee_id: int, fields: Dict) -> Optional[Any]:
        """직원 부분 수정

        Args:
            employee_id: 직원 ID
            fields: 수정할 필드 Dict

        Returns:
            수정된 Employee 또는 None
        """
        return self.employee_repo.update_partial(employee_id, fields)

    def delete_employee_direct(self, employee_id: int) -> bool:
        """직원 삭제 (직접 호출)

        Args:
            employee_id: 직원 ID

        Returns:
            삭제 성공 여부
        """
        return self.employee_repo.delete(employee_id)

    # ========================================
    # 관계형 데이터 조회
    # ========================================

    def get_education_list(self, employee_id: int) -> List[Dict]:
        """학력 목록 조회"""
        models = self.education_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_career_list(self, employee_id: int) -> List[Dict]:
        """경력 목록 조회"""
        models = self.career_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_certificate_list(self, employee_id: int) -> List[Dict]:
        """자격증 목록 조회"""
        models = self.certificate_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_family_list(self, employee_id: int) -> List[Dict]:
        """가족 목록 조회"""
        models = self.family_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_language_list(self, employee_id: int) -> List[Dict]:
        """어학 목록 조회"""
        models = self.language_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_military_info(self, employee_id: int) -> Optional[Dict]:
        """병역 정보 조회"""
        model = self.military_repo.find_by_employee_id(employee_id)
        return model.to_dict() if model else None

    def get_salary_info(self, employee_id: int) -> Optional[Dict]:
        """급여 정보 조회"""
        model = self.salary_repo.find_by_employee_id(employee_id)
        return model.to_dict() if model else None

    def get_benefit_info(self, employee_id: int) -> Optional[Dict]:
        """복리후생 정보 조회"""
        model = self.benefit_repo.find_by_employee_id(employee_id)
        return model.to_dict() if model else None

    def get_contract_info(self, employee_id: int) -> Optional[Dict]:
        """계약 정보 조회"""
        model = self.contract_repo.find_by_employee_id(employee_id)
        return model.to_dict() if model else None

    def get_salary_history_list(self, employee_id: int) -> List[Dict]:
        """급여 이력 조회"""
        models = self.salary_history_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_promotion_list(self, employee_id: int) -> List[Dict]:
        """승진 이력 조회"""
        models = self.promotion_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_evaluation_list(self, employee_id: int) -> List[Dict]:
        """평가 이력 조회"""
        models = self.evaluation_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_training_list(self, employee_id: int) -> List[Dict]:
        """교육 이력 조회"""
        models = self.training_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_attendance_summary(self, employee_id: int, year: int) -> Optional[Dict]:
        """근태 요약 조회"""
        return self.attendance_repo.get_summary_by_employee(employee_id, year)

    def get_insurance_info(self, employee_id: int) -> Optional[Dict]:
        """보험 정보 조회"""
        model = self.insurance_repo.find_by_employee_id(employee_id)
        return model.to_dict() if model else None

    def get_hr_project_list(self, employee_id: int) -> List[Dict]:
        """인사 프로젝트 목록 조회"""
        models = self.hr_project_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_project_participation_list(self, employee_id: int) -> List[Dict]:
        """프로젝트 참여 목록 조회"""
        models = self.project_participation_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_award_list(self, employee_id: int) -> List[Dict]:
        """수상 목록 조회"""
        models = self.award_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_asset_list(self, employee_id: int) -> List[Dict]:
        """자산 목록 조회"""
        models = self.asset_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_salary_payment_list(self, employee_id: int) -> List[Dict]:
        """급여 지급 목록 조회"""
        models = self.salary_payment_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_attachment_list(self, employee_id: int) -> List[Dict]:
        """첨부파일 목록 조회"""
        models = self.attachment_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_attachment_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """카테고리별 첨부파일 조회"""
        return self.attachment_repo.get_one_by_category(employee_id, category)

    def get_classification_options(self) -> List[Dict]:
        """분류 옵션 조회"""
        models = self.classification_repo.find_all()
        return [m.to_dict() for m in models]

    def get_all_classification_options(self) -> Dict:
        """전체 분류 옵션 조회 (카테고리별)"""
        return self.classification_repo.get_all_options()

    # ========================================
    # 첨부파일 관리
    # ========================================

    def create_attachment(self, attachment_data: Dict) -> Dict:
        """첨부파일 생성"""
        return self.attachment_repo.create(attachment_data)

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict]:
        """첨부파일 ID로 조회"""
        model = self.attachment_repo.find_by_id(attachment_id)
        return model.to_dict() if model else None

    def delete_attachment(self, attachment_id: int) -> bool:
        """첨부파일 삭제"""
        return self.attachment_repo.delete(attachment_id)

    def delete_attachment_by_category(self, employee_id: int, category: str) -> bool:
        """카테고리별 첨부파일 삭제"""
        return self.attachment_repo.delete_by_category(employee_id, category)

    # ========================================
    # 병역 정보 관리
    # ========================================

    def delete_military_info(self, employee_id: int) -> bool:
        """병역 정보 삭제"""
        return self.military_repo.delete_by_employee_id(employee_id)

    def create_military_info(self, military_data) -> Any:
        """병역 정보 생성"""
        return self.military_repo.create(military_data)

    def create_employee(self, form_data: Dict) -> Tuple[bool, Optional[Employee], Optional[str]]:
        """직원 생성

        Returns:
            Tuple[성공여부, Employee객체, 에러메시지]
        """
        try:
            org_id = self.get_current_org_id()
            if not org_id:
                return False, None, "조직 정보를 찾을 수 없습니다."

            with atomic_transaction():
                employee = self._extract_employee_from_form(form_data)
                employee.company_id = org_id

                self.employee_repo.create(employee, commit=False)
                db.session.flush()

                # 관계형 데이터 업데이트
                self._update_all_related_data(employee.id, form_data)

            return True, employee, None

        except Exception as e:
            return False, None, str(e)

    def update_employee(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """직원 정보 수정

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                # 기본 필드 업데이트
                updated_employee = self._extract_employee_from_form(form_data, employee_id)
                self.employee_repo.update(employee, updated_employee, commit=False)

                # 관계형 데이터 업데이트
                self._update_all_related_data(employee_id, form_data)

            return True, None

        except Exception as e:
            return False, str(e)

    def delete_employee(self, employee_id: int) -> Tuple[bool, Optional[str]]:
        """직원 삭제

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            if not self.verify_access(employee_id):
                return False, "접근 권한이 없습니다."

            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                self.employee_repo.delete(employee, commit=False)

            return True, None

        except Exception as e:
            return False, str(e)

    # ========================================
    # 기본 정보만 수정 (Employee 역할용)
    # ========================================

    def update_basic_info(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """기본 정보만 수정 (연락처, 주소 등)"""
        try:
            employee = self._get_employee_model(employee_id)
            if not employee:
                return False, "직원을 찾을 수 없습니다."

            with atomic_transaction():
                basic_fields = self._extract_basic_fields(form_data)
                for key, value in basic_fields.items():
                    if hasattr(employee, key):
                        setattr(employee, key, value)

            return True, None

        except Exception as e:
            return False, str(e)

    # ========================================
    # 관계형 데이터 개별 수정 (RelationDataUpdater 사용)
    # ========================================

    def _update_relation(self, relation_type: str, employee_id: int,
                         form_data: Dict) -> Tuple[bool, Optional[str]]:
        """관계형 데이터 범용 수정 (내부 헬퍼)"""
        config = get_relation_config(relation_type, self._get_repositories())
        return relation_updater.update_with_commit(employee_id, form_data, config)

    def update_education(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """학력 정보 수정"""
        return self._update_relation('education', employee_id, form_data)

    def update_career(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """경력 정보 수정"""
        return self._update_relation('career', employee_id, form_data)

    def update_certificate(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """자격증 정보 수정"""
        return self._update_relation('certificate', employee_id, form_data)

    def update_language(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """어학 정보 수정"""
        return self._update_relation('language', employee_id, form_data)

    def update_military(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """병역 정보 수정 (특수 처리: 1:1 관계)"""
        try:
            with atomic_transaction():
                self._update_military_data(employee_id, form_data)
            return True, None
        except Exception as e:
            return False, str(e)

    def update_family(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """가족 정보 수정"""
        return self._update_relation('family', employee_id, form_data)

    def update_project(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """프로젝트 정보 수정"""
        return self._update_relation('project_participation', employee_id, form_data)

    def update_award(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """수상 정보 수정"""
        return self._update_relation('award', employee_id, form_data)

    # ========================================
    # Private: 폼 데이터 처리
    # ========================================

    def _extract_employee_from_form(self, form_data: Dict, employee_id: int = 0) -> Employee:
        """폼 데이터에서 Employee 객체 생성"""
        org_id = form_data.get('organization_id')
        organization_id = int(org_id) if org_id and str(org_id).strip() else None

        # 수정 시 기존 employee의 company_id, organization_id 보존 (중요: 손실 방지)
        company_id = None
        if employee_id:
            existing = db.session.get(Employee, employee_id)
            if existing:
                company_id = existing.company_id
                # organization_id가 폼에 없으면 기존 값 보존
                if not organization_id:
                    organization_id = existing.organization_id

        return Employee(
            company_id=company_id,
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
    # Private: 관계형 데이터 업데이트 (RelationDataUpdater 사용)
    # ========================================

    def _update_all_related_data(self, employee_id: int, form_data: Dict):
        """모든 관계형 데이터 일괄 업데이트

        RelationDataUpdater를 사용하여 7개 관계 타입을 처리합니다.
        병역 정보는 1:1 관계이므로 별도 처리합니다.
        """
        repos = self._get_repositories()

        # 1:N 관계 데이터 일괄 처리
        for relation_type in SUPPORTED_RELATION_TYPES:
            config = get_relation_config(relation_type, repos)
            relation_updater.update(employee_id, form_data, config)

        # 1:1 관계 (병역) 별도 처리
        self._update_military_data(employee_id, form_data)

    def _update_military_data(self, employee_id: int, form_data: Dict):
        """병역 정보 업데이트 (1:1 관계, 특수 처리)"""
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

    # ========================================
    # 대시보드용 메서드
    # ========================================

    def get_dashboard_data(self, employee_id: int) -> Optional[Dict]:
        """직원 대시보드 데이터 조회

        Args:
            employee_id: 직원 ID

        Returns:
            대시보드용 데이터 Dict 또는 None
        """
        from datetime import date

        employee = self.employee_repo.find_by_id(employee_id)
        if not employee:
            return None

        # 이력 통계 (lazy relationship은 list()로 변환 후 len() 사용)
        stats = {
            'education_count': len(list(employee.educations)) if employee.educations else 0,
            'career_count': len(list(employee.careers)) if employee.careers else 0,
            'certificate_count': len(list(employee.certificates)) if employee.certificates else 0,
            'language_count': len(list(employee.languages)) if employee.languages else 0,
        }

        # 근속년수 계산
        years_of_service = 0
        if employee.hire_date:
            try:
                hire_date = employee.hire_date
                if isinstance(hire_date, str):
                    from datetime import datetime
                    hire_date = datetime.strptime(hire_date, '%Y-%m-%d').date()
                today = date.today()
                years_of_service = (today - hire_date).days // 365
            except (ValueError, TypeError):
                years_of_service = 0

        # 근무 정보
        work_info = {
            'hire_date': employee.hire_date,
            'years_of_service': years_of_service,
            'status': employee.status,
            'department': employee.department,
            'position': employee.position,
        }

        return {
            'employee': employee,
            'stats': stats,
            'work_info': work_info,
        }

    # ========================================
    # 통계/검색용 메서드 (main.py용)
    # ========================================

    def get_statistics(self, organization_id: int = None) -> Dict:
        """직원 통계 조회"""
        return self.employee_repo.get_statistics(organization_id=organization_id)

    def get_department_statistics(self, organization_id: int = None) -> List[Dict]:
        """부서별 통계 조회"""
        return self.employee_repo.get_department_statistics(organization_id=organization_id)

    def get_recent_employees(self, organization_id: int = None, limit: int = 5) -> List[Dict]:
        """최근 입사 직원 조회"""
        return self.employee_repo.get_recent_employees(limit=limit, organization_id=organization_id)

    def search_employees(self, query: str, organization_id: int = None) -> List[Dict]:
        """직원 검색"""
        return self.employee_repo.search(query, organization_id=organization_id)


# 싱글턴 인스턴스
employee_service = EmployeeService()
