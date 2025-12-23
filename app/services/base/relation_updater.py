"""
RelationDataUpdater

관계형 데이터(학력, 경력, 자격증 등) 업데이트 공통 로직을 제공합니다.
Phase 4.2: SOLID 원칙 적용 - SRP, DRY 개선

기존 EmployeeService의 8개 _update_*_data 메서드를 설정 기반으로 통합합니다.
"""
from dataclasses import dataclass, field
from typing import Dict, List, Any, Optional, Callable, Type
from app.database import db


@dataclass
class RelationDataConfig:
    """
    관계형 데이터 업데이트 설정

    Phase 8: FieldRegistry 통합 - field_order 지원
    """
    model_class: Type
    repository: Any
    form_prefix: str
    required_field: str
    field_mapping: Dict[str, str]
    converters: Dict[str, Callable] = field(default_factory=dict)
    owner_field: str = 'employee_id'  # 'employee_id' or 'profile_id'
    field_order: List[str] = field(default_factory=list)  # FieldRegistry 순서


class RelationDataUpdater:
    """
    관계형 데이터 범용 업데이트 서비스

    사용법:
        from app.services.base.relation_updater import RelationDataUpdater, RelationDataConfig

        config = RelationDataConfig(
            model_class=Education,
            repository=education_repo,
            form_prefix='education_',
            required_field='school_name',
            field_mapping={
                'school_type': 'school_type',
                'school_name': 'school_name',
                'graduation_year': 'graduation_date',
            }
        )

        updater = RelationDataUpdater()
        updater.update(employee_id, form_data, config)
    """

    def update(self, owner_id: int, form_data: Dict, config: RelationDataConfig) -> int:
        """
        관계형 데이터 업데이트 (전체 교체 방식)

        Args:
            owner_id: 직원 ID 또는 프로필 ID
            form_data: 폼 데이터 (Flask request.form)
            config: 업데이트 설정

        Returns:
            생성된 레코드 수
        """
        # 기존 데이터 삭제
        if config.owner_field == 'employee_id':
            config.repository.delete_by_employee_id(owner_id)
        else:
            config.repository.delete_all_by_profile(owner_id)

        # 폼 데이터 추출
        form_lists = {}
        for field_suffix in config.field_mapping.keys():
            form_key = f"{config.form_prefix}{field_suffix}[]"
            if hasattr(form_data, 'getlist'):
                form_lists[field_suffix] = form_data.getlist(form_key)
            else:
                # Dict인 경우 (테스트용)
                form_lists[field_suffix] = form_data.get(form_key, [])

        # 필수 필드 리스트를 기준으로 반복
        required_values = form_lists.get(config.required_field, [])
        created_count = 0

        for i in range(len(required_values)):
            if required_values[i]:
                model_data = {config.owner_field: owner_id}

                for field_suffix, model_attr in config.field_mapping.items():
                    values = form_lists.get(field_suffix, [])
                    value = values[i] if i < len(values) else None

                    if model_attr in config.converters and value is not None:
                        value = config.converters[model_attr](value)

                    model_data[model_attr] = value

                instance = config.model_class(**model_data)
                config.repository.create(instance)
                created_count += 1

        return created_count

    def update_with_commit(self, owner_id: int, form_data: Dict,
                           config: RelationDataConfig) -> tuple[bool, Optional[str]]:
        """
        관계형 데이터 업데이트 (트랜잭션 포함)

        Args:
            owner_id: 직원 ID 또는 프로필 ID
            form_data: 폼 데이터
            config: 업데이트 설정

        Returns:
            Tuple[성공여부, 에러메시지]
        """
        try:
            self.update(owner_id, form_data, config)
            db.session.commit()
            return True, None
        except Exception as e:
            db.session.rollback()
            return False, str(e)


# 싱글톤 인스턴스
relation_updater = RelationDataUpdater()
