"""
Model Mixins - 공통 모델 기능 제공

DictSerializableMixin: to_dict/from_dict 자동화
- 코드 중복 제거 (~3,500 LOC 감소 목표)
- 선언적 alias/computed 필드 정의
- camelCase/snake_case 자동 변환
- FieldRegistry 통합 필드 순서 관리
"""
from collections import OrderedDict
from typing import Dict, List, Any, Optional, Callable, Type, Union


class DictSerializableMixin:
    """
    딕셔너리 직렬화/역직렬화 Mixin

    모델 클래스에서 상속하여 to_dict/from_dict 자동 구현.
    기존 37개 모델의 중복 코드를 제거합니다.

    사용법:
        class Education(DictSerializableMixin, db.Model):
            __tablename__ = 'educations'

            # FieldRegistry 도메인 (섹션 ID)
            __dict_field_domain__ = 'education'  # 필드 순서 자동 적용

            # Alias 정의: to_dict()에서 추가 키로 포함
            __dict_aliases__ = {
                'school': 'school_name',      # edu.school -> edu.school_name
                'status': 'graduation_status',
                'notes': 'note'
            }

            # 제외할 필드 (민감 정보 등)
            __dict_excludes__ = ['password_hash', 'resident_number']

            # Computed 필드: 런타임 계산 값
            __dict_computed__ = {
                'graduation_year': lambda self: self.graduation_date[:4] if self.graduation_date and len(self.graduation_date) >= 4 else None
            }

            # camelCase 키 매핑 (from_dict용)
            __dict_camel_mapping__ = {
                'employee_id': ['employeeId'],
                'school_name': ['schoolName'],
            }
    """

    # 클래스 속성 (서브클래스에서 오버라이드)
    __dict_aliases__: Dict[str, str] = {}
    __dict_excludes__: List[str] = []
    __dict_computed__: Dict[str, Callable] = {}
    __dict_camel_mapping__: Dict[str, List[str]] = {}
    __dict_json_fields__: List[str] = []  # JSON 파싱이 필요한 필드
    __dict_field_domain__: str = ''  # FieldRegistry 섹션 ID (설정 시 필드 순서 자동 적용)

    def to_dict(
        self,
        ordered: bool = True,
        account_type: Optional[str] = None
    ) -> Union[Dict[str, Any], OrderedDict]:
        """
        모델을 딕셔너리로 변환

        - 모든 컬럼 자동 포함
        - __dict_excludes__ 필드 제외
        - __dict_aliases__ 추가 키 생성
        - __dict_computed__ 계산 필드 추가
        - datetime/date 객체 자동 ISO 포맷 변환
        - FieldRegistry 기반 필드 순서 적용 (ordered=True, __dict_field_domain__ 설정 시)

        Args:
            ordered: 필드 순서 정렬 여부 (기본 True)
            account_type: 계정 타입 (가시성 필터링용)

        Returns:
            모델 데이터 딕셔너리 (ordered=True일 경우 OrderedDict)
        """
        result = {}

        # 1. 기본 컬럼 직렬화
        for column in self.__table__.columns:
            field_name = column.name

            # 제외 필드 스킵
            if field_name in self.__dict_excludes__:
                continue

            value = getattr(self, field_name)

            # datetime/date 자동 변환
            if hasattr(value, 'isoformat'):
                value = value.isoformat()

            # JSON 필드 자동 파싱
            if field_name in self.__dict_json_fields__ and value:
                import json
                try:
                    value = json.loads(value)
                except (json.JSONDecodeError, TypeError):
                    pass

            result[field_name] = value

        # 2. Alias 추가 (기존 필드에 대한 추가 키)
        for alias_name, actual_field in self.__dict_aliases__.items():
            if actual_field in result:
                result[alias_name] = result[actual_field]

        # 3. Computed 필드 추가
        for computed_name, compute_fn in self.__dict_computed__.items():
            try:
                result[computed_name] = compute_fn(self)
            except Exception:
                result[computed_name] = None

        # 4. FieldRegistry 기반 필드 순서 적용
        if ordered and self.__dict_field_domain__:
            from app.constants.field_registry import FieldRegistry
            result = FieldRegistry.to_ordered_dict(
                self.__dict_field_domain__,
                result,
                account_type
            )

        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'DictSerializableMixin':
        """
        딕셔너리에서 모델 인스턴스 생성

        - snake_case 우선, camelCase 폴백
        - __dict_camel_mapping__ 커스텀 매핑 지원
        - None 값은 건너뜀

        Args:
            data: 입력 딕셔너리 (camelCase 또는 snake_case)

        Returns:
            모델 인스턴스
        """
        kwargs = {}

        for column in cls.__table__.columns:
            field_name = column.name

            # 1. snake_case 직접 매칭
            value = data.get(field_name)

            # 2. camelCase 자동 변환 폴백
            if value is None:
                camel_name = cls._snake_to_camel(field_name)
                value = data.get(camel_name)

            # 3. 커스텀 매핑 확인
            if value is None and field_name in cls.__dict_camel_mapping__:
                for alt_key in cls.__dict_camel_mapping__[field_name]:
                    value = data.get(alt_key)
                    if value is not None:
                        break

            # 값이 있으면 kwargs에 추가
            if value is not None:
                kwargs[field_name] = value

        return cls(**kwargs)

    @staticmethod
    def _snake_to_camel(name: str) -> str:
        """snake_case를 camelCase로 변환"""
        components = name.split('_')
        return components[0] + ''.join(x.title() for x in components[1:])

    @staticmethod
    def _camel_to_snake(name: str) -> str:
        """camelCase를 snake_case로 변환"""
        result = []
        for char in name:
            if char.isupper():
                result.append('_')
                result.append(char.lower())
            else:
                result.append(char)
        return ''.join(result).lstrip('_')


class TimestampMixin:
    """
    생성/수정 시간 자동 관리 Mixin

    사용법:
        class Employee(TimestampMixin, db.Model):
            # created_at, updated_at 자동 생성
    """
    from sqlalchemy import Column, DateTime
    from sqlalchemy.sql import func

    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class SoftDeleteMixin:
    """
    소프트 삭제 Mixin

    사용법:
        class Employee(SoftDeleteMixin, db.Model):
            # deleted_at으로 논리 삭제
    """
    from sqlalchemy import Column, DateTime

    deleted_at = Column(DateTime(timezone=True), nullable=True)

    @property
    def is_deleted(self) -> bool:
        """삭제 여부 확인"""
        return self.deleted_at is not None

    def soft_delete(self):
        """논리 삭제"""
        from datetime import datetime
        self.deleted_at = datetime.utcnow()

    def restore(self):
        """삭제 복구"""
        self.deleted_at = None
