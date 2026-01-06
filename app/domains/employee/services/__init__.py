"""
Employee Service Package

EmployeeService Facade를 제공하여 기존 API 100% 호환성을 유지합니다.
내부적으로 EmployeeCoreService와 EmployeeRelationService에 위임합니다.

Phase 3: EmployeeService 분리 - Facade 패턴

사용법:
    # 기존과 동일한 방식으로 사용
    from app.services.employee_service import employee_service
    employee_service.get_employee(1)

    # 새로운 방식 (분리된 서비스 직접 사용)
    from . import employee_core_service, employee_relation_service
    employee_core_service.get_employee(1)
    employee_relation_service.get_education_list(1)
"""
from typing import Any, Dict, List, Optional, Tuple

from app.domains.employee.models import Employee

from .employee_core_service import EmployeeCoreService, employee_core_service
from .employee_relation_service import EmployeeRelationService, employee_relation_service


class EmployeeService:
    """
    Facade - 기존 EmployeeService API 100% 유지

    내부적으로 분리된 서비스에 위임합니다:
    - core: 직원 기본 CRUD, 멀티테넌시
    - relation: 관계형 데이터 조회/수정
    """

    def __init__(self):
        self.core = EmployeeCoreService()
        self.relation = EmployeeRelationService()

    # ========================================
    # Repository Properties (하위 호환성)
    # ========================================

    @property
    def employee_repo(self):
        return self.core.employee_repo

    @property
    def family_repo(self):
        return self.relation.family_repo

    @property
    def education_repo(self):
        return self.relation.education_repo

    @property
    def career_repo(self):
        return self.relation.career_repo

    @property
    def certificate_repo(self):
        return self.relation.certificate_repo

    @property
    def language_repo(self):
        return self.relation.language_repo

    @property
    def military_repo(self):
        return self.relation.military_repo

    @property
    def hr_project_repo(self):
        return self.relation.hr_project_repo

    @property
    def project_participation_repo(self):
        return self.relation.project_participation_repo

    @property
    def award_repo(self):
        return self.relation.award_repo

    @property
    def attachment_repo(self):
        return self.relation.attachment_repo

    @property
    def salary_repo(self):
        return self.relation.salary_repo

    @property
    def benefit_repo(self):
        return self.relation.benefit_repo

    @property
    def contract_repo(self):
        return self.relation.contract_repo

    @property
    def salary_history_repo(self):
        return self.relation.salary_history_repo

    @property
    def promotion_repo(self):
        return self.relation.promotion_repo

    @property
    def evaluation_repo(self):
        return self.relation.evaluation_repo

    @property
    def training_repo(self):
        return self.relation.training_repo

    @property
    def attendance_repo(self):
        return self.relation.attendance_repo

    @property
    def insurance_repo(self):
        return self.relation.insurance_repo

    @property
    def asset_repo(self):
        return self.relation.asset_repo

    @property
    def salary_payment_repo(self):
        return self.relation.salary_payment_repo

    @property
    def classification_repo(self):
        return self.relation.classification_repo

    def _get_repositories(self) -> Dict[str, Any]:
        """RelationDataUpdater용 Repository 딕셔너리 반환"""
        return self.relation._get_repositories()

    # ========================================
    # 멀티테넌시 접근 제어 (Core에 위임)
    # ========================================

    def get_current_org_id(self) -> Optional[int]:
        return self.core.get_current_org_id()

    def verify_access(self, employee_id: int) -> bool:
        return self.core.verify_access(employee_id)

    def verify_ownership(self, employee_id: int, org_id: int) -> bool:
        return self.core.verify_ownership(employee_id, org_id)

    # ========================================
    # 직원 조회 (Core에 위임)
    # ========================================

    def get_employee(self, employee_id: int) -> Optional[Dict]:
        return self.core.get_employee(employee_id)

    def _get_employee_model(self, employee_id: int) -> Optional[Employee]:
        return self.core._get_employee_model(employee_id)

    def get_employees_by_org(self, org_id: int = None) -> List[Employee]:
        return self.core.get_employees_by_org(org_id)

    def get_employee_by_id(self, employee_id: int) -> Optional[Dict]:
        return self.core.get_employee_by_id(employee_id)

    def get_employee_model_by_id(self, employee_id: int) -> Optional[Employee]:
        return self.core.get_employee_model_by_id(employee_id)

    def filter_employees(self, **kwargs) -> List[Dict]:
        return self.core.filter_employees(**kwargs)

    def get_all_employees(self, organization_id: int = None) -> List[Dict]:
        return self.core.get_all_employees(organization_id)

    def get_employees_by_ids(self, employee_ids: List[int]) -> List[Dict]:
        return self.core.get_employees_by_ids(employee_ids)

    # ========================================
    # 직원 CRUD (Core에 위임)
    # ========================================

    def create_employee_direct(self, employee_data: Dict) -> Dict:
        return self.core.create_employee_direct(employee_data)

    def update_employee_direct(self, employee_id: int, employee: Any) -> Optional[Any]:
        return self.core.update_employee_direct(employee_id, employee)

    def update_employee_partial(self, employee_id: int, fields: Dict) -> Optional[Any]:
        return self.core.update_employee_partial(employee_id, fields)

    def delete_employee_direct(self, employee_id: int) -> bool:
        return self.core.delete_employee_direct(employee_id)

    def create_employee(self, form_data: Dict) -> Tuple[bool, Optional[Employee], Optional[str]]:
        """직원 생성 (관계형 데이터 포함)"""
        return self.core.create_employee(
            form_data,
            relation_updater_callback=self._update_all_related_data
        )

    def update_employee(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        """직원 수정 (관계형 데이터 포함)"""
        return self.core.update_employee(
            employee_id,
            form_data,
            relation_updater_callback=self._update_all_related_data
        )

    def delete_employee(self, employee_id: int) -> Tuple[bool, Optional[str]]:
        return self.core.delete_employee(employee_id)

    def update_basic_info(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.core.update_basic_info(employee_id, form_data)

    # ========================================
    # 통계/검색 (Core에 위임)
    # ========================================

    def get_statistics(self, organization_id: int = None) -> Dict:
        return self.core.get_statistics(organization_id)

    def get_department_statistics(self, organization_id: int = None) -> List[Dict]:
        return self.core.get_department_statistics(organization_id)

    def get_recent_employees(self, organization_id: int = None, limit: int = 5) -> List[Dict]:
        return self.core.get_recent_employees(organization_id, limit)

    def search_employees(self, query: str, organization_id: int = None) -> List[Dict]:
        return self.core.search_employees(query, organization_id)

    def get_employees_with_contracts(
        self,
        employees: List[Dict],
        company_id: int
    ) -> List[Dict]:
        """직원 목록에 계약 정보 추가 (Core에 위임)"""
        return self.core.get_employees_with_contracts(employees, company_id)

    # ========================================
    # 관계형 데이터 조회 (Relation에 위임)
    # ========================================

    def get_education_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_education_list(employee_id)

    def get_career_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_career_list(employee_id)

    def get_certificate_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_certificate_list(employee_id)

    def get_family_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_family_list(employee_id)

    def get_language_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_language_list(employee_id)

    def get_military_info(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_military_info(employee_id)

    def get_salary_info(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_salary_info(employee_id)

    def get_benefit_info(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_benefit_info(employee_id)

    def get_contract_info(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_contract_info(employee_id)

    def get_salary_history_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_salary_history_list(employee_id)

    def get_promotion_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_promotion_list(employee_id)

    def get_evaluation_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_evaluation_list(employee_id)

    def get_training_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_training_list(employee_id)

    def get_attendance_summary(self, employee_id: int, year: int) -> Optional[Dict]:
        return self.relation.get_attendance_summary(employee_id, year)

    def get_insurance_info(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_insurance_info(employee_id)

    def save_insurance_data(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """4대보험 데이터 저장 (Phase 28: upsert)"""
        return self.relation.save_insurance_data(employee_id, data, commit=commit)

    def get_hr_project_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_hr_project_list(employee_id)

    def get_project_participation_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_project_participation_list(employee_id)

    def get_award_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_award_list(employee_id)

    def get_asset_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_asset_list(employee_id)

    def get_salary_payment_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_salary_payment_list(employee_id)

    def get_attachment_list(self, employee_id: int) -> List[Dict]:
        return self.relation.get_attachment_list(employee_id)

    def get_attachment_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        return self.relation.get_attachment_by_category(employee_id, category)

    def get_classification_options(self) -> List[Dict]:
        return self.relation.get_classification_options()

    def get_all_classification_options(self, company_id: int = None) -> Dict:
        return self.relation.get_all_classification_options(company_id)

    # ========================================
    # 첨부파일 관리 (Relation에 위임)
    # ========================================

    def create_attachment(self, attachment_data: Dict) -> Dict:
        return self.relation.create_attachment(attachment_data)

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict]:
        return self.relation.get_attachment_by_id(attachment_id)

    def delete_attachment(self, attachment_id: int) -> bool:
        return self.relation.delete_attachment(attachment_id)

    def delete_attachment_by_category(self, employee_id: int, category: str) -> bool:
        return self.relation.delete_attachment_by_category(employee_id, category)

    # ========================================
    # 병역 정보 관리 (Relation에 위임)
    # ========================================

    def delete_military_info(self, employee_id: int) -> bool:
        return self.relation.delete_military_info(employee_id)

    def create_military_info(self, military_data) -> Any:
        return self.relation.create_military_info(military_data)

    # ========================================
    # 관계형 데이터 수정 (Relation에 위임)
    # ========================================

    def update_education(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_education(employee_id, form_data)

    def update_career(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_career(employee_id, form_data)

    def update_certificate(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_certificate(employee_id, form_data)

    def update_language(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_language(employee_id, form_data)

    def update_military(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_military(employee_id, form_data)

    def update_family(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_family(employee_id, form_data)

    def update_project(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_project(employee_id, form_data)

    def update_award(self, employee_id: int, form_data: Dict) -> Tuple[bool, Optional[str]]:
        return self.relation.update_award(employee_id, form_data)

    # ========================================
    # 관계형 데이터 일괄 업데이트 (내부용)
    # ========================================

    def _update_all_related_data(self, employee_id: int, form_data: Dict):
        """모든 관계형 데이터 일괄 업데이트"""
        self.relation.update_all_related_data(employee_id, form_data)

    def _update_military_data(self, employee_id: int, form_data: Dict):
        """병역 정보 업데이트"""
        self.relation._update_military_data(employee_id, form_data)

    # ========================================
    # 대시보드 (Relation에 위임)
    # ========================================

    def get_dashboard_data(self, employee_id: int) -> Optional[Dict]:
        return self.relation.get_dashboard_data(employee_id)

    def get_employee_full_view_data(self, employee_id: int, year: int = None) -> Dict:
        """직원 전체 조회 데이터 통합 반환 (Relation에 위임)"""
        return self.relation.get_employee_full_view_data(employee_id, year)

    # ========================================
    # 폼 처리 (Core에 위임, 하위 호환성)
    # ========================================

    def _extract_employee_from_form(self, form_data: Dict, employee_id: int = 0) -> Employee:
        return self.core._extract_employee_from_form(form_data, employee_id)

    def _extract_basic_fields(self, form_data: Dict) -> Dict:
        return self.core._extract_basic_fields(form_data)


# 싱글톤 인스턴스
employee_service = EmployeeService()

# Re-export
__all__ = [
    'EmployeeService',
    'EmployeeCoreService',
    'EmployeeRelationService',
    'employee_service',
    'employee_core_service',
    'employee_relation_service',
]
