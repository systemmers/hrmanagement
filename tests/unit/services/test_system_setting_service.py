"""
SystemSettingService 단위 테스트

시스템 설정 서비스 테스트
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.platform.services.system_setting_service import SystemSettingService, system_setting_service


class TestSystemSettingServiceInit:
    """초기화 테스트"""

    def test_singleton_instance_exists(self):
        """싱글톤 인스턴스 존재 확인"""
        assert system_setting_service is not None
        assert isinstance(system_setting_service, SystemSettingService)

    def test_service_has_repo_property(self):
        """Repository 속성 확인"""
        assert hasattr(system_setting_service, 'system_setting_repo')


class TestGetByKey:
    """키로 설정 조회 테스트"""

    def test_get_by_key_success(self):
        """설정 조회 성공"""
        mock_setting = {'key': 'test.key', 'value': 'test_value'}
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = mock_setting
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_by_key('test.key')
            
            assert result == mock_setting
            mock_repo.get_by_key.assert_called_once_with('test.key')

    def test_get_by_key_not_found(self):
        """설정을 찾을 수 없을 때"""
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = None
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_by_key('nonexistent.key')
            
            assert result is None


class TestGetValue:
    """설정 값만 조회 테스트"""

    def test_get_value_dict_success(self):
        """Dict 형태 설정 값 조회"""
        mock_setting = {'key': 'test.key', 'value': 'test_value'}
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = mock_setting
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_value('test.key')
            
            assert result == 'test_value'

    def test_get_value_object_success(self):
        """객체 형태 설정 값 조회"""
        mock_setting = Mock()
        mock_setting.value = 'object_value'
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = mock_setting
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_value('test.key')
            
            assert result == 'object_value'

    def test_get_value_with_default(self):
        """기본값과 함께 조회"""
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = None
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_value('test.key', default='default_value')
            
            assert result == 'default_value'

    def test_get_value_no_value_key(self):
        """value 키가 없는 Dict"""
        mock_setting = {'key': 'test.key'}
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = mock_setting
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_value('test.key', default='fallback')
            
            assert result == 'fallback'


class TestGetCompanyData:
    """회사 정보 조회 테스트"""

    def test_get_company_data_success(self):
        """회사 정보 조회 성공"""
        def mock_get_by_key(key):
            """Mock 설정 반환"""
            if key == 'company.name':
                return {'key': key, 'value': '테스트 회사'}
            elif key == 'company.ceo_name':
                return {'key': key, 'value': '대표자'}
            elif key == 'company.phone':
                return {'key': key, 'value': '02-1234-5678'}
            return None
        
        mock_repo = Mock()
        mock_repo.get_by_key.side_effect = mock_get_by_key
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_company_data()
            
            assert isinstance(result, dict)
            assert result.get('name') == '테스트 회사'
            assert result.get('ceo_name') == '대표자'
            assert result.get('phone') == '02-1234-5678'

    def test_get_company_data_partial(self):
        """일부 회사 정보만 있을 때"""
        def mock_get_by_key(key):
            """Mock 설정 반환 - 일부만"""
            if key == 'company.name':
                return {'key': key, 'value': '테스트 회사'}
            return None
        
        mock_repo = Mock()
        mock_repo.get_by_key.side_effect = mock_get_by_key
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_company_data()
            
            assert isinstance(result, dict)
            assert result.get('name') == '테스트 회사'
            assert 'ceo_name' not in result

    def test_get_company_data_object_type(self):
        """객체 형태 설정 값"""
        def mock_get_by_key(key):
            """Mock 객체 반환"""
            if key == 'company.name':
                mock_obj = Mock()
                mock_obj.value = '테스트 회사'
                return mock_obj
            return None
        
        mock_repo = Mock()
        mock_repo.get_by_key.side_effect = mock_get_by_key
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_company_data()
            
            assert isinstance(result, dict)
            assert result.get('name') == '테스트 회사'

    def test_get_company_data_empty(self):
        """회사 정보가 없을 때"""
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = None
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            result = system_setting_service.get_company_data()
            
            assert isinstance(result, dict)
            assert len(result) == 0


class TestSystemSettingServiceIntegration:
    """통합 테스트"""

    def test_service_methods_callable(self):
        """모든 서비스 메서드 호출 가능"""
        assert callable(system_setting_service.get_by_key)
        assert callable(system_setting_service.get_value)
        assert callable(system_setting_service.get_company_data)

    def test_get_value_various_defaults(self):
        """다양한 기본값 타입"""
        mock_repo = Mock()
        mock_repo.get_by_key.return_value = None
        
        with patch('app.extensions.system_setting_repo', mock_repo):
            # 문자열 기본값
            assert system_setting_service.get_value('key1', 'default') == 'default'
            
            # 숫자 기본값
            assert system_setting_service.get_value('key2', 100) == 100
            
            # 불린 기본값
            assert system_setting_service.get_value('key3', True) is True
            
            # None 기본값
            assert system_setting_service.get_value('key4', None) is None

