"""
PlatformService 단위 테스트

플랫폼 관리 서비스의 핵심 비즈니스 로직 테스트:
- 사용자 관리
- 법인 관리
- 플랫폼 설정 관리
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.platform.services.platform_service import PlatformService, platform_service


class TestPlatformServiceInit:
    """PlatformService 초기화 테스트"""

    def test_service_instance_exists(self, app):
        """서비스 인스턴스 존재 확인"""
        assert platform_service is not None
        assert isinstance(platform_service, PlatformService)


class TestPlatformServiceUserManagement:
    """사용자 관리 테스트"""

    def test_get_users_paginated_success(self, session):
        """사용자 목록 조회 성공"""
        with patch('app.domains.platform.services.platform_service.User') as mock_user:
            mock_user_instance = Mock(id=1, username='test')
            mock_pagination = Mock()
            mock_pagination.items = [mock_user_instance]
            mock_pagination.total = 1
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.filter_by.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.paginate.return_value = mock_pagination
            mock_user.query = mock_query

            users, pagination = platform_service.get_users_paginated(page=1, per_page=20)

            assert len(users) == 1
            assert pagination.total == 1

    def test_get_user_by_id_success(self, session):
        """사용자 ID로 조회 성공"""
        with patch('app.domains.platform.services.platform_service.db') as mock_db:
            mock_user = Mock(id=1, username='test')
            mock_db.session.get.return_value = mock_user

            result = platform_service.get_user_by_id(user_id=1)

            assert result is not None
            assert result.id == 1

    def test_toggle_user_active_success(self, session):
        """사용자 활성화/비활성화 토글 성공"""
        with patch('app.domains.platform.services.platform_service.db') as mock_db, \
             patch('app.domains.platform.services.platform_service.atomic_transaction'):
            mock_user = Mock(id=2, is_active=True)
            mock_db.session.get.return_value = mock_user

            success, error, is_active = platform_service.toggle_user_active(
                user_id=2,
                current_user_id=1
            )

            assert success is True
            assert is_active is False

    def test_toggle_user_active_self(self, session):
        """자기 자신을 비활성화하려고 할 때"""
        success, error, is_active = platform_service.toggle_user_active(
            user_id=1,
            current_user_id=1
        )

        assert success is False
        assert '자기 자신' in error


class TestPlatformServiceCompanyManagement:
    """법인 관리 테스트"""

    def test_get_companies_paginated_success(self, session):
        """법인 목록 조회 성공"""
        with patch('app.domains.platform.services.platform_service.Company') as mock_company:
            mock_company_instance = Mock(id=1, name='테스트법인')
            mock_pagination = Mock()
            mock_pagination.items = [mock_company_instance]
            mock_pagination.total = 1
            mock_query = Mock()
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.paginate.return_value = mock_pagination
            mock_company.query = mock_query

            companies, pagination = platform_service.get_companies_paginated(page=1, per_page=20)

            assert len(companies) == 1

