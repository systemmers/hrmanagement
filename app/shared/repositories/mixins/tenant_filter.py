"""
Tenant Filter Mixin

멀티테넌시 필터링을 위한 공통 로직을 제공합니다.
조직 계층 구조를 기반으로 데이터 접근 범위를 제한합니다.

SSOT: 멀티테넌시 조직 ID 조회 로직의 단일 진실 공급원
"""
from typing import Set, List


class TenantFilterMixin:
    """멀티테넌시 필터링 Mixin

    조직 계층 구조를 기반으로 특정 root_organization_id와
    그 하위 모든 조직의 ID를 조회하는 기능을 제공합니다.

    사용 예시:
        class EmployeeRepository(BaseRepository[Employee], TenantFilterMixin):
            def find_all(self, organization_id=None):
                if organization_id:
                    org_ids = self.get_tenant_org_ids(organization_id)
                    # org_ids를 사용하여 필터링
    """

    def get_tenant_org_ids(self, root_org_id: int) -> Set[int]:
        """루트 조직과 모든 하위 조직의 ID 집합 반환

        Args:
            root_org_id: 루트 조직 ID

        Returns:
            조직 ID 집합 (루트 포함). 루트가 없으면 빈 집합.
        """
        if not root_org_id:
            return set()

        from app.domains.company.models import Organization
        root_org = Organization.query.get(root_org_id)
        if not root_org:
            return set()

        # 루트 조직 ID + 모든 하위 조직 ID
        org_ids = {root_org_id}
        descendants = root_org.get_descendants()
        for desc in descendants:
            org_ids.add(desc.id)

        return org_ids

    def get_tenant_org_ids_list(self, root_org_id: int) -> List[int]:
        """루트 조직과 모든 하위 조직의 ID 목록 반환

        Args:
            root_org_id: 루트 조직 ID

        Returns:
            조직 ID 목록 (루트 포함). 루트가 없으면 빈 목록.

        Note:
            Set 대신 List가 필요한 경우 이 메서드 사용.
            내부적으로 get_tenant_org_ids()를 호출합니다.
        """
        return list(self.get_tenant_org_ids(root_org_id))

    def verify_tenant_ownership(self, org_id: int, root_org_id: int) -> bool:
        """특정 조직이 해당 테넌트에 속하는지 확인

        Args:
            org_id: 확인할 조직 ID
            root_org_id: 루트 조직 ID (테넌트 식별자)

        Returns:
            해당 테넌트에 속하면 True, 아니면 False
        """
        if not root_org_id:
            return False
        allowed_ids = self.get_tenant_org_ids(root_org_id)
        return org_id in allowed_ids

    def apply_tenant_filter(self, query, org_field, root_org_id: int):
        """쿼리에 멀티테넌시 필터 적용

        Args:
            query: SQLAlchemy Query 객체
            org_field: 필터링할 조직 ID 필드 (예: Employee.organization_id)
            root_org_id: 루트 조직 ID

        Returns:
            필터가 적용된 Query 객체

        Example:
            query = Employee.query
            query = self.apply_tenant_filter(query, Employee.organization_id, root_org_id)
        """
        if not root_org_id:
            return query

        org_ids = self.get_tenant_org_ids(root_org_id)
        if org_ids:
            return query.filter(org_field.in_(org_ids))
        else:
            # 조직이 없으면 빈 결과 반환
            from app.database import db
            return query.filter(db.false())
