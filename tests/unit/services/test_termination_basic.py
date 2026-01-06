"""
TerminationService 기본 테스트

퇴사 처리 서비스 기본 기능 테스트
"""
import pytest
from unittest.mock import Mock, patch


class TestTerminationServiceInit:
    """TerminationService 초기화 테스트"""

    def test_service_creation(self):
        """서비스 생성"""
        from app.services.termination_service import TerminationService
        service = TerminationService()
        assert service is not None


class TestTerminationServiceBasic:
    """TerminationService 기본 기능 테스트"""

    def test_service_creation_only(self):
        """서비스 생성만 확인"""
        from app.services.termination_service import TerminationService
        service = TerminationService()

        # 서비스 객체만 확인
        assert service is not None


class TestUserEmployeeLinkServiceInit:
    """UserEmployeeLinkService 초기화 테스트"""

    def test_service_creation(self):
        """서비스 생성"""
        from app.services.user_employee_link_service import UserEmployeeLinkService
        service = UserEmployeeLinkService()
        assert service is not None


class TestUserEmployeeLinkServiceBasic:
    """UserEmployeeLinkService 기본 기능 테스트"""

    def test_service_creation_only(self):
        """서비스 생성만 확인"""
        from app.services.user_employee_link_service import UserEmployeeLinkService
        service = UserEmployeeLinkService()

        # 서비스 객체만 확인
        assert service is not None

