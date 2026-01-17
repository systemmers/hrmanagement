"""
Employee Relation Service

직원 관계형 데이터 조회 및 수정을 담당합니다.
- 학력/경력/자격증/어학/병역/프로젝트/수상/가족 관리
- 첨부파일 관리
- 급여/복리후생/계약 정보 조회
- 대시보드 데이터

Phase 3: EmployeeService 분리 - Relation Service
Phase 8.1: create_* 메서드 필드 필터링 추가
"""
from typing import Any, Dict, List, Optional, Tuple


def _filter_model_fields(model_class, data: Dict) -> Dict:
    """모델에 정의된 컬럼만 필터링하여 반환

    Args:
        model_class: SQLAlchemy 모델 클래스
        data: 입력 데이터 딕셔너리

    Returns:
        모델 컬럼에 해당하는 필드만 포함된 딕셔너리
    """
    allowed_fields = set(model_class.__table__.columns.keys())
    return {k: v for k, v in data.items() if k in allowed_fields}

from app.shared.utils.transaction import atomic_transaction
from app.shared.base import relation_updater, get_relation_config, SUPPORTED_RELATION_TYPES


class EmployeeRelationService:
    """직원 관계형 데이터 서비스"""

    # ========================================
    # Repository Properties (지연 초기화)
    # ========================================

    @property
    def employee_repo(self):
        """직원 Repository (대시보드용)"""
        from app.extensions import employee_repo
        return employee_repo

    @property
    def family_repo(self):
        from app.extensions import family_repo
        return family_repo

    @property
    def education_repo(self):
        from app.extensions import education_repo
        return education_repo

    @property
    def career_repo(self):
        from app.extensions import career_repo
        return career_repo

    @property
    def certificate_repo(self):
        from app.extensions import certificate_repo
        return certificate_repo

    @property
    def language_repo(self):
        from app.extensions import language_repo
        return language_repo

    @property
    def hr_project_repo(self):
        from app.extensions import hr_project_repo
        return hr_project_repo

    @property
    def project_participation_repo(self):
        from app.extensions import project_participation_repo
        return project_participation_repo

    @property
    def award_repo(self):
        from app.extensions import award_repo
        return award_repo

    @property
    def attachment_repo(self):
        from app.extensions import attachment_repo
        return attachment_repo

    @property
    def salary_repo(self):
        from app.extensions import salary_repo
        return salary_repo

    @property
    def benefit_repo(self):
        from app.extensions import benefit_repo
        return benefit_repo

    @property
    def contract_repo(self):
        from app.extensions import contract_repo
        return contract_repo

    @property
    def salary_history_repo(self):
        from app.extensions import salary_history_repo
        return salary_history_repo

    @property
    def promotion_repo(self):
        from app.extensions import promotion_repo
        return promotion_repo

    @property
    def evaluation_repo(self):
        from app.extensions import evaluation_repo
        return evaluation_repo

    @property
    def training_repo(self):
        from app.extensions import training_repo
        return training_repo

    @property
    def attendance_repo(self):
        from app.extensions import attendance_repo
        return attendance_repo

    @property
    def insurance_repo(self):
        from app.extensions import insurance_repo
        return insurance_repo

    @property
    def asset_repo(self):
        from app.extensions import asset_repo
        return asset_repo

    @property
    def salary_payment_repo(self):
        from app.extensions import salary_payment_repo
        return salary_payment_repo

    @property
    def employment_contract_repo(self):
        from app.extensions import employment_contract_repo
        return employment_contract_repo

    @property
    def classification_repo(self):
        from app.extensions import classification_repo
        return classification_repo

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

    def get_employment_contract_list(self, employee_id: int) -> List[Dict]:
        """근로계약 이력 목록 조회"""
        models = self.employment_contract_repo.find_by_employee_id(employee_id)
        return [m.to_dict() for m in models]

    def get_attachment_list(self, employee_id: int) -> List[Dict]:
        """첨부파일 목록 조회 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        return attachment_service.get_by_employee_id(employee_id)

    def get_attachment_by_category(self, employee_id: int, category: str) -> Optional[Dict]:
        """카테고리별 첨부파일 조회 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        return attachment_service.get_one_by_category(employee_id, category)

    def get_classification_options(self) -> List[Dict]:
        """분류 옵션 조회"""
        models = self.classification_repo.find_all()
        return [m.to_dict() for m in models]

    def get_all_classification_options(self, company_id: int = None) -> Dict:
        """전체 분류 옵션 조회 (카테고리별)"""
        return self.classification_repo.get_all_options(company_id)

    # ========================================
    # 첨부파일 관리 (deprecated - attachment_service 사용 권장)
    # Phase 33: attachment 도메인으로 통합
    # ========================================

    def create_attachment(self, attachment_data: Dict) -> Dict:
        """첨부파일 생성 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        # camelCase → snake_case 변환
        normalized_data = {
            'owner_type': 'employee',
            'owner_id': attachment_data.get('employeeId') or attachment_data.get('employee_id'),
            'employee_id': attachment_data.get('employeeId') or attachment_data.get('employee_id'),
            'file_name': attachment_data.get('fileName') or attachment_data.get('file_name'),
            'file_path': attachment_data.get('filePath') or attachment_data.get('file_path'),
            'file_type': attachment_data.get('fileType') or attachment_data.get('file_type'),
            'file_size': attachment_data.get('fileSize') or attachment_data.get('file_size', 0),
            'category': attachment_data.get('category'),
            'upload_date': attachment_data.get('uploadDate') or attachment_data.get('upload_date'),
        }
        return attachment_service.create(normalized_data)

    def get_attachment_by_id(self, attachment_id: int) -> Optional[Dict]:
        """첨부파일 ID로 조회 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        return attachment_service.get_by_id(attachment_id)

    def delete_attachment(self, attachment_id: int) -> bool:
        """첨부파일 삭제 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        return attachment_service.delete(attachment_id)

    def delete_attachment_by_category(self, employee_id: int, category: str) -> bool:
        """카테고리별 첨부파일 삭제 (deprecated - attachment_service 사용 권장)"""
        from app.domains.attachment.services import attachment_service
        result = attachment_service.delete_by_category(employee_id, category)
        return result > 0 if isinstance(result, int) else bool(result)

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
    # 전체 관계형 데이터 업데이트 (내부용)
    # ========================================

    def update_all_related_data(self, employee_id: int, form_data: Dict):
        """모든 관계형 데이터 일괄 업데이트

        RelationDataUpdater를 사용하여 관계 타입을 처리합니다.
        """
        repos = self._get_repositories()

        # 1:N 관계 데이터 일괄 처리
        for relation_type in SUPPORTED_RELATION_TYPES:
            config = get_relation_config(relation_type, repos)
            relation_updater.update(employee_id, form_data, config)

    def save_insurance_data(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """4대보험 데이터 저장 (Phase 28: upsert)

        Args:
            employee_id: 직원 ID
            data: 4대보험 데이터 (Boolean 필드)
            commit: 커밋 여부

        Returns:
            저장된 Insurance 모델의 to_dict()
        """
        return self.insurance_repo.save_for_employee(employee_id, data, commit=commit)

    # ========================================
    # 전체 조회 통합 메서드 (N+1 최적화)
    # ========================================

    def get_employee_full_view_data(self, employee_id: int, year: int = None) -> Dict:
        """직원 전체 조회 데이터 통합 반환 (N+1 쿼리 최적화)

        detail_routes.py, mypage.py에서 사용되는 모든 관계형 데이터를
        한 번에 조회하여 반환합니다.

        Args:
            employee_id: 직원 ID
            year: 근태 요약 조회 연도 (기본: 현재 연도)

        Returns:
            Dict containing all relation data for employee detail view:
            - education_list, career_list, certificate_list, family_list
            - language_list, military, salary, benefit, contract
            - salary_history_list, promotion_list, evaluation_list
            - training_list, attendance_summary, insurance
            - hr_project_list, project_participation_list, award_list
            - asset_list, salary_payment_list, attachment_list
        """
        from datetime import date
        if year is None:
            year = date.today().year

        return {
            # 기본 이력 데이터
            'education_list': self.get_education_list(employee_id),
            'career_list': self.get_career_list(employee_id),
            'certificate_list': self.get_certificate_list(employee_id),
            'family_list': self.get_family_list(employee_id),
            'language_list': self.get_language_list(employee_id),

            # 핵심 기능 데이터
            'salary': self.get_salary_info(employee_id),
            'benefit': self.get_benefit_info(employee_id),
            'contract': self.get_contract_info(employee_id),
            'salary_history_list': self.get_salary_history_list(employee_id),

            # 인사평가 기능 데이터
            'promotion_list': self.get_promotion_list(employee_id),
            'evaluation_list': self.get_evaluation_list(employee_id),
            'training_list': self.get_training_list(employee_id),
            'attendance_summary': self.get_attendance_summary(employee_id, year),

            # 부가 기능 데이터
            'insurance': self.get_insurance_info(employee_id),
            'hr_project_list': self.get_hr_project_list(employee_id),
            'project_participation_list': self.get_project_participation_list(employee_id),
            'award_list': self.get_award_list(employee_id),
            'asset_list': self.get_asset_list(employee_id),

            # 급여 및 첨부파일
            'salary_payment_list': self.get_salary_payment_list(employee_id),
            'employment_contract_list': self.get_employment_contract_list(employee_id),
            'attachment_list': self.get_attachment_list(employee_id),
        }

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

        # 이력 통계
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
    # 개별 항목 CRUD (인라인 편집 API용)
    # Phase 8: 동적 테이블 섹션
    # ========================================

    # --- 가족정보 (families) ---
    def get_family_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """가족 항목 단건 조회"""
        model = self.family_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_family(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """가족 항목 생성"""
        from app.domains.employee.models import FamilyMember
        filtered_data = _filter_model_fields(FamilyMember, data)
        filtered_data['employee_id'] = employee_id
        model = FamilyMember(**filtered_data)
        return self.family_repo.create_model(model, commit=commit).to_dict()

    def update_family(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """가족 항목 수정 (단건 - 인라인 편집 API용)"""
        model = self.family_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_family(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """가족 항목 삭제 (단건 - 인라인 편집 API용)"""
        model = self.family_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.family_repo.delete(item_id, commit=commit)

    # --- 학력정보 (educations) ---
    def get_education_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """학력 항목 단건 조회"""
        model = self.education_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_education(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """학력 항목 생성"""
        from app.domains.employee.models import Education
        filtered_data = _filter_model_fields(Education, data)
        filtered_data['employee_id'] = employee_id
        model = Education(**filtered_data)
        return self.education_repo.create_model(model, commit=commit).to_dict()

    def update_education(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """학력 항목 수정"""
        model = self.education_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_education(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """학력 항목 삭제"""
        model = self.education_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.education_repo.delete(item_id, commit=commit)

    # --- 경력정보 (careers) ---
    def get_career_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """경력 항목 단건 조회"""
        model = self.career_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_career(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """경력 항목 생성"""
        from app.domains.employee.models import Career
        filtered_data = _filter_model_fields(Career, data)
        filtered_data['employee_id'] = employee_id
        model = Career(**filtered_data)
        return self.career_repo.create_model(model, commit=commit).to_dict()

    def update_career(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """경력 항목 수정"""
        model = self.career_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_career(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """경력 항목 삭제"""
        model = self.career_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.career_repo.delete(item_id, commit=commit)

    # --- 자격증 (certificates) ---
    def get_certificate_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """자격증 항목 단건 조회"""
        model = self.certificate_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_certificate(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """자격증 항목 생성"""
        from app.domains.employee.models import Certificate
        filtered_data = _filter_model_fields(Certificate, data)
        filtered_data['employee_id'] = employee_id
        model = Certificate(**filtered_data)
        return self.certificate_repo.create_model(model, commit=commit).to_dict()

    def update_certificate(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """자격증 항목 수정"""
        model = self.certificate_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_certificate(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """자격증 항목 삭제"""
        model = self.certificate_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.certificate_repo.delete(item_id, commit=commit)

    # --- 언어능력 (languages) ---
    def get_language_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """언어능력 항목 단건 조회"""
        model = self.language_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_language(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """언어능력 항목 생성"""
        from app.domains.employee.models import Language
        filtered_data = _filter_model_fields(Language, data)
        filtered_data['employee_id'] = employee_id
        model = Language(**filtered_data)
        return self.language_repo.create_model(model, commit=commit).to_dict()

    def update_language(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """언어능력 항목 수정"""
        model = self.language_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_language(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """언어능력 항목 삭제"""
        model = self.language_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.language_repo.delete(item_id, commit=commit)

    # --- 수상내역 (awards) ---
    def get_award_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """수상내역 항목 단건 조회"""
        model = self.award_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_award(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """수상내역 항목 생성"""
        from app.domains.employee.models import Award
        filtered_data = _filter_model_fields(Award, data)
        filtered_data['employee_id'] = employee_id
        model = Award(**filtered_data)
        return self.award_repo.create_model(model, commit=commit).to_dict()

    def update_award(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """수상내역 항목 수정"""
        model = self.award_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_award(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """수상내역 항목 삭제"""
        model = self.award_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.award_repo.delete(item_id, commit=commit)

    # --- 프로젝트 참여 (projects) ---
    def get_project_list(self, employee_id: int) -> List[Dict]:
        """프로젝트 참여 목록 조회 (API alias)"""
        return self.get_project_participation_list(employee_id)

    def get_project_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """프로젝트 참여 항목 단건 조회"""
        model = self.project_participation_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_project(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """프로젝트 참여 항목 생성"""
        from app.domains.employee.models import ProjectParticipation
        filtered_data = _filter_model_fields(ProjectParticipation, data)
        filtered_data['employee_id'] = employee_id
        model = ProjectParticipation(**filtered_data)
        return self.project_participation_repo.create_model(model, commit=commit).to_dict()

    def update_project(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """프로젝트 참여 항목 수정"""
        model = self.project_participation_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_project(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """프로젝트 참여 항목 삭제"""
        model = self.project_participation_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.project_participation_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 연봉계약 이력 (salary-histories) ---
    def get_salary_history_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """연봉계약 이력 항목 단건 조회"""
        model = self.salary_history_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_salary_history(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """연봉계약 이력 항목 생성"""
        from app.domains.employee.models import SalaryHistory
        filtered_data = _filter_model_fields(SalaryHistory, data)
        filtered_data['employee_id'] = employee_id
        model = SalaryHistory(**filtered_data)
        return self.salary_history_repo.create_model(model, commit=commit).to_dict()

    def update_salary_history(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """연봉계약 이력 항목 수정"""
        model = self.salary_history_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_salary_history(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """연봉계약 이력 항목 삭제"""
        model = self.salary_history_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.salary_history_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 급여 지급 이력 (salary-payments) ---
    def get_salary_payment_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """급여 지급 이력 항목 단건 조회"""
        model = self.salary_payment_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_salary_payment(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """급여 지급 이력 항목 생성"""
        from app.domains.employee.models import SalaryPayment
        filtered_data = _filter_model_fields(SalaryPayment, data)
        filtered_data['employee_id'] = employee_id
        model = SalaryPayment(**filtered_data)
        return self.salary_payment_repo.create_model(model, commit=commit).to_dict()

    def update_salary_payment(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """급여 지급 이력 항목 수정"""
        model = self.salary_payment_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_salary_payment(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """급여 지급 이력 항목 삭제"""
        model = self.salary_payment_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.salary_payment_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 인사이동/승진 (promotions) ---
    def get_promotion_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """인사이동/승진 항목 단건 조회"""
        model = self.promotion_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_promotion(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """인사이동/승진 항목 생성"""
        from app.domains.employee.models import Promotion
        filtered_data = _filter_model_fields(Promotion, data)
        filtered_data['employee_id'] = employee_id
        model = Promotion(**filtered_data)
        return self.promotion_repo.create_model(model, commit=commit).to_dict()

    def update_promotion(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """인사이동/승진 항목 수정"""
        model = self.promotion_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_promotion(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """인사이동/승진 항목 삭제"""
        model = self.promotion_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.promotion_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 인사고과 (evaluations) ---
    def get_evaluation_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """인사고과 항목 단건 조회"""
        model = self.evaluation_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_evaluation(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """인사고과 항목 생성"""
        from app.domains.employee.models import Evaluation
        filtered_data = _filter_model_fields(Evaluation, data)
        filtered_data['employee_id'] = employee_id
        model = Evaluation(**filtered_data)
        return self.evaluation_repo.create_model(model, commit=commit).to_dict()

    def update_evaluation(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """인사고과 항목 수정"""
        model = self.evaluation_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_evaluation(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """인사고과 항목 삭제"""
        model = self.evaluation_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.evaluation_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 교육훈련 (trainings) ---
    def get_training_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """교육훈련 항목 단건 조회"""
        model = self.training_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_training(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """교육훈련 항목 생성"""
        from app.domains.employee.models import Training
        filtered_data = _filter_model_fields(Training, data)
        filtered_data['employee_id'] = employee_id
        model = Training(**filtered_data)
        return self.training_repo.create_model(model, commit=commit).to_dict()

    def update_training(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """교육훈련 항목 수정"""
        model = self.training_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_training(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """교육훈련 항목 삭제"""
        model = self.training_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.training_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: HR 프로젝트 (hr-projects) ---
    def get_hr_project_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """HR 프로젝트 항목 단건 조회"""
        model = self.hr_project_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_hr_project(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """HR 프로젝트 항목 생성"""
        from app.domains.employee.models import HrProject
        filtered_data = _filter_model_fields(HrProject, data)
        filtered_data['employee_id'] = employee_id
        model = HrProject(**filtered_data)
        return self.hr_project_repo.create_model(model, commit=commit).to_dict()

    def update_hr_project(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """HR 프로젝트 항목 수정"""
        model = self.hr_project_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_hr_project(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """HR 프로젝트 항목 삭제"""
        model = self.hr_project_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.hr_project_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 비품지급 (assets) ---
    def get_asset_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """비품지급 항목 단건 조회"""
        model = self.asset_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_asset(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """비품지급 항목 생성"""
        from app.domains.employee.models import Asset
        filtered_data = _filter_model_fields(Asset, data)
        filtered_data['employee_id'] = employee_id
        model = Asset(**filtered_data)
        return self.asset_repo.create_model(model, commit=commit).to_dict()

    def update_asset(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """비품지급 항목 수정"""
        model = self.asset_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_asset(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """비품지급 항목 삭제"""
        model = self.asset_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.asset_repo.delete(item_id, commit=commit)

    # --- HR 릴레이션: 근로계약 이력 (employment-contracts) ---
    def get_employment_contract_by_id(self, item_id: int, employee_id: int) -> Optional[Dict]:
        """근로계약 이력 항목 단건 조회"""
        model = self.employment_contract_repo.find_by_id(item_id)
        if model and model.employee_id == employee_id:
            return model.to_dict()
        return None

    def create_employment_contract(self, employee_id: int, data: Dict, commit: bool = True) -> Dict:
        """근로계약 이력 항목 생성"""
        from app.domains.employee.models import EmploymentContract
        filtered_data = _filter_model_fields(EmploymentContract, data)
        filtered_data['employee_id'] = employee_id
        model = EmploymentContract(**filtered_data)
        return self.employment_contract_repo.create_model(model, commit=commit).to_dict()

    def update_employment_contract(self, item_id: int, data: Dict, employee_id: int, commit: bool = True) -> Tuple[bool, Optional[str]]:
        """근로계약 이력 항목 수정"""
        model = self.employment_contract_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False, '항목을 찾을 수 없습니다.'
        for key, value in data.items():
            if hasattr(model, key) and key not in ('id', 'employee_id'):
                setattr(model, key, value)
        if commit:
            from app.extensions import db
            db.session.commit()
        return True, None

    def delete_employment_contract(self, item_id: int, employee_id: int, commit: bool = True) -> bool:
        """근로계약 이력 항목 삭제"""
        model = self.employment_contract_repo.find_by_id(item_id)
        if not model or model.employee_id != employee_id:
            return False
        return self.employment_contract_repo.delete(item_id, commit=commit)


# 싱글톤 인스턴스
employee_relation_service = EmployeeRelationService()
