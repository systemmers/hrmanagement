"""
Base Service Classes

공통 비즈니스 로직을 제공하는 기본 서비스 클래스들입니다.
Phase 2 리팩토링: EmployeeService와 PersonalService의 공통 패턴 추출
Phase 4.2: SOLID 원칙 적용 - RelationDataUpdater 추가
Phase 6: ServiceResult 패턴 표준화 추가
"""
from .history_service import BaseHistoryService
from .relation_updater import RelationDataUpdater, RelationDataConfig, relation_updater
from .relation_configs import get_relation_config, SUPPORTED_RELATION_TYPES
from .service_result import ServiceResult

__all__ = [
    'BaseHistoryService',
    'RelationDataUpdater',
    'RelationDataConfig',
    'relation_updater',
    'get_relation_config',
    'SUPPORTED_RELATION_TYPES',
    'ServiceResult',
]
