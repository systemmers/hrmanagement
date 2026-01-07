"""
AIService 단위 테스트

AI 서비스의 핵심 비즈니스 로직 테스트:
- Provider 인스턴스 생성
- Provider 설정 로드
- 사용 가능한 Provider 목록 조회
- 문서 분석 실행
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from flask import Flask

from app.services.ai_service import AIService
from app.services.ai import AnalysisResult


class TestAIServiceInit:
    """AIService 초기화 테스트"""

    def test_service_class_exists(self):
        """AIService 클래스 존재 확인"""
        assert AIService is not None

    def test_service_has_providers(self):
        """등록된 Provider 목록 확인"""
        assert hasattr(AIService, '_providers')
        assert isinstance(AIService._providers, dict)
        assert len(AIService._providers) > 0


class TestAIServiceGetProvider:
    """Provider 인스턴스 생성 테스트"""

    def test_get_provider_valid_name(self, app):
        """유효한 Provider 이름으로 인스턴스 생성"""
        with patch('app.services.ai_service.current_app') as mock_app:
            mock_app.config = {
                'GEMINI_API_KEY': 'test_key',
                'GOOGLE_PROJECT_ID': 'test_project',
                'GOOGLE_LOCATION': 'asia-northeast3',
                'GOOGLE_APPLICATION_CREDENTIALS': 'test_creds.json',
                'DOCUMENTAI_PROCESSOR_ID': 'test_processor'
            }
            # 실제 Provider가 생성되므로 인스턴스 타입 확인
            provider = AIService.get_provider('gemini')
            
            assert provider is not None
            # GeminiProvider 인스턴스인지 확인
            from app.services.ai.gemini_provider import GeminiProvider
            assert isinstance(provider, GeminiProvider)

    def test_get_provider_invalid_name(self, app):
        """유효하지 않은 Provider 이름"""
        with pytest.raises(ValueError) as exc_info:
            AIService.get_provider('invalid_provider')
        
        assert '알 수 없는 Provider' in str(exc_info.value)


class TestAIServiceGetConfig:
    """Provider 설정 로드 테스트"""

    def test_get_config_gemini(self, app):
        """Gemini Provider 설정 로드"""
        with patch('app.services.ai_service.current_app') as mock_app:
            mock_app.config = {
                'GEMINI_API_KEY': 'test_key',
                'GOOGLE_PROJECT_ID': 'test_project',
                'GOOGLE_LOCATION': 'asia-northeast3',
                'GOOGLE_APPLICATION_CREDENTIALS': 'test_creds.json',
                'DOCUMENTAI_PROCESSOR_ID': 'test_processor'
            }
            
            config = AIService._get_config('gemini')
            
            assert config is not None
            assert config.api_key == 'test_key'
            assert config.project_id == 'test_project'

    def test_get_config_local_llama(self, app):
        """Local Llama Provider 설정 로드"""
        with patch('app.services.ai_service.current_app') as mock_app:
            mock_app.config = {
                'LOCAL_LLM_ENDPOINT': 'http://localhost:8080',
                'LOCAL_LLM_MODEL': 'test-model',
                'LOCAL_LLM_TIMEOUT': 120
            }
            
            config = AIService._get_config('local_llama')
            
            assert config is not None
            assert config.endpoint_url == 'http://localhost:8080'
            assert config.model_name == 'test-model'
            assert config.timeout == 120

    def test_get_config_document_ai(self, app):
        """Document AI Provider 설정 로드"""
        with patch('app.services.ai_service.current_app') as mock_app:
            mock_app.config = {
                'GOOGLE_PROJECT_ID': 'test_project',
                'DOCUMENTAI_LOCATION': 'us',
                'GOOGLE_APPLICATION_CREDENTIALS': 'test_creds.json',
                'DOCUMENTAI_PROCESSOR_ID': 'test_processor'
            }
            
            config = AIService._get_config('document_ai')
            
            assert config is not None
            assert config.project_id == 'test_project'
            assert config.location == 'us'
            assert config.processor_id == 'test_processor'


class TestAIServiceGetAvailableProviders:
    """사용 가능한 Provider 목록 조회 테스트"""

    def test_get_available_providers_success(self, app):
        """사용 가능한 Provider 목록 조회 성공"""
        with patch('app.services.ai_service.AIService.get_provider') as mock_get:
            mock_provider = Mock()
            mock_provider.is_available = True
            mock_get.return_value = mock_provider
            
            result = AIService.get_available_providers()
            
            assert isinstance(result, dict)
            assert len(result) > 0

    def test_get_available_providers_with_exception(self, app):
        """Provider 생성 중 예외 발생 시"""
        with patch('app.services.ai_service.AIService.get_provider') as mock_get:
            mock_get.side_effect = Exception("Provider error")
            
            result = AIService.get_available_providers()
            
            assert isinstance(result, dict)


class TestAIServiceAnalyze:
    """문서 분석 실행 테스트"""

    def test_analyze_success(self, app):
        """문서 분석 성공"""
        with patch('app.services.ai_service.AIService.get_provider') as mock_get:
            mock_provider = Mock()
            mock_provider.is_available = True
            mock_provider.analyze_document.return_value = AnalysisResult(
                success=True,
                document_type='resume',
                confidence=0.95,
                extracted_fields={'name': '홍길동'},
                error=None,
                provider='gemini'
            )
            mock_get.return_value = mock_provider
            
            result = AIService.analyze('test_file.pdf', 'gemini')
            
            assert result is not None
            assert result.success is True
            assert result.document_type == 'resume'
            mock_provider.analyze_document.assert_called_once()

    def test_analyze_provider_unavailable(self, app):
        """Provider 사용 불가능 시"""
        with patch('app.services.ai_service.AIService.get_provider') as mock_get:
            mock_provider = Mock()
            mock_provider.is_available = False
            mock_get.return_value = mock_provider
            
            result = AIService.analyze('test_file.pdf', 'gemini')
            
            assert result is not None
            assert result.success is False
            assert '사용할 수 없습니다' in result.error

    def test_analyze_with_document_type(self, app):
        """문서 유형 지정하여 분석"""
        with patch('app.services.ai_service.AIService.get_provider') as mock_get:
            mock_provider = Mock()
            mock_provider.is_available = True
            mock_provider.analyze_document.return_value = AnalysisResult(
                success=True,
                document_type='resume',
                confidence=0.95,
                extracted_fields={},
                error=None,
                provider='gemini'
            )
            mock_get.return_value = mock_provider
            
            result = AIService.analyze('test_file.pdf', 'gemini', 'resume')
            
            assert result is not None
            mock_provider.analyze_document.assert_called_once_with('test_file.pdf', 'resume')


class TestAIServiceGetVisionOCR:
    """Vision OCR 인스턴스 반환 테스트"""

    def test_get_vision_ocr(self, app):
        """Vision OCR 인스턴스 반환"""
        with patch('app.services.ai_service.current_app') as mock_app:
            mock_app.config = {
                'GOOGLE_APPLICATION_CREDENTIALS': 'test_creds.json',
                'GOOGLE_PROJECT_ID': 'test_project'
            }
            with patch('app.services.ai_service.VisionOCR') as mock_vision_ocr:
                mock_instance = Mock()
                mock_vision_ocr.return_value = mock_instance
                
                result = AIService.get_vision_ocr()
                
                assert result is not None
                mock_vision_ocr.assert_called_once_with(
                    credentials_path='test_creds.json',
                    project_id='test_project'
                )

