"""
Generic Relation CRUD - 관계형 데이터 CRUD 공통 패턴

Phase 2 Task 2.2: ProfileRelationService Generic화
- 9개 엔티티의 반복 CRUD 패턴을 Generic 클래스로 추출
- 기존 API 100% 호환성 유지

사용 예:
    education_crud = GenericRelationCRUD(RelationConfig(
        model=Education,
        field_mapping={'school_name': 'school_name', ...},
        order_by='graduation_date',
        order_desc=True
    ))
    education_crud.get_all(owner_id, 'profile')
"""
from typing import Dict, List, Optional, Type, Callable, Any
from dataclasses import dataclass, field

from app.database import db
from app.types import OwnerType


@dataclass
class RelationConfig:
    """관계형 데이터 설정"""
    model: Type[Any]
    field_mapping: Dict[str, str] = field(default_factory=dict)
    # 정렬 설정
    order_by: Optional[str] = None
    order_desc: bool = True
    # 소유자 제한 (employee만 지원하는 모델 등)
    supported_owner_types: tuple = ('profile', 'employee')
    # 특수 필드 매핑 (여러 키 중 하나를 사용하는 경우)
    # 예: {'note': ['notes', 'note']}
    alt_field_mapping: Dict[str, List[str]] = field(default_factory=dict)


class GenericRelationCRUD:
    """관계형 데이터 Generic CRUD

    반복되는 CRUD 패턴을 추상화하여 코드 중복 제거

    메서드:
        - get_all: 목록 조회
        - add: 추가
        - delete: 단건 삭제 (소유권 확인)
        - delete_all: 전체 삭제
    """

    def __init__(self, config: RelationConfig):
        self.config = config
        self.model = config.model

    def _get_owner_field(self, owner_type: OwnerType) -> str:
        """소유자 필드명 반환"""
        return 'profile_id' if owner_type == 'profile' else 'employee_id'

    def _get_filter_kwargs(self, owner_id: int, owner_type: OwnerType) -> Dict[str, int]:
        """필터 조건 생성"""
        owner_field = self._get_owner_field(owner_type)
        return {owner_field: owner_id}

    def _check_owner_type(self, owner_type: OwnerType) -> bool:
        """지원되는 owner_type인지 확인"""
        return owner_type in self.config.supported_owner_types

    def _get_field_value(self, data: Dict, target_field: str) -> Any:
        """데이터에서 필드값 추출 (대체 키 지원)"""
        # 1. 직접 매핑 확인
        if target_field in self.config.field_mapping:
            source_key = self.config.field_mapping[target_field]
            if source_key in data:
                return data[source_key]

        # 2. 대체 키 확인
        if target_field in self.config.alt_field_mapping:
            for alt_key in self.config.alt_field_mapping[target_field]:
                if alt_key in data and data[alt_key] is not None:
                    return data[alt_key]

        # 3. target_field 자체가 data에 있는지 확인
        return data.get(target_field)

    def _map_data_to_model(self, data: Dict, owner_id: int, owner_type: OwnerType) -> Dict:
        """데이터를 모델 필드로 매핑"""
        owner_field = self._get_owner_field(owner_type)
        result = {owner_field: owner_id}

        # 필드 매핑 적용
        for model_field, source_key in self.config.field_mapping.items():
            if isinstance(source_key, str):
                value = data.get(source_key)
            else:
                # 리스트인 경우 첫 번째로 찾은 값 사용
                value = None
                for key in source_key:
                    if key in data and data[key] is not None:
                        value = data[key]
                        break
            if value is not None:
                result[model_field] = value

        # 대체 키 매핑 적용
        for model_field, alt_keys in self.config.alt_field_mapping.items():
            if model_field not in result or result.get(model_field) is None:
                for alt_key in alt_keys:
                    if alt_key in data and data[alt_key] is not None:
                        result[model_field] = data[alt_key]
                        break

        return result

    def get_all(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> List[Dict]:
        """목록 조회"""
        if not self._check_owner_type(owner_type):
            return []

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        query = self.model.query.filter_by(**filter_kwargs)

        # 정렬 적용
        if self.config.order_by:
            order_field = getattr(self.model, self.config.order_by, None)
            if order_field is not None:
                if self.config.order_desc:
                    query = query.order_by(order_field.desc())
                else:
                    query = query.order_by(order_field.asc())

        items = query.all()
        return [item.to_dict() for item in items]

    def get_one(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> Optional[Dict]:
        """단건 조회 (1:1 관계용)"""
        if not self._check_owner_type(owner_type):
            return None

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        item = self.model.query.filter_by(**filter_kwargs).first()
        return item.to_dict() if item else None

    def add(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Optional[Dict]:
        """추가"""
        if not self._check_owner_type(owner_type):
            return None

        mapped_data = self._map_data_to_model(data, owner_id, owner_type)
        item = self.model(**mapped_data)
        db.session.add(item)

        if commit:
            db.session.commit()

        return item.to_dict()

    def delete(
        self,
        item_id: int,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> bool:
        """단건 삭제 (소유권 확인)"""
        if not self._check_owner_type(owner_type):
            return False

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        filter_kwargs['id'] = item_id

        item = self.model.query.filter_by(**filter_kwargs).first()
        if not item:
            return False

        db.session.delete(item)
        if commit:
            db.session.commit()

        return True

    def delete_all(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> int:
        """전체 삭제"""
        if not self._check_owner_type(owner_type):
            return 0

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        count = self.model.query.filter_by(**filter_kwargs).delete()

        if commit:
            db.session.commit()

        return count

    def count(
        self,
        owner_id: int,
        owner_type: OwnerType = 'profile'
    ) -> int:
        """개수 조회"""
        if not self._check_owner_type(owner_type):
            return 0

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        return self.model.query.filter_by(**filter_kwargs).count()

    def update_or_create(
        self,
        owner_id: int,
        data: Dict,
        owner_type: OwnerType = 'profile',
        commit: bool = True
    ) -> Optional[Dict]:
        """업데이트 또는 생성 (1:1 관계용)"""
        if not self._check_owner_type(owner_type):
            return None

        filter_kwargs = self._get_filter_kwargs(owner_id, owner_type)
        item = self.model.query.filter_by(**filter_kwargs).first()

        if item:
            # 기존 데이터 업데이트
            mapped_data = self._map_data_to_model(data, owner_id, owner_type)
            for key, value in mapped_data.items():
                if key != self._get_owner_field(owner_type) and hasattr(item, key):
                    setattr(item, key, value)
        else:
            # 새로 생성
            mapped_data = self._map_data_to_model(data, owner_id, owner_type)
            item = self.model(**mapped_data)
            db.session.add(item)

        if commit:
            db.session.commit()

        return item.to_dict()
