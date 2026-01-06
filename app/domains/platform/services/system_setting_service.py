"""
시스템 설정 서비스

시스템 설정 조회 비즈니스 로직을 제공합니다.

Phase 2: Service 계층 표준화
Phase 7: 도메인 중심 마이그레이션 완료
"""
from typing import Dict, Optional, Any


class SystemSettingService:
    """
    시스템 설정 서비스

    시스템 설정 조회 기능을 제공합니다.
    """

    @property
    def system_setting_repo(self):
        """지연 초기화된 시스템 설정 Repository"""
        from app.domains.platform import get_system_setting_repo
        return get_system_setting_repo()

    def get_by_key(self, key: str) -> Optional[Dict]:
        """
        키로 시스템 설정 조회

        Args:
            key: 설정 키

        Returns:
            설정 값 또는 None
        """
        return self.system_setting_repo.get_by_key(key)

    def get_value(self, key: str, default: Any = None) -> Any:
        """
        키로 시스템 설정 값만 조회

        Args:
            key: 설정 키
            default: 기본값

        Returns:
            설정 값 또는 기본값
        """
        setting = self.system_setting_repo.get_by_key(key)
        if setting:
            return setting.get('value', default) if isinstance(setting, dict) else setting.value
        return default

    def get_company_data(self) -> Dict[str, str]:
        """
        회사 정보 조회

        Returns:
            회사 정보 Dict
        """
        company_data = {}
        company_keys = [
            'company.name', 'company.name_en', 'company.ceo_name',
            'company.business_number', 'company.corporate_number',
            'company.address', 'company.phone', 'company.fax',
            'company.website', 'company.established_date', 'company.logo_url'
        ]

        for key in company_keys:
            setting = self.system_setting_repo.get_by_key(key)
            if setting:
                field_name = key.replace('company.', '')
                company_data[field_name] = setting.get('value', '') if isinstance(setting, dict) else setting.value

        return company_data


# 싱글톤 인스턴스
system_setting_service = SystemSettingService()
