"""
법인 설정 서비스

법인별 분류 옵션, 설정, 노출 설정, 서류 관리 비즈니스 로직을 제공합니다.
Phase 2: Service 계층 표준화
"""
from typing import Dict, List, Optional, Any

from app.repositories import (
    ClassificationOptionsRepository,
    CompanySettingsRepository,
    NumberCategoryRepository,
    CompanyVisibilityRepository,
    CompanyDocumentRepository
)


class CorporateSettingsService:
    """
    법인 설정 서비스

    법인별 분류 옵션, 설정, 번호 카테고리, 노출 설정, 서류 관리 기능을 제공합니다.
    """

    def __init__(self):
        self.classification_repo = ClassificationOptionsRepository()
        self.settings_repo = CompanySettingsRepository()
        self.number_category_repo = NumberCategoryRepository()
        self.visibility_repo = CompanyVisibilityRepository()
        self.document_repo = CompanyDocumentRepository()

    # ========================================
    # 분류 옵션 관리
    # ========================================

    def get_all_classifications(self, company_id: int) -> Dict:
        """모든 분류 옵션 조회"""
        return self.classification_repo.get_all_options(company_id)

    def get_organization_options(self, company_id: int) -> Dict:
        """조직 구조 분류 옵션 조회"""
        return self.classification_repo.get_organization_options(company_id)

    def get_employment_options(self, company_id: int) -> Dict:
        """고용 정책 분류 옵션 조회"""
        return self.classification_repo.get_employment_options(company_id)

    def get_classifications_by_category(self, category: str, company_id: int) -> List[Dict]:
        """카테고리별 분류 옵션 조회"""
        return self.classification_repo.get_by_category_for_company(category, company_id)

    def add_classification(self, company_id: int, category: str, value: str, label: str) -> Dict:
        """분류 옵션 추가"""
        return self.classification_repo.add_option_for_company(
            company_id=company_id,
            category=category,
            value=value,
            label=label or value
        )

    def update_classification(self, option_id: int, company_id: int, data: Dict) -> Optional[Dict]:
        """분류 옵션 수정"""
        return self.classification_repo.update_option(option_id, company_id, data)

    def delete_classification(self, option_id: int, company_id: int) -> bool:
        """분류 옵션 삭제"""
        return self.classification_repo.delete_option_for_company(option_id, company_id)

    def toggle_system_option(self, company_id: int, category: str, value: str, is_active: bool) -> Dict:
        """시스템 옵션 활성화/비활성화 토글"""
        return self.classification_repo.toggle_system_option(company_id, category, value, is_active)

    # ========================================
    # 법인 설정 관리
    # ========================================

    def get_settings(self, company_id: int) -> Dict:
        """법인 설정 조회"""
        return self.settings_repo.get_by_company(company_id)

    def update_settings(self, company_id: int, data: Dict) -> List:
        """법인 설정 일괄 저장"""
        return self.settings_repo.set_bulk_settings(company_id, data)

    def get_setting(self, company_id: int, key: str) -> Any:
        """단일 설정값 조회"""
        return self.settings_repo.get_setting(company_id, key)

    def set_setting(self, company_id: int, key: str, value: Any) -> Dict:
        """단일 설정값 저장"""
        return self.settings_repo.set_setting(company_id, key, value)

    def get_employee_number_settings(self, company_id: int) -> Dict:
        """사번 설정 조회"""
        return self.settings_repo.get_employee_number_settings(company_id)

    def get_payroll_settings(self, company_id: int) -> Dict:
        """급여 설정 조회"""
        return self.settings_repo.get_payroll_settings(company_id)

    def initialize_settings(self, company_id: int) -> List:
        """기본 설정값 초기화"""
        return self.settings_repo.initialize_defaults(company_id)

    # ========================================
    # 번호 카테고리 관리
    # ========================================

    def get_number_categories(self, company_id: int, type_filter: str = None) -> List[Dict]:
        """번호 분류코드 조회"""
        return self.number_category_repo.get_by_company(company_id, type_filter)

    def get_employee_categories(self, company_id: int) -> List[Dict]:
        """사번 분류코드 조회"""
        return self.number_category_repo.get_employee_categories(company_id)

    def get_asset_categories(self, company_id: int) -> List[Dict]:
        """자산번호 분류코드 조회"""
        return self.number_category_repo.get_asset_categories(company_id)

    def create_number_category(self, company_id: int, type_code: str, code: str,
                               name: str, description: str = '') -> Dict:
        """번호 분류코드 생성"""
        return self.number_category_repo.create_category(
            company_id=company_id,
            type_code=type_code,
            code=code,
            name=name,
            description=description
        )

    def update_number_category(self, category_id: int, company_id: int, data: Dict) -> Optional[Dict]:
        """번호 분류코드 수정"""
        return self.number_category_repo.update_category(category_id, company_id, data)

    def delete_number_category(self, category_id: int, company_id: int) -> bool:
        """번호 분류코드 삭제"""
        return self.number_category_repo.delete_category(category_id, company_id)

    def preview_next_number(self, category_id: int, company_code: str,
                            separator: str, digits: int) -> str:
        """다음 번호 미리보기"""
        return self.number_category_repo.preview_next_number(
            category_id, company_code, separator, digits
        )

    def initialize_asset_categories(self, company_id: int) -> List:
        """기본 자산 분류코드 초기화"""
        return self.number_category_repo.initialize_default_asset_categories(company_id)

    # ========================================
    # 노출 설정 관리
    # ========================================

    def get_visibility_settings(self, company_id: int) -> Dict:
        """노출 설정 조회"""
        return self.visibility_repo.get_or_create(company_id)

    def update_visibility_settings(self, company_id: int, data: Dict) -> Dict:
        """노출 설정 저장"""
        return self.visibility_repo.update_settings(company_id, data)

    def reset_visibility_settings(self, company_id: int) -> Dict:
        """노출 설정 기본값 초기화"""
        return self.visibility_repo.reset_to_defaults(company_id)

    # ========================================
    # 법인 서류 관리
    # ========================================

    def get_documents(self, company_id: int) -> List[Dict]:
        """법인 서류 목록 조회"""
        return self.document_repo.get_by_company(company_id)

    def get_document_statistics(self, company_id: int) -> Dict:
        """법인 서류 통계 조회"""
        return self.document_repo.get_statistics(company_id)

    def get_documents_by_category(self, company_id: int, category: str) -> List[Dict]:
        """카테고리별 법인 서류 조회"""
        return self.document_repo.get_by_category(company_id, category)

    def create_document(self, data: Dict) -> Dict:
        """법인 서류 등록"""
        return self.document_repo.create(data)

    def update_document(self, document_id: int, data: Dict) -> Optional[Dict]:
        """법인 서류 수정"""
        return self.document_repo.update(document_id, data)

    def delete_document(self, document_id: int) -> bool:
        """법인 서류 삭제"""
        return self.document_repo.delete(document_id)

    def get_expiring_documents(self, company_id: int, days: int = 30) -> List[Dict]:
        """만료 예정 서류 조회"""
        return self.document_repo.get_expiring_documents(company_id, days)

    def get_document_by_id(self, document_id: int, company_id: int) -> Optional[Dict]:
        """법인 서류 ID로 조회

        Args:
            document_id: 서류 ID
            company_id: 법인 ID (권한 검증용)

        Returns:
            서류 정보 Dict 또는 None
        """
        model = self.document_repo.find_by_id(document_id)
        if not model:
            return None
        # 권한 검증: 해당 법인의 서류인지 확인
        if model.company_id != company_id:
            return None
        return model.to_dict()


# 싱글톤 인스턴스
corporate_settings_service = CorporateSettingsService()
