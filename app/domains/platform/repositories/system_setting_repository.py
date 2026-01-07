"""
SystemSetting Repository

시스템 설정 CRUD 및 캐싱 기능을 제공합니다.

Phase 7: 도메인 중심 마이그레이션 완료
"""
from typing import Optional, Dict, List, Any
from app.database import db
from app.domains.platform.models import SystemSetting
from app.shared.repositories.base_repository import BaseRepository


class SystemSettingRepository(BaseRepository[SystemSetting]):
    """시스템 설정 저장소"""

    # 메모리 캐시 (간단한 구현)
    _cache: Dict[str, Any] = {}
    _cache_enabled: bool = True

    def __init__(self):
        super().__init__(SystemSetting)

    def get_by_key(self, key: str) -> Optional[Dict]:
        """키로 설정 조회"""
        # 캐시 확인
        if self._cache_enabled and key in self._cache:
            return self._cache[key]

        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            result = setting.to_dict()
            if self._cache_enabled:
                self._cache[key] = result
            return result
        return None

    def get_value(self, key: str, default: Any = None) -> Any:
        """키로 설정값(타입 변환된) 조회"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            return setting.get_typed_value()
        return default

    def set_value(self, key: str, value: Any, value_type: str = 'string',
                  description: str = None, category: str = None) -> Dict:
        """설정값 저장 (upsert)"""
        setting = SystemSetting.query.filter_by(key=key).first()

        if setting:
            # 기존 설정 업데이트
            setting.value_type = value_type
            setting.set_typed_value(value)
            if description is not None:
                setting.description = description
            if category is not None:
                setting.category = category
        else:
            # 새 설정 생성
            setting = SystemSetting(
                key=key,
                value_type=value_type,
                description=description,
                category=category,
            )
            setting.set_typed_value(value)
            db.session.add(setting)

        db.session.commit()

        # 캐시 무효화
        self._invalidate_cache(key)

        return setting.to_dict()

    def get_by_category(self, category: str) -> List[Dict]:
        """카테고리별 설정 조회"""
        settings = SystemSetting.query.filter_by(category=category).all()
        return [s.to_dict() for s in settings]

    def get_all_grouped(self) -> Dict[str, List[Dict]]:
        """카테고리별로 그룹화된 모든 설정 조회"""
        settings = SystemSetting.query.order_by(
            SystemSetting.category,
            SystemSetting.key
        ).all()

        grouped = {}
        for setting in settings:
            category = setting.category or 'general'
            if category not in grouped:
                grouped[category] = []
            grouped[category].append(setting.to_dict())

        return grouped

    def delete_by_key(self, key: str) -> bool:
        """키로 설정 삭제"""
        setting = SystemSetting.query.filter_by(key=key).first()
        if setting:
            db.session.delete(setting)
            db.session.commit()
            self._invalidate_cache(key)
            return True
        return False

    def bulk_set(self, settings: Dict[str, Any], category: str = None) -> List[Dict]:
        """여러 설정 일괄 저장"""
        results = []
        for key, value in settings.items():
            # value가 dict인 경우 추가 정보 포함
            if isinstance(value, dict):
                result = self.set_value(
                    key=key,
                    value=value.get('value'),
                    value_type=value.get('type', 'string'),
                    description=value.get('description'),
                    category=value.get('category', category),
                )
            else:
                # value_type 추론
                if isinstance(value, bool):
                    value_type = 'boolean'
                elif isinstance(value, int):
                    value_type = 'integer'
                elif isinstance(value, float):
                    value_type = 'float'
                elif isinstance(value, (dict, list)):
                    value_type = 'json'
                else:
                    value_type = 'string'

                result = self.set_value(
                    key=key,
                    value=value,
                    value_type=value_type,
                    category=category,
                )
            results.append(result)
        return results

    def _invalidate_cache(self, key: str = None):
        """캐시 무효화"""
        if key:
            self._cache.pop(key, None)
        else:
            self._cache.clear()

    def clear_cache(self):
        """전체 캐시 클리어"""
        self._cache.clear()

    def enable_cache(self, enabled: bool = True):
        """캐시 활성화/비활성화"""
        self._cache_enabled = enabled
        if not enabled:
            self._cache.clear()

    # 편의 메서드들

    def get_company_info(self) -> Dict:
        """회사 정보 조회"""
        settings = self.get_by_category('company')
        result = {}
        for s in settings:
            # 키에서 'company.' 접두사 제거
            short_key = s['key'].replace('company.', '')
            result[short_key] = s['typedValue']
        return result

    def set_company_info(self, info: Dict) -> List[Dict]:
        """회사 정보 저장"""
        settings = {}
        for key, value in info.items():
            settings[f'company.{key}'] = value
        return self.bulk_set(settings, category='company')

    def get_employee_number_config(self) -> Dict:
        """사번 생성 규칙 조회"""
        settings = self.get_by_category('employee_number')
        result = {
            'format': 'EMP-{YYYY}-{NNNN}',  # 기본값
            'auto_generate': True,
            'prefix': 'EMP',
            'include_year': True,
            'sequence_digits': 4,
            'separator': '-',
        }
        for s in settings:
            short_key = s['key'].replace('employee_number.', '')
            result[short_key] = s['typedValue']
        return result

    def get_email_config(self) -> Dict:
        """이메일 설정 조회"""
        settings = self.get_by_category('email')
        result = {
            'domain': '',
            'auto_generate': False,
            'format': '{first_name}.{last_name}',
        }
        for s in settings:
            short_key = s['key'].replace('email.', '')
            result[short_key] = s['typedValue']
        return result

    # ========================================
    # Phase 30: 레이어 분리용 추가 메서드
    # ========================================

    def find_all_ordered(self) -> List[SystemSetting]:
        """모든 시스템 설정 조회 (Model 반환, key 순서)

        Phase 30: Service Layer 레이어 분리용 메서드

        Returns:
            SystemSetting 모델 리스트
        """
        return SystemSetting.query.order_by(SystemSetting.key).all()

    def find_by_key(self, key: str) -> Optional[SystemSetting]:
        """키로 시스템 설정 조회 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            key: 설정 키

        Returns:
            SystemSetting 모델 객체 또는 None
        """
        return SystemSetting.query.filter_by(key=key).first()

    def create_setting(
        self,
        key: str,
        value: str,
        description: str = '',
        commit: bool = True
    ) -> SystemSetting:
        """시스템 설정 생성 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            key: 설정 키
            value: 설정 값
            description: 설명
            commit: 커밋 여부

        Returns:
            SystemSetting 모델 객체
        """
        setting = SystemSetting(
            key=key,
            value=value,
            description=description
        )
        db.session.add(setting)
        if commit:
            db.session.commit()
        return setting


# 싱글톤 인스턴스
system_setting_repository = SystemSettingRepository()
