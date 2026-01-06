"""
Organization Repository

조직 데이터의 CRUD 및 트리 구조 관련 기능을 제공합니다.
멀티테넌시: root_organization_id를 기준으로 해당 조직과 하위 조직만 접근 가능합니다.

Phase 7: 도메인 중심 마이그레이션 완료
"""
from typing import List, Optional, Dict, Set
from app.database import db
from app.models.organization import Organization
from app.repositories.base_repository import BaseRepository
from app.repositories.mixins import TenantFilterMixin


class OrganizationRepository(BaseRepository[Organization], TenantFilterMixin):
    """조직 저장소 - 멀티테넌시 지원 (TenantFilterMixin)"""

    def __init__(self):
        super().__init__(Organization)

    def _get_descendant_ids(self, root_org_id: int) -> Set[int]:
        """특정 조직과 모든 하위 조직의 ID 집합 반환 (멀티테넌시 필터용)

        [DEPRECATED] TenantFilterMixin.get_tenant_org_ids() 사용 권장
        """
        return self.get_tenant_org_ids(root_org_id)

    def _filter_by_tenant(self, query, root_organization_id: int = None):
        """쿼리에 멀티테넌시 필터 적용

        [DEPRECATED] TenantFilterMixin.apply_tenant_filter() 사용 권장
        """
        if root_organization_id:
            return self.apply_tenant_filter(query, Organization.id, root_organization_id)
        return query

    def verify_ownership(self, org_id: int, root_organization_id: int) -> bool:
        """특정 조직이 해당 테넌트 소속인지 확인"""
        return self.verify_tenant_ownership(org_id, root_organization_id)

    def get_by_code(self, code: str, root_organization_id: int = None) -> Optional[Organization]:
        """조직 코드로 조회"""
        query = Organization.query.filter_by(code=code, is_active=True)
        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            query = query.filter(Organization.id.in_(allowed_ids))
        return query.first()

    def get_root_organizations(self, root_organization_id: int = None) -> List[Dict]:
        """최상위 조직 목록 (멀티테넌시: 해당 회사의 루트 조직)"""
        if root_organization_id:
            org = Organization.query.filter_by(
                id=root_organization_id, is_active=True
            ).first()
            return [org.to_dict()] if org else []

        orgs = Organization.query.filter_by(
            parent_id=None, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict() for org in orgs]

    def get_children(self, parent_id: int, root_organization_id: int = None) -> List[Dict]:
        """특정 조직의 하위 조직 목록"""
        if root_organization_id and not self.verify_ownership(parent_id, root_organization_id):
            return []

        orgs = Organization.query.filter_by(
            parent_id=parent_id, is_active=True
        ).order_by(Organization.sort_order).all()

        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            orgs = [org for org in orgs if org.id in allowed_ids]

        return [org.to_dict() for org in orgs]

    def get_tree(self, root_organization_id: int = None) -> List[Dict]:
        """조직 트리 구조 반환 (멀티테넌시: 해당 회사의 루트 조직부터)"""
        if root_organization_id:
            root_org = Organization.query.filter_by(
                id=root_organization_id, is_active=True
            ).first()
            return [root_org.to_dict(include_children=True)] if root_org else []

        root_orgs = Organization.query.filter_by(
            parent_id=None, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict(include_children=True) for org in root_orgs]

    def get_flat_list(self, include_inactive=False, root_organization_id: int = None) -> List[Dict]:
        """전체 조직 목록 (플랫 리스트, 경로 포함)"""
        query = Organization.query
        if not include_inactive:
            query = query.filter_by(is_active=True)

        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            if allowed_ids:
                query = query.filter(Organization.id.in_(allowed_ids))
            else:
                return []

        orgs = query.order_by(
            Organization.parent_id.nullsfirst(),
            Organization.sort_order
        ).all()

        return [org.to_dict(include_path=True) for org in orgs]

    def get_by_type(self, org_type: str, root_organization_id: int = None) -> List[Dict]:
        """조직 유형별 조회"""
        query = Organization.query.filter_by(org_type=org_type, is_active=True)

        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            if allowed_ids:
                query = query.filter(Organization.id.in_(allowed_ids))
            else:
                return []

        orgs = query.order_by(Organization.sort_order).all()
        return [org.to_dict() for org in orgs]

    def get_departments(self, root_organization_id: int = None) -> List[Dict]:
        """부서 목록 조회"""
        return self.get_by_type(Organization.TYPE_DEPARTMENT, root_organization_id)

    def get_teams(self, root_organization_id: int = None) -> List[Dict]:
        """팀 목록 조회"""
        return self.get_by_type(Organization.TYPE_TEAM, root_organization_id)

    def get_ancestors(self, org_id: int, root_organization_id: int = None) -> List[Dict]:
        """상위 조직 경로 조회"""
        if root_organization_id and not self.verify_ownership(org_id, root_organization_id):
            return []
        org = Organization.query.get(org_id)
        if not org:
            return []
        ancestors = org.get_ancestors()
        return [a.to_dict() for a in ancestors]

    def get_descendants(self, org_id: int, root_organization_id: int = None) -> List[Dict]:
        """하위 조직 목록 조회 (모든 자손)"""
        if root_organization_id and not self.verify_ownership(org_id, root_organization_id):
            return []
        org = Organization.query.get(org_id)
        if not org:
            return []
        descendants = org.get_descendants()
        return [d.to_dict() for d in descendants]

    def create_organization(self, name: str, org_type: str,
                            parent_id: int = None, code: str = None,
                            manager_id: int = None, description: str = None,
                            root_organization_id: int = None) -> Organization:
        """새 조직 생성 (멀티테넌시: parent_id가 해당 테넌트 소속인지 검증)"""
        # 멀티테넌시 검증: parent_id가 지정된 경우 해당 테넌트 소속인지 확인
        if root_organization_id and parent_id:
            if not self.verify_ownership(parent_id, root_organization_id):
                raise ValueError("상위 조직이 현재 회사에 속하지 않습니다.")

        # 정렬 순서 자동 설정 (같은 레벨의 마지막)
        max_order = db.session.query(db.func.max(Organization.sort_order)).filter_by(
            parent_id=parent_id
        ).scalar() or 0

        org = Organization(
            name=name,
            code=code,
            org_type=org_type,
            parent_id=parent_id,
            manager_id=manager_id,
            sort_order=max_order + 1,
            description=description,
        )
        db.session.add(org)
        db.session.commit()
        return org

    def update_organization(self, org_id: int, data: Dict,
                            root_organization_id: int = None) -> Optional[Organization]:
        """조직 정보 수정 (멀티테넌시: 해당 테넌트 소속 조직만 수정 가능)"""
        if root_organization_id and not self.verify_ownership(org_id, root_organization_id):
            return None

        org = Organization.query.get(org_id)
        if not org:
            return None

        if 'name' in data:
            org.name = data['name']
        if 'code' in data:
            org.code = data['code']
        if 'org_type' in data:
            org.org_type = data['org_type']
        if 'parent_id' in data:
            # 순환 참조 방지 및 멀티테넌시 검증
            new_parent_id = data['parent_id']
            if new_parent_id != org_id:
                if root_organization_id and new_parent_id:
                    if not self.verify_ownership(new_parent_id, root_organization_id):
                        raise ValueError("상위 조직이 현재 회사에 속하지 않습니다.")
                org.parent_id = new_parent_id
        if 'manager_id' in data:
            org.manager_id = data['manager_id']
        if 'sort_order' in data:
            org.sort_order = data['sort_order']
        if 'description' in data:
            org.description = data['description']
        if 'is_active' in data:
            org.is_active = data['is_active']

        db.session.commit()
        return org

    def move_organization(self, org_id: int, new_parent_id: int,
                          root_organization_id: int = None) -> bool:
        """조직 이동 (상위 조직 변경, 멀티테넌시 적용)"""
        if root_organization_id:
            if not self.verify_ownership(org_id, root_organization_id):
                return False
            if new_parent_id and not self.verify_ownership(new_parent_id, root_organization_id):
                return False

        org = Organization.query.get(org_id)
        if not org:
            return False

        # 자기 자신을 상위로 설정하거나 자손을 상위로 설정하는 것 방지
        if new_parent_id:
            new_parent = Organization.query.get(new_parent_id)
            if not new_parent:
                return False

            # 순환 참조 체크
            descendants = org.get_descendants()
            if new_parent in descendants:
                return False

        org.parent_id = new_parent_id

        # 정렬 순서 재설정
        max_order = db.session.query(db.func.max(Organization.sort_order)).filter_by(
            parent_id=new_parent_id
        ).scalar() or 0
        org.sort_order = max_order + 1

        db.session.commit()
        return True

    def reorder_children(self, parent_id: int, org_ids: List[int],
                         root_organization_id: int = None) -> bool:
        """하위 조직 순서 변경 (멀티테넌시 적용)"""
        if root_organization_id and not self.verify_ownership(parent_id, root_organization_id):
            return False

        for order, org_id in enumerate(org_ids):
            org = Organization.query.get(org_id)
            if org and org.parent_id == parent_id:
                org.sort_order = order
        db.session.commit()
        return True

    def deactivate(self, org_id: int, cascade: bool = False,
                   root_organization_id: int = None) -> bool:
        """조직 비활성화 (멀티테넌시 적용)"""
        if root_organization_id and not self.verify_ownership(org_id, root_organization_id):
            return False

        org = Organization.query.get(org_id)
        if not org:
            return False

        org.is_active = False

        # 하위 조직도 비활성화
        if cascade:
            for descendant in org.get_descendants():
                descendant.is_active = False

        db.session.commit()
        return True

    def activate(self, org_id: int, root_organization_id: int = None) -> bool:
        """조직 활성화 (멀티테넌시 적용)"""
        if root_organization_id and not self.verify_ownership(org_id, root_organization_id):
            return False

        org = Organization.query.get(org_id)
        if not org:
            return False

        org.is_active = True
        db.session.commit()
        return True

    def get_organization_statistics(self, root_organization_id: int = None) -> Dict:
        """조직 통계 (멀티테넌시 적용)"""
        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            if not allowed_ids:
                return {'total': 0, 'by_type': {t: 0 for t in Organization.VALID_TYPES}}

            total = Organization.query.filter(
                Organization.is_active == True,
                Organization.id.in_(allowed_ids)
            ).count()

            by_type = {}
            for org_type in Organization.VALID_TYPES:
                count = Organization.query.filter(
                    Organization.org_type == org_type,
                    Organization.is_active == True,
                    Organization.id.in_(allowed_ids)
                ).count()
                by_type[org_type] = count
        else:
            total = Organization.query.filter_by(is_active=True).count()
            by_type = {}
            for org_type in Organization.VALID_TYPES:
                count = Organization.query.filter_by(org_type=org_type, is_active=True).count()
                by_type[org_type] = count

        return {
            'total': total,
            'by_type': by_type,
        }

    def search(self, query: str, root_organization_id: int = None) -> List[Dict]:
        """조직 검색 (이름, 코드, 멀티테넌시 적용)"""
        q = Organization.query.filter(
            Organization.is_active == True,
            db.or_(
                Organization.name.ilike(f'%{query}%'),
                Organization.code.ilike(f'%{query}%')
            )
        )

        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            if allowed_ids:
                q = q.filter(Organization.id.in_(allowed_ids))
            else:
                return []

        orgs = q.order_by(Organization.name).all()
        return [org.to_dict(include_path=True) for org in orgs]

    def code_exists(self, code: str, exclude_id: int = None,
                    root_organization_id: int = None) -> bool:
        """조직 코드 중복 확인 (멀티테넌시: 해당 테넌트 범위 내에서 확인)"""
        query = Organization.query.filter_by(code=code)
        if exclude_id:
            query = query.filter(Organization.id != exclude_id)

        if root_organization_id:
            allowed_ids = self._get_descendant_ids(root_organization_id)
            if allowed_ids:
                query = query.filter(Organization.id.in_(allowed_ids))
            else:
                return False

        return query.first() is not None


# 싱글톤 인스턴스
organization_repository = OrganizationRepository()
