"""
Base Service Classes

공통 비즈니스 로직을 제공하는 기본 서비스 클래스들입니다.
Phase 2 리팩토링: EmployeeService와 PersonalService의 공통 패턴 추출
"""
from .history_service import BaseHistoryService

__all__ = ['BaseHistoryService']
