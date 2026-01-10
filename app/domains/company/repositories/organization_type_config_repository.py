"""
조직유형 설정 Repository

회사별 조직유형 설정의 CRUD 기능을 제공합니다.

Phase 4: 조직유형 설정 기능
"""
from typing import List, Optional, Dict
from app.database import db
from app.domains.company.models import OrganizationTypeConfig
from app.shared.repositories.base_repository import BaseRepository


class OrganizationTypeConfigRepository(BaseRepository[OrganizationTypeConfig]):
    """조직유형 설정 Repository"""

    def __init__(self):
        super().__init__(OrganizationTypeConfig)

    def get_by_company(self, company_id: int) -> List[OrganizationTypeConfig]:
        """회사별 조직유형 목록 조회 (정렬순)"""
        return OrganizationTypeConfig.query.filter_by(
            company_id=company_id
        ).order_by(OrganizationTypeConfig.sort_order).all()

    def get_active_types(self, company_id: int) -> List[OrganizationTypeConfig]:
        """회사별 조직유형 조회 (is_active 제거됨, 모든 유형 반환)"""
        return OrganizationTypeConfig.query.filter_by(
            company_id=company_id
        ).order_by(OrganizationTypeConfig.sort_order).all()

    def get_by_code(self, company_id: int, type_code: str) -> Optional[OrganizationTypeConfig]:
        """회사와 코드로 조직유형 조회"""
        return OrganizationTypeConfig.query.filter_by(
            company_id=company_id,
            type_code=type_code
        ).first()

    def exists_for_company(self, company_id: int) -> bool:
        """회사에 조직유형 설정이 있는지 확인"""
        return OrganizationTypeConfig.query.filter_by(
            company_id=company_id
        ).count() > 0

    def create_defaults(self, company_id: int, commit: bool = True) -> List[OrganizationTypeConfig]:
        """회사에 기본 조직유형 생성"""
        configs = OrganizationTypeConfig.create_defaults_for_company(company_id)
        for config in configs:
            db.session.add(config)
        if commit:
            db.session.commit()
        return configs

    def update_labels(self, config_id: int, label_ko: str = None, label_en: str = None,
                       commit: bool = True) -> Optional[OrganizationTypeConfig]:
        """조직유형 라벨 수정 (한글명, 영문명)"""
        config = self.find_by_id(config_id)
        if config:
            if label_ko is not None:
                config.type_label_ko = label_ko
            if label_en is not None:
                config.type_label_en = label_en
            if commit:
                db.session.commit()
        return config

    def update_icon(self, config_id: int, icon: str, commit: bool = True) -> Optional[OrganizationTypeConfig]:
        """조직유형 아이콘 수정"""
        config = self.find_by_id(config_id)
        if config:
            config.icon = icon
            if commit:
                db.session.commit()
        return config

    def update_sort_order(self, config_id: int, sort_order: int,
                          commit: bool = True) -> Optional[OrganizationTypeConfig]:
        """조직유형 정렬 순서 수정"""
        config = self.find_by_id(config_id)
        if config:
            config.sort_order = sort_order
            if commit:
                db.session.commit()
        return config

    def reorder_types(self, company_id: int, type_ids: List[int],
                      commit: bool = True) -> List[OrganizationTypeConfig]:
        """조직유형 순서 일괄 변경"""
        configs = []
        for idx, config_id in enumerate(type_ids):
            config = self.find_by_id(config_id)
            if config and config.company_id == company_id:
                config.sort_order = idx
                configs.append(config)
        if commit:
            db.session.commit()
        return configs

    def reset_to_default(self, company_id: int, commit: bool = True) -> List[OrganizationTypeConfig]:
        """기본값으로 복원 (기존 설정 삭제 후 재생성)"""
        # 기존 설정 삭제
        OrganizationTypeConfig.query.filter_by(company_id=company_id).delete()
        # 기본값 재생성
        return self.create_defaults(company_id, commit=commit)

    def get_statistics(self, company_id: int) -> Dict:
        """조직유형 통계"""
        all_types = self.get_by_company(company_id)
        return {
            'total': len(all_types),
        }

    def get_usage_count(self, company_id: int, type_code: str) -> int:
        """특정 조직유형을 사용하는 조직 개수 조회

        Organization은 company_id가 없고 트리 구조로 되어 있음.
        Company의 root_organization_id를 통해 해당 회사 소속 조직을 조회해야 함.
        """
        from app.domains.company.models import Organization, Company

        # 회사의 root_organization_id 조회
        company = Company.query.filter_by(id=company_id).first()
        if not company or not company.root_organization_id:
            return 0

        # 해당 회사 조직 트리의 모든 조직 ID 조회 (root 포함)
        def get_all_descendant_ids(root_id: int) -> set:
            """재귀적으로 모든 하위 조직 ID 조회"""
            result = {root_id}
            children = Organization.query.filter_by(parent_id=root_id).all()
            for child in children:
                result.update(get_all_descendant_ids(child.id))
            return result

        org_ids = get_all_descendant_ids(company.root_organization_id)

        # 해당 조직들 중 type_code를 사용하는 조직 수 조회
        return Organization.query.filter(
            Organization.id.in_(org_ids),
            Organization.org_type == type_code
        ).count()

    def delete_type(self, config_id: int, commit: bool = True) -> bool:
        """조직유형 삭제"""
        config = self.find_by_id(config_id)
        if not config:
            return False
        db.session.delete(config)
        if commit:
            db.session.commit()
        return True

    def create_type(
        self,
        company_id: int,
        type_code: str,
        type_label_ko: str,
        type_label_en: Optional[str] = None,
        icon: str = 'fa-folder',
        level: int = 1,
        sort_order: int = 0,
        commit: bool = True
    ) -> Optional[OrganizationTypeConfig]:
        """새 조직유형 생성"""
        config = OrganizationTypeConfig(
            company_id=company_id,
            type_code=type_code,
            type_label_ko=type_label_ko,
            type_label_en=type_label_en,
            icon=icon,
            level=level,
            sort_order=sort_order
        )
        db.session.add(config)
        if commit:
            db.session.commit()
        return config


# 싱글톤 인스턴스
organization_type_config_repository = OrganizationTypeConfigRepository()
