"""
Organization Repository

조직 데이터의 CRUD 및 트리 구조 관련 기능을 제공합니다.
"""
from typing import List, Optional, Dict
from app.database import db
from app.models.organization import Organization
from .base_repository import BaseRepository


class OrganizationRepository(BaseRepository):
    """조직 저장소"""

    def __init__(self):
        super().__init__(Organization)

    def get_by_code(self, code: str) -> Optional[Organization]:
        """조직 코드로 조회"""
        return Organization.query.filter_by(code=code, is_active=True).first()

    def get_root_organizations(self) -> List[Dict]:
        """최상위 조직 목록 (parent_id가 없는 조직)"""
        orgs = Organization.query.filter_by(
            parent_id=None, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict() for org in orgs]

    def get_children(self, parent_id: int) -> List[Dict]:
        """특정 조직의 하위 조직 목록"""
        orgs = Organization.query.filter_by(
            parent_id=parent_id, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict() for org in orgs]

    def get_tree(self) -> List[Dict]:
        """전체 조직 트리 구조 반환"""
        root_orgs = Organization.query.filter_by(
            parent_id=None, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict(include_children=True) for org in root_orgs]

    def get_flat_list(self, include_inactive=False) -> List[Dict]:
        """전체 조직 목록 (플랫 리스트, 경로 포함)"""
        query = Organization.query
        if not include_inactive:
            query = query.filter_by(is_active=True)

        orgs = query.order_by(
            Organization.parent_id.nullsfirst(),
            Organization.sort_order
        ).all()

        return [org.to_dict(include_path=True) for org in orgs]

    def get_by_type(self, org_type: str) -> List[Dict]:
        """조직 유형별 조회"""
        orgs = Organization.query.filter_by(
            org_type=org_type, is_active=True
        ).order_by(Organization.sort_order).all()
        return [org.to_dict() for org in orgs]

    def get_departments(self) -> List[Dict]:
        """부서 목록 조회"""
        return self.get_by_type(Organization.TYPE_DEPARTMENT)

    def get_teams(self) -> List[Dict]:
        """팀 목록 조회"""
        return self.get_by_type(Organization.TYPE_TEAM)

    def get_ancestors(self, org_id: int) -> List[Dict]:
        """상위 조직 경로 조회"""
        org = Organization.query.get(org_id)
        if not org:
            return []
        ancestors = org.get_ancestors()
        return [a.to_dict() for a in ancestors]

    def get_descendants(self, org_id: int) -> List[Dict]:
        """하위 조직 목록 조회 (모든 자손)"""
        org = Organization.query.get(org_id)
        if not org:
            return []
        descendants = org.get_descendants()
        return [d.to_dict() for d in descendants]

    def create_organization(self, name: str, org_type: str,
                            parent_id: int = None, code: str = None,
                            manager_id: int = None, description: str = None) -> Organization:
        """새 조직 생성"""
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

    def update_organization(self, org_id: int, data: Dict) -> Optional[Organization]:
        """조직 정보 수정"""
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
            # 순환 참조 방지
            if data['parent_id'] != org_id:
                org.parent_id = data['parent_id']
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

    def move_organization(self, org_id: int, new_parent_id: int) -> bool:
        """조직 이동 (상위 조직 변경)"""
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

    def reorder_children(self, parent_id: int, org_ids: List[int]) -> bool:
        """하위 조직 순서 변경"""
        for order, org_id in enumerate(org_ids):
            org = Organization.query.get(org_id)
            if org and org.parent_id == parent_id:
                org.sort_order = order
        db.session.commit()
        return True

    def deactivate(self, org_id: int, cascade: bool = False) -> bool:
        """조직 비활성화"""
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

    def activate(self, org_id: int) -> bool:
        """조직 활성화"""
        org = Organization.query.get(org_id)
        if not org:
            return False

        org.is_active = True
        db.session.commit()
        return True

    def get_organization_statistics(self) -> Dict:
        """조직 통계"""
        total = Organization.query.filter_by(is_active=True).count()
        by_type = {}
        for org_type in Organization.VALID_TYPES:
            count = Organization.query.filter_by(org_type=org_type, is_active=True).count()
            by_type[org_type] = count

        return {
            'total': total,
            'by_type': by_type,
        }

    def search(self, query: str) -> List[Dict]:
        """조직 검색 (이름, 코드)"""
        orgs = Organization.query.filter(
            Organization.is_active == True,
            db.or_(
                Organization.name.ilike(f'%{query}%'),
                Organization.code.ilike(f'%{query}%')
            )
        ).order_by(Organization.name).all()
        return [org.to_dict(include_path=True) for org in orgs]

    def code_exists(self, code: str, exclude_id: int = None) -> bool:
        """조직 코드 중복 확인"""
        query = Organization.query.filter_by(code=code)
        if exclude_id:
            query = query.filter(Organization.id != exclude_id)
        return query.first() is not None
