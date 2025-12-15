"""
AI Service

문서 분석을 위한 AI 서비스 팩토리
"""
from typing import Dict, Optional, Type
from flask import current_app

from .ai.base import BaseAIProvider, AnalysisResult, ProviderConfig
from .ai.gemini_provider import GeminiProvider
from .ai.local_llama_provider import LocalLlamaProvider, LocalLlamaOCRProvider
from .ai.document_ai_provider import DocumentAIProvider
from .ai.vision_ocr import VisionOCR


class AIService:
    """AI 서비스 팩토리"""

    # 등록된 Provider들
    _providers: Dict[str, Type[BaseAIProvider]] = {
        'gemini': GeminiProvider,
        'local_llama': LocalLlamaProvider,
        'local_llama_ocr': LocalLlamaOCRProvider,
        'document_ai': DocumentAIProvider,
    }

    @classmethod
    def get_provider(cls, provider_name: str) -> BaseAIProvider:
        """Provider 인스턴스 생성"""
        if provider_name not in cls._providers:
            raise ValueError(f"알 수 없는 Provider: {provider_name}")

        provider_class = cls._providers[provider_name]
        config = cls._get_config(provider_name)

        return provider_class(config)

    @classmethod
    def _get_config(cls, provider_name: str) -> ProviderConfig:
        """Flask config에서 Provider 설정 로드"""
        if provider_name == 'local_llama':
            return ProviderConfig(
                endpoint_url=current_app.config.get('LOCAL_LLM_ENDPOINT'),
                model_name=current_app.config.get('LOCAL_LLM_MODEL', 'local-model'),
                timeout=current_app.config.get('LOCAL_LLM_TIMEOUT', 120),
                max_tokens=4096,
                temperature=0.1
            )

        if provider_name == 'local_llama_ocr':
            # OCR 모드: LM Studio + Google Vision OCR
            return ProviderConfig(
                endpoint_url=current_app.config.get('LOCAL_LLM_ENDPOINT'),
                model_name=current_app.config.get('LOCAL_LLM_MODEL', 'local-model'),
                timeout=current_app.config.get('LOCAL_LLM_TIMEOUT', 120),
                credentials_path=current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS'),
                project_id=current_app.config.get('GOOGLE_PROJECT_ID'),
                max_tokens=4096,
                temperature=0.1
            )

        if provider_name == 'document_ai':
            # Document AI: 별도 리전 설정 지원
            return ProviderConfig(
                project_id=current_app.config.get('GOOGLE_PROJECT_ID'),
                location=current_app.config.get('DOCUMENTAI_LOCATION', 'us'),
                credentials_path=current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS'),
                processor_id=current_app.config.get('DOCUMENTAI_PROCESSOR_ID'),
            )

        # Gemini 및 기타 GCP 기반 Provider
        return ProviderConfig(
            api_key=current_app.config.get('GEMINI_API_KEY'),
            project_id=current_app.config.get('GOOGLE_PROJECT_ID'),
            location=current_app.config.get('GOOGLE_LOCATION', 'asia-northeast3'),
            credentials_path=current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS'),
            processor_id=current_app.config.get('DOCUMENTAI_PROCESSOR_ID'),
            model_name='gemini-2.0-flash',
            max_tokens=4096,
            temperature=0.1
        )

    @classmethod
    def get_available_providers(cls) -> Dict[str, bool]:
        """사용 가능한 Provider 목록 반환"""
        available = {}

        for name in cls._providers:
            try:
                provider = cls.get_provider(name)
                available[name] = provider.is_available
            except Exception:
                available[name] = False

        return {k: v for k, v in available.items() if v}

    @classmethod
    def analyze(
        cls,
        file_path: str,
        provider_name: str = 'gemini',
        document_type: str = 'auto_detect'
    ) -> AnalysisResult:
        """문서 분석 실행

        Args:
            file_path: 분석할 파일 경로
            provider_name: 사용할 Provider 이름
            document_type: 문서 유형 (auto_detect면 자동 감지)

        Returns:
            AnalysisResult: 분석 결과
        """
        provider = cls.get_provider(provider_name)

        if not provider.is_available:
            return AnalysisResult(
                success=False,
                document_type="unknown",
                confidence=0.0,
                extracted_fields={},
                error=f"{provider_name} Provider를 사용할 수 없습니다. 설정을 확인해주세요.",
                provider=provider_name
            )

        return provider.analyze_document(file_path, document_type)

    @classmethod
    def get_vision_ocr(cls) -> VisionOCR:
        """Vision OCR 인스턴스 반환"""
        return VisionOCR(
            credentials_path=current_app.config.get('GOOGLE_APPLICATION_CREDENTIALS'),
            project_id=current_app.config.get('GOOGLE_PROJECT_ID')
        )
