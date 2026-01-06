"""
조직 서비스

조직 구조 CRUD 및 트리 관리 비즈니스 로직을 제공합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Phase 2: Service 계층 표준화
Phase 24: Option A 레이어 분리 - Service는 Dict 반환 표준화
"""
from typing import Dict, List, Optional, Any


class OrganizationService:
    """
    조직 서비스

    조직 구조 CRUD 및 트리 관리 기능을 제공합니다.
    """

    @property
    def organization_repo(self):
        """지연 초기화된 조직 Repository"""
        from app.domains.company import get_organization_repo
        return get_organization_repo()

    # ========================================
    # 조직 조회
    # ========================================

    def get_tree(self, root_organization_id: int = None) -> List[Dict]:
        """조직 트리 조회

        Args:
            root_organization_id: 루트 조직 ID

        Returns:
            조직 트리 목록
        """
        return self.organization_repo.get_tree(root_organization_id=root_organization_id)

    def get_flat_list(self, root_organization_id: int = None) -> List[Dict]:
        """조직 평탄화 목록 조회

        Args:
            root_organization_id: 루트 조직 ID

        Returns:
            조직 목록
        """
        return self.organization_repo.get_flat_list(root_organization_id=root_organization_id)

    def get_organization_statistics(self, root_organization_id: int = None) -> Dict:
        """조직 통계 조회

        Args:
            root_organization_id: 루트 조직 ID

        Returns:
            통계 Dict
        """
        return self.organization_repo.get_organization_statistics(root_organization_id=root_organization_id)

    def get_by_id(self, org_id: int) -> Optional[Dict]:
        """조직 ID로 조회 (Dict 반환)

        Phase 24: find_by_id() + to_dict() 패턴 적용

        Args:
            org_id: 조직 ID

        Returns:
            조직 Dict 또는 None
        """
        model = self.organization_repo.find_by_id(org_id)
        return model.to_dict() if model else None

    def get_children(self, org_id: int, root_organization_id: int = None) -> List[Dict]:
        """하위 조직 조회

        Args:
            org_id: 조직 ID
            root_organization_id: 루트 조직 ID

        Returns:
            하위 조직 목록
        """
        return self.organization_repo.get_children(org_id, root_organization_id=root_organization_id)

    def search(self, query: str, root_organization_id: int = None) -> List[Dict]:
        """조직 검색

        Args:
            query: 검색어
            root_organization_id: 루트 조직 ID

        Returns:
            검색 결과 목록
        """
        return self.organization_repo.search(query, root_organization_id=root_organization_id)

    # ========================================
    # 조직 검증
    # ========================================

    def verify_ownership(self, org_id: int, root_organization_id: int) -> bool:
        """조직 소유권 검증

        Args:
            org_id: 조직 ID
            root_organization_id: 루트 조직 ID

        Returns:
            소유권 여부
        """
        return self.organization_repo.verify_ownership(org_id, root_organization_id)

    def code_exists(self, code: str, exclude_id: int = None, root_organization_id: int = None) -> bool:
        """조직 코드 중복 검사

        Args:
            code: 조직 코드
            exclude_id: 제외할 조직 ID
            root_organization_id: 루트 조직 ID

        Returns:
            중복 여부
        """
        return self.organization_repo.code_exists(code, exclude_id=exclude_id, root_organization_id=root_organization_id)

    # ========================================
    # 조직 CRUD
    # ========================================

    def create_organization(self, name: str, org_type: str, parent_id: int = None,
                            code: str = None, manager_id: int = None,
                            description: str = None, root_organization_id: int = None) -> Any:
        """조직 생성

        Args:
            name: 조직명
            org_type: 조직 유형
            parent_id: 상위 조직 ID
            code: 조직 코드
            manager_id: 책임자 ID
            description: 설명
            root_organization_id: 루트 조직 ID

        Returns:
            생성된 Organization 객체
        """
        return self.organization_repo.create_organization(
            name=name,
            org_type=org_type,
            parent_id=parent_id,
            code=code,
            manager_id=manager_id,
            description=description,
            root_organization_id=root_organization_id
        )

    def update_organization(self, org_id: int, data: Dict, root_organization_id: int = None) -> Optional[Any]:
        """조직 수정

        Args:
            org_id: 조직 ID
            data: 수정할 데이터
            root_organization_id: 루트 조직 ID

        Returns:
            수정된 Organization 객체 또는 None
        """
        return self.organization_repo.update_organization(org_id, data, root_organization_id=root_organization_id)

    def deactivate(self, org_id: int, cascade: bool = False, root_organization_id: int = None) -> bool:
        """조직 비활성화

        Args:
            org_id: 조직 ID
            cascade: 하위 조직 포함 비활성화 여부
            root_organization_id: 루트 조직 ID

        Returns:
            성공 여부
        """
        return self.organization_repo.deactivate(org_id, cascade=cascade, root_organization_id=root_organization_id)

    def move_organization(self, org_id: int, new_parent_id: int, root_organization_id: int = None) -> bool:
        """조직 이동

        Args:
            org_id: 조직 ID
            new_parent_id: 새 상위 조직 ID
            root_organization_id: 루트 조직 ID

        Returns:
            성공 여부
        """
        return self.organization_repo.move_organization(org_id, new_parent_id, root_organization_id=root_organization_id)


# 싱글톤 인스턴스
organization_service = OrganizationService()
