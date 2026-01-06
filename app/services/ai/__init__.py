"""
AI 서비스 모듈 - 호환성 래퍼

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/shared/services/ai/ 에 위치
"""

from app.shared.services.ai import (
    BaseAIProvider,
    AnalysisResult,
    ProviderConfig,
    GeminiProvider,
    LocalLlamaProvider,
    LocalLlamaOCRProvider,
    DocumentAIProvider,
    VisionOCR,
    OCRResult,
)

__all__ = [
    'BaseAIProvider',
    'AnalysisResult',
    'ProviderConfig',
    'GeminiProvider',
    'LocalLlamaProvider',
    'LocalLlamaOCRProvider',
    'DocumentAIProvider',
    'VisionOCR',
    'OCRResult',
]
