"""
Company Service

법인(Company) 관련 비즈니스 로직을 처리합니다.
Phase 24: 레이어 분리 - Blueprint -> Service -> Repository

CLAUDE.md 레이어 분리 규칙 준수:
- Blueprint에서 Repository 직접 호출 금지
- 모든 Repository 호출은 Service 경유
"""
from typing import Dict, Optional

from app.database import db
from app.models.company import Company
from app.repositories.company_repository import company_repository
from app.shared.utils.transaction import atomic_transaction
from app.shared.base import ServiceResult


class CompanyService:
    """법인 관리 서비스"""

    def __init__(self):
        self.company_repo = company_repository

    # ========================================
    # 조회
    # ========================================

    def get_by_id(self, company_id: int) -> Optional[Company]:
        """법인 ID로 조회

        Args:
            company_id: 법인 ID

        Returns:
            Company 모델 또는 None
        """
        return self.company_repo.find_by_id(company_id)

    def get_with_stats(self, company_id: int) -> Optional[Dict]:
        """법인 정보 + 통계 조회

        Args:
            company_id: 법인 ID

        Returns:
            법인 정보 Dict (통계 포함) 또는 None
        """
        return self.company_repo.get_with_stats(company_id)

    def exists_by_business_number(self, business_number: str) -> bool:
        """사업자등록번호 존재 여부 확인

        Args:
            business_number: 사업자등록번호

        Returns:
            존재 여부
        """
        return self.company_repo.exists_by_business_number(business_number)

    # ========================================
    # 수정
    # ========================================

    def update_company_info(
        self,
        company_id: int,
        form_data: Dict
    ) -> ServiceResult[Dict]:
        """법인 정보 수정

        Args:
            company_id: 법인 ID
            form_data: 폼 데이터

        Returns:
            ServiceResult[Dict]
        """
        company = self.get_by_id(company_id)
        if not company:
            return ServiceResult.not_found('법인')

        try:
            with atomic_transaction():
                company.name = form_data.get('company_name', company.name).strip()
                company.representative = form_data.get('representative', company.representative).strip()
                company.business_type = form_data.get('business_type', '').strip() or None
                company.business_category = form_data.get('business_category', '').strip() or None
                company.phone = form_data.get('phone', '').strip() or None
                company.email = form_data.get('company_email', '').strip() or None
                company.website = form_data.get('website', '').strip() or None
                company.address = form_data.get('address', '').strip() or None
                company.address_detail = form_data.get('address_detail', '').strip() or None
                company.postal_code = form_data.get('postal_code', '').strip() or None
            return ServiceResult.ok(data=company.to_dict())
        except Exception as e:
            return ServiceResult.fail(str(e))


# 싱글톤 인스턴스
company_service = CompanyService()
