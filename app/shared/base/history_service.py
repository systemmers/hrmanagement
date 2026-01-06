"""
BaseHistoryService

이력 데이터(학력, 경력, 자격증, 어학, 병역, 가족) CRUD 공통 로직을 제공합니다.
EmployeeService와 PersonalService에서 공통으로 사용할 수 있는 패턴입니다.

Phase 2 리팩토링: Strategy 패턴 적용
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from typing import Dict, List, Optional, Tuple, Type, Callable
from app.database import db


class BaseHistoryService:
    """
    이력 데이터 CRUD 공통 서비스

    사용 예시:
        history_service = BaseHistoryService()

        # 학력 추가
        education = history_service.add_item(
            repository=self.education_repo,
            owner_id=profile_id,
            data=education_data,
            owner_field='profile_id'  # 또는 'employee_id'
        )

        # 학력 목록 조회
        educations = history_service.get_items(
            repository=self.education_repo,
            owner_id=profile_id,
            owner_field='profile_id'
        )
    """

    def get_items(self, repository, owner_id: int, owner_field: str = 'profile_id') -> List[Dict]:
        """
        이력 데이터 목록 조회

        Args:
            repository: BaseProfileRelationRepository 또는 BaseRelationRepository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            owner_field: 'profile_id' 또는 'employee_id'

        Returns:
            이력 데이터 딕셔너리 리스트
        """
        if owner_field == 'profile_id':
            models = repository.find_by_profile_id(owner_id)
        else:
            models = repository.find_by_employee_id(owner_id)
        return [m.to_dict() for m in models]

    def add_item(self, repository, owner_id: int, data: Dict,
                 owner_field: str = 'profile_id') -> Dict:
        """
        이력 데이터 추가

        Args:
            repository: Repository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            data: 추가할 데이터
            owner_field: 'profile_id' 또는 'employee_id'

        Returns:
            생성된 레코드의 딕셔너리
        """
        if owner_field == 'profile_id':
            record = repository.create(owner_id, data)
        else:
            record = repository.create_for_employee(owner_id, data)
        return record.to_dict() if hasattr(record, 'to_dict') else record

    def delete_item(self, repository, item_id: int, owner_id: int,
                    owner_field: str = 'profile_id', commit: bool = True) -> bool:
        """
        이력 데이터 삭제 (소유권 확인)

        Args:
            repository: Repository 인스턴스
            item_id: 삭제할 아이템 ID
            owner_id: 프로필 ID 또는 직원 ID
            owner_field: 'profile_id' 또는 'employee_id'
            commit: True면 즉시 커밋 (Phase 31)

        Returns:
            삭제 성공 여부
        """
        if owner_field == 'profile_id':
            return repository.delete_by_id_and_profile(item_id, owner_id, commit=commit)
        else:
            # Phase 31: Repository 패턴 적용
            return repository.delete_by_id_and_employee(item_id, owner_id, commit=commit)

    def delete_all_items(self, repository, owner_id: int,
                         owner_field: str = 'profile_id') -> int:
        """
        소유자의 모든 이력 데이터 삭제

        Args:
            repository: Repository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            owner_field: 'profile_id' 또는 'employee_id'

        Returns:
            삭제된 레코드 수
        """
        if owner_field == 'profile_id':
            return repository.delete_all_by_profile(owner_id)
        else:
            return repository.delete_by_employee_id(owner_id)

    def replace_all_items(self, repository, owner_id: int, items: List[Dict],
                          owner_field: str = 'profile_id',
                          create_method: Callable = None) -> List[Dict]:
        """
        소유자의 모든 이력 데이터를 새 데이터로 교체 (전체 삭제 후 재생성)

        EmployeeService의 _update_related_data 패턴을 일반화합니다.

        Args:
            repository: Repository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            items: 새로 추가할 데이터 리스트
            owner_field: 'profile_id' 또는 'employee_id'
            create_method: 커스텀 생성 메서드 (없으면 기본 add_item 사용)

        Returns:
            생성된 레코드들의 딕셔너리 리스트
        """
        # 기존 데이터 삭제
        self.delete_all_items(repository, owner_id, owner_field)

        # 새 데이터 추가
        results = []
        for item_data in items:
            if create_method:
                record = create_method(owner_id, item_data)
            else:
                record = self.add_item(repository, owner_id, item_data, owner_field)
            results.append(record)

        return results

    def upsert_single_item(self, repository, owner_id: int, data: Dict,
                           owner_field: str = 'profile_id') -> Dict:
        """
        1:1 관계 이력 데이터 저장/수정 (병역 정보 등)

        Args:
            repository: BaseProfileOneToOneRepository 또는 BaseOneToOneRepository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            data: 저장할 데이터
            owner_field: 'profile_id' 또는 'employee_id'

        Returns:
            저장된 레코드의 딕셔너리
        """
        if owner_field == 'profile_id':
            record = repository.save_for_profile(owner_id, data)
        else:
            record = repository.save_for_employee(owner_id, data)
        return record.to_dict() if hasattr(record, 'to_dict') else record

    def get_single_item(self, repository, owner_id: int,
                        owner_field: str = 'profile_id') -> Optional[Dict]:
        """
        1:1 관계 이력 데이터 조회 (병역 정보 등)

        Args:
            repository: BaseProfileOneToOneRepository 또는 BaseOneToOneRepository 인스턴스
            owner_id: 프로필 ID 또는 직원 ID
            owner_field: 'profile_id' 또는 'employee_id'

        Returns:
            레코드의 딕셔너리 또는 None
        """
        if owner_field == 'profile_id':
            record = repository.find_by_profile_id(owner_id)
        else:
            record = repository.find_by_employee_id(owner_id)
        return record.to_dict() if record and hasattr(record, 'to_dict') else record


# 싱글턴 인스턴스
history_service = BaseHistoryService()
