"""
Company Visibility Settings Repository

법인별 정보 노출 설정을 관리합니다.
"""
from typing import Dict, Optional
from app.database import db
from app.models import CompanyVisibilitySettings
from .base_repository import BaseRepository


class CompanyVisibilityRepository(BaseRepository):
    """법인 노출 설정 저장소"""

    def __init__(self):
        super().__init__(CompanyVisibilitySettings)

    def get_by_company(self, company_id: int) -> Optional[Dict]:
        """법인별 노출 설정 조회"""
        settings = CompanyVisibilitySettings.query.filter_by(
            company_id=company_id
        ).first()

        return settings.to_dict() if settings else None

    def get_or_create(self, company_id: int) -> Dict:
        """법인별 노출 설정 조회 또는 생성"""
        settings = CompanyVisibilitySettings.query.filter_by(
            company_id=company_id
        ).first()

        if not settings:
            settings = CompanyVisibilitySettings.get_default_settings(company_id)
            db.session.add(settings)
            db.session.commit()

        return settings.to_dict()

    def update_settings(self, company_id: int, data: Dict) -> Optional[Dict]:
        """노출 설정 업데이트"""
        settings = CompanyVisibilitySettings.query.filter_by(
            company_id=company_id
        ).first()

        if not settings:
            # 기본 설정으로 생성 후 업데이트
            settings = CompanyVisibilitySettings.get_default_settings(company_id)
            db.session.add(settings)

        # 필드 업데이트
        if 'salaryVisibility' in data:
            settings.salary_visibility = data['salaryVisibility']
        if 'evaluationVisibility' in data:
            settings.evaluation_visibility = data['evaluationVisibility']
        if 'orgChartVisibility' in data:
            settings.org_chart_visibility = data['orgChartVisibility']
        if 'contactVisibility' in data:
            settings.contact_visibility = data['contactVisibility']
        if 'documentVisibility' in data:
            settings.document_visibility = data['documentVisibility']
        if 'showSalaryToManagers' in data:
            settings.show_salary_to_managers = data['showSalaryToManagers']
        if 'showEvaluationToManagers' in data:
            settings.show_evaluation_to_managers = data['showEvaluationToManagers']

        db.session.commit()
        return settings.to_dict()

    def reset_to_defaults(self, company_id: int) -> Dict:
        """기본값으로 초기화"""
        settings = CompanyVisibilitySettings.query.filter_by(
            company_id=company_id
        ).first()

        if settings:
            for key, value in CompanyVisibilitySettings.DEFAULTS.items():
                setattr(settings, key, value)
        else:
            settings = CompanyVisibilitySettings.get_default_settings(company_id)
            db.session.add(settings)

        db.session.commit()
        return settings.to_dict()
