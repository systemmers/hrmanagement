"""
조직유형 설정 Service

회사별 조직유형 설정의 비즈니스 로직을 제공합니다.
SSOT: 조직유형 설정 관련 모든 비즈니스 로직의 단일 소스

Phase 4: 조직유형 설정 기능
"""
from typing import List, Optional, Dict
from app.domains.company.repositories import organization_type_config_repository
from app.domains.company.models import OrganizationTypeConfig
from app.shared.utils.transaction import atomic_transaction


class OrganizationTypeConfigService:
    """조직유형 설정 서비스"""

    def __init__(self):
        self.repo = organization_type_config_repository

    def get_by_company(self, company_id: int) -> List[Dict]:
        """회사별 조직유형 목록 조회"""
        configs = self.repo.get_by_company(company_id)
        return [c.to_dict() for c in configs]

    def get_active_types(self, company_id: int) -> List[Dict]:
        """회사별 활성화된 조직유형만 조회"""
        configs = self.repo.get_active_types(company_id)
        return [c.to_dict() for c in configs]

    def get_active_type_models(self, company_id: int) -> List[OrganizationTypeConfig]:
        """회사별 활성화된 조직유형 모델 목록 조회 (내부용)"""
        return self.repo.get_active_types(company_id)

    def get_by_id(self, config_id: int) -> Optional[Dict]:
        """ID로 조직유형 조회"""
        config = self.repo.find_by_id(config_id)
        return config.to_dict() if config else None

    def ensure_defaults_exist(self, company_id: int) -> List[Dict]:
        """회사에 기본 조직유형이 없으면 생성 (Lazy Initialization)"""
        if not self.repo.exists_for_company(company_id):
            with atomic_transaction():
                configs = self.repo.create_defaults(company_id, commit=False)
            return [c.to_dict() for c in configs]
        return self.get_by_company(company_id)

    def initialize_for_company(self, company_id: int) -> List[Dict]:
        """회사 생성 시 기본 조직유형 초기화"""
        with atomic_transaction():
            configs = self.repo.create_defaults(company_id, commit=False)
        return [c.to_dict() for c in configs]

    def update_labels(self, config_id: int, label_ko: str = None, label_en: str = None) -> Optional[Dict]:
        """조직유형 라벨 수정 (한글명, 영문명)"""
        with atomic_transaction():
            config = self.repo.update_labels(
                config_id,
                label_ko=label_ko.strip() if label_ko else None,
                label_en=label_en.strip() if label_en else None,
                commit=False
            )
        return config.to_dict() if config else None

    def update_config(self, config_id: int, data: Dict) -> Optional[Dict]:
        """조직유형 설정 업데이트 (라벨, 아이콘)"""
        from app.database import db

        config = self.repo.find_by_id(config_id)
        if not config:
            return None

        # 직접 속성 수정 후 commit (같은 세션 유지)
        if 'type_label_ko' in data:
            config.type_label_ko = data['type_label_ko'].strip()
        if 'type_label_en' in data:
            config.type_label_en = data['type_label_en'].strip() if data['type_label_en'] else None
        if 'icon' in data:
            config.icon = data['icon']
        db.session.commit()

        return config.to_dict()

    def update_icon(self, config_id: int, icon: str) -> Optional[Dict]:
        """조직유형 아이콘 수정"""
        with atomic_transaction():
            config = self.repo.update_icon(config_id, icon, commit=False)
        return config.to_dict() if config else None

    def reorder_types(self, company_id: int, type_ids: List[int]) -> List[Dict]:
        """조직유형 순서 일괄 변경"""
        with atomic_transaction():
            configs = self.repo.reorder_types(company_id, type_ids, commit=False)
        return [c.to_dict() for c in configs]

    def reset_to_default(self, company_id: int) -> List[Dict]:
        """기본값으로 복원"""
        with atomic_transaction():
            configs = self.repo.reset_to_default(company_id, commit=False)
        return [c.to_dict() for c in configs]

    def get_statistics(self, company_id: int) -> Dict:
        """조직유형 통계"""
        return self.repo.get_statistics(company_id)

    def verify_ownership(self, config_id: int, company_id: int) -> bool:
        """특정 설정이 해당 회사 소속인지 확인"""
        config = self.repo.find_by_id(config_id)
        if not config:
            return False
        return config.company_id == company_id

    def create_config(self, company_id: int, data: Dict) -> Dict:
        """새 조직유형 생성

        Args:
            company_id: 회사 ID
            data: {'type_label_ko': '필수', 'type_label_en': '선택', 'icon': '선택'}

        Returns:
            Dict: {'success': True, 'data': {...}} 또는 {'success': False, 'error': '...'}
        """
        type_label_ko = data.get('type_label_ko', '').strip()
        type_label_en = data.get('type_label_en', '').strip() if data.get('type_label_en') else None
        icon = data.get('icon', 'fa-folder')

        if not type_label_ko:
            return {'success': False, 'error': '한글명은 필수입니다.'}

        # type_code 자동 생성 (custom_N 형식)
        existing_types = self.repo.get_by_company(company_id)
        custom_count = sum(1 for t in existing_types if t.type_code.startswith('custom_'))
        type_code = f'custom_{custom_count + 1}'

        # 중복 체크
        for t in existing_types:
            if t.type_label_ko == type_label_ko:
                return {'success': False, 'error': '이미 동일한 한글명의 조직유형이 있습니다.'}

        # sort_order 계산 (마지막 + 1)
        max_sort_order = max((t.sort_order for t in existing_types), default=0)
        sort_order = max_sort_order + 1

        # level 계산 (sort_order와 동일하게)
        level = sort_order

        with atomic_transaction():
            config = self.repo.create_type(
                company_id=company_id,
                type_code=type_code,
                type_label_ko=type_label_ko,
                type_label_en=type_label_en,
                icon=icon,
                level=level,
                sort_order=sort_order,
                commit=False
            )

        if config:
            return {'success': True, 'data': config.to_dict()}
        return {'success': False, 'error': '조직유형 생성에 실패했습니다.'}

    def delete_config(self, config_id: int, company_id: int) -> Dict:
        """조직유형 삭제 (사용 중인 조직이 없는 경우만)

        Returns:
            Dict: {'success': True} 또는 {'success': False, 'error': '에러 메시지'}
        """
        config = self.repo.find_by_id(config_id)
        if not config:
            return {'success': False, 'error': '조직유형을 찾을 수 없습니다.'}

        if config.company_id != company_id:
            return {'success': False, 'error': '조직유형을 찾을 수 없습니다.'}

        # 사용 중인 조직 확인
        usage_count = self.repo.get_usage_count(company_id, config.type_code)
        if usage_count > 0:
            return {
                'success': False,
                'error': f'이 조직유형을 사용 중인 조직이 {usage_count}개 있어 삭제할 수 없습니다.'
            }

        # 삭제 실행
        with atomic_transaction():
            success = self.repo.delete_type(config_id, commit=False)

        if success:
            return {'success': True}
        return {'success': False, 'error': '조직유형 삭제에 실패했습니다.'}

    def get_type_options_for_select(self, company_id: int) -> List[Dict]:
        """조직 추가/수정 모달의 select 옵션용 데이터"""
        # 먼저 기본값 보장
        self.ensure_defaults_exist(company_id)
        # 모든 유형 반환 (is_active 제거됨)
        active_types = self.repo.get_active_types(company_id)
        return [
            {
                'value': t.type_code,
                'label': t.type_label_ko,
                'label_ko': t.type_label_ko,
                'label_en': t.type_label_en,
                'icon': t.icon,
            }
            for t in active_types
        ]


# 싱글톤 인스턴스
organization_type_config_service = OrganizationTypeConfigService()
