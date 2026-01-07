"""
Employee Service (Compatibility Layer)

이 파일은 기존 import 경로 호환성을 유지하기 위한 리다이렉트 모듈입니다.

기존 코드:
    from app.domains.employee.services import employee_service

새로운 구조 (권장):
    from . import employee_service
    from . import employee_core_service, employee_relation_service

Phase 3: EmployeeService 분리 완료
- EmployeeCoreService: 직원 기본 CRUD, 멀티테넌시
- EmployeeRelationService: 관계형 데이터 조회/수정
- EmployeeService: Facade (기존 API 100% 유지)
"""

# Re-export from new package structure
from . import (
    EmployeeService,
    EmployeeCoreService,
    EmployeeRelationService,
    employee_service,
    employee_core_service,
    employee_relation_service,
)

# 하위 호환성을 위한 EmployeeStatus import (기존 코드에서 사용 시)
from app.shared.constants.status import EmployeeStatus

__all__ = [
    "EmployeeService",
    "EmployeeCoreService",
    "EmployeeRelationService",
    "employee_service",
    "employee_core_service",
    "employee_relation_service",
    "EmployeeStatus",
]
