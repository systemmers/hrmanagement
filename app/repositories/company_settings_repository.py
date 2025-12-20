"""
Company Settings Repository

법인별 설정 정보를 관리합니다.
"""
from typing import Dict, Optional, List
from app.database import db
from app.models import CompanySettings
from .base_repository import BaseRepository


class CompanySettingsRepository(BaseRepository[CompanySettings]):
    """법인 설정 저장소"""

    def __init__(self):
        super().__init__(CompanySettings)

    def get_by_company(self, company_id: int) -> Dict[str, any]:
        """법인별 모든 설정 조회 (키-값 딕셔너리 반환)"""
        settings = CompanySettings.query.filter_by(company_id=company_id).all()
        return {s.key: s.get_typed_value() for s in settings}

    def get_by_company_and_category(self, company_id: int, category: str) -> Dict[str, any]:
        """법인별 카테고리 설정 조회"""
        settings = CompanySettings.query.filter_by(
            company_id=company_id,
            category=category
        ).all()
        return {s.key: s.get_typed_value() for s in settings}

    def get_setting(self, company_id: int, key: str) -> Optional[any]:
        """단일 설정값 조회"""
        setting = CompanySettings.query.filter_by(
            company_id=company_id,
            key=key
        ).first()

        if setting:
            return setting.get_typed_value()

        # 기본값 반환
        return CompanySettings.get_default(key)

    def set_setting(self, company_id: int, key: str, value: any,
                    value_type: str = None, category: str = None,
                    description: str = None) -> Dict:
        """설정값 저장 (upsert)"""
        setting = CompanySettings.query.filter_by(
            company_id=company_id,
            key=key
        ).first()

        if setting:
            setting.set_typed_value(value)
            if value_type:
                setting.value_type = value_type
            if category:
                setting.category = category
            if description:
                setting.description = description
        else:
            # 기본값에서 타입 가져오기
            default_info = CompanySettings.DEFAULTS.get(key)
            if not value_type and default_info:
                value_type = default_info[1]

            setting = CompanySettings(
                company_id=company_id,
                key=key,
                value_type=value_type or CompanySettings.TYPE_STRING,
                category=category,
                description=description
            )
            setting.set_typed_value(value)
            db.session.add(setting)

        db.session.commit()
        return setting.to_dict()

    def set_bulk_settings(self, company_id: int, settings_dict: Dict[str, any],
                          category: str = None) -> List[Dict]:
        """여러 설정값 일괄 저장"""
        results = []
        for key, value in settings_dict.items():
            result = self.set_setting(company_id, key, value, category=category)
            results.append(result)
        return results

    def delete_setting(self, company_id: int, key: str) -> bool:
        """설정 삭제"""
        setting = CompanySettings.query.filter_by(
            company_id=company_id,
            key=key
        ).first()

        if setting:
            db.session.delete(setting)
            db.session.commit()
            return True
        return False

    def get_all_settings_full(self, company_id: int) -> List[Dict]:
        """법인별 모든 설정 전체 정보 조회"""
        settings = CompanySettings.query.filter_by(company_id=company_id).all()
        return [s.to_dict() for s in settings]

    def initialize_defaults(self, company_id: int) -> List[Dict]:
        """기본 설정값으로 초기화"""
        results = []
        for key, (default_value, value_type, description) in CompanySettings.DEFAULTS.items():
            # 기존 설정이 없는 경우만 생성
            existing = CompanySettings.query.filter_by(
                company_id=company_id,
                key=key
            ).first()

            if not existing:
                # 카테고리 추출
                category = key.split('.')[0] if '.' in key else None

                result = self.set_setting(
                    company_id=company_id,
                    key=key,
                    value=default_value,
                    value_type=value_type,
                    category=category,
                    description=description
                )
                results.append(result)

        return results

    def get_employee_number_settings(self, company_id: int) -> Dict:
        """사번 설정 조회"""
        return {
            'companyCode': self.get_setting(company_id, CompanySettings.KEY_COMPANY_CODE),
            'separator': self.get_setting(company_id, CompanySettings.KEY_EMP_NUM_SEPARATOR),
            'digits': self.get_setting(company_id, CompanySettings.KEY_EMP_NUM_DIGITS),
        }

    def get_email_settings(self, company_id: int) -> Dict:
        """이메일 설정 조회"""
        return {
            'domain': self.get_setting(company_id, CompanySettings.KEY_EMAIL_DOMAIN),
            'autoGenerate': self.get_setting(company_id, CompanySettings.KEY_EMAIL_AUTO_GENERATE),
            'format': self.get_setting(company_id, CompanySettings.KEY_EMAIL_FORMAT),
        }

    def get_payroll_settings(self, company_id: int) -> Dict:
        """급여 설정 조회"""
        return {
            'paymentDay': self.get_setting(company_id, CompanySettings.KEY_PAYMENT_DAY),
        }
