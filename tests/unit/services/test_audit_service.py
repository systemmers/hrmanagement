"""
AuditService 단위 테스트

감사 로그 서비스의 핵심 비즈니스 로직 테스트:
- 로그 생성
- 로그 조회
- 통계 및 리포트
"""
import pytest
from unittest.mock import Mock, patch, MagicMock

from app.domains.platform.services.audit_service import AuditService, audit_service


class TestAuditServiceInit:
    """AuditService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert audit_service is not None
        assert isinstance(audit_service, AuditService)

    def test_enable_disable(self):
        """감사 로깅 활성화/비활성화"""
        service = AuditService()
        service.disable()
        assert service.is_enabled() is False
        service.enable()
        assert service.is_enabled() is True


class TestAuditServiceLog:
    """로그 생성 테스트"""

    def test_log_success(self, app):
        """로그 생성 성공"""
        from app.shared.constants.session_keys import SessionKeys
        service = AuditService()
        service.enable()

        with patch('app.services.audit_service.session') as mock_session, \
             patch('app.services.audit_service.request') as mock_request, \
             patch('app.services.audit_service.AuditLog') as mock_log_model, \
             patch('app.services.audit_service.db') as mock_db, \
             patch('app.services.audit_service.json') as mock_json:
            def session_get(key):
                return {SessionKeys.USER_ID: 1, SessionKeys.ACCOUNT_TYPE: 'corporate', SessionKeys.COMPANY_ID: 1}.get(key)
            mock_session.get = session_get
            mock_user_agent = Mock()
            mock_user_agent.string = 'test'
            mock_request.user_agent = mock_user_agent
            mock_request.endpoint = 'test.endpoint'
            mock_request.method = 'GET'
            mock_request.remote_addr = '127.0.0.1'
            
            # request.headers.get을 동기 함수로 Mock 설정
            mock_headers = MagicMock()
            mock_headers.get = MagicMock(return_value=None)
            mock_request.headers = mock_headers
            
            mock_log_instance = Mock()
            mock_log_model.return_value = mock_log_instance
            mock_json.dumps.return_value = '{}'
            mock_db.session.add = Mock()
            mock_db.session.commit = Mock()

            result = service.log(
                action='view',
                resource_type='employee',
                resource_id=1
            )

            assert result is not None

    def test_log_disabled(self):
        """감사 로깅 비활성화 시"""
        service = AuditService()
        service.disable()

        result = service.log(
            action='view',
            resource_type='employee'
        )

        assert result is None


class TestAuditServiceQueries:
    """로그 조회 테스트"""

    def test_get_logs_success(self, app):
        """로그 조회 성공"""
        service = AuditService()

        with patch('app.services.audit_service.AuditLog') as mock_log:
            mock_log_instance = Mock()
            mock_log_instance.to_dict.return_value = {'id': 1, 'action': 'view'}
            mock_query = Mock()
            mock_query.filter_by.return_value = mock_query
            mock_query.filter.return_value = mock_query
            mock_query.order_by.return_value = mock_query
            mock_query.offset.return_value = mock_query
            mock_query.limit.return_value = mock_query
            mock_query.all.return_value = [mock_log_instance]
            mock_log.query = mock_query

            result = service.get_logs(limit=20, offset=0)

            assert result is not None
            assert isinstance(result, list)

    def test_tracked_resources_constant(self):
        """추적 대상 리소스 상수 확인"""
        service = AuditService()
        
        assert 'employee' in service.TRACKED_RESOURCES
        assert 'contract' in service.TRACKED_RESOURCES
        assert 'user' in service.TRACKED_RESOURCES

    def test_sensitive_fields_constant(self):
        """민감 필드 상수 확인"""
        service = AuditService()
        
        assert 'password' in service.SENSITIVE_FIELDS
        assert 'token' in service.SENSITIVE_FIELDS

    def test_mask_sensitive_data(self):
        """민감 정보 마스킹"""
        service = AuditService()
        
        data = {
            'name': 'John',
            'password': 'secret123',
            'email': 'john@example.com'
        }
        
        result = service._mask_sensitive_data(data)
        
        assert result['name'] == 'John'
        assert result['password'] == '[MASKED]'  # 실제 마스킹 값
        assert result['email'] == 'john@example.com'

