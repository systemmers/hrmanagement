"""
AI 서비스 모듈

문서 분석을 위한 AI Provider들을 제공합니다.
- Gemini (AI Studio): 무료, 빠른 설정
- Local LLM (LM Studio): 로컬 멀티모달 모델
- Local LLM + OCR: Vision OCR + 텍스트 LLM 조합
- Document AI: Google Cloud Document AI 기반 구조화된 문서 처리
- Vision OCR: Google Cloud Vision 기반 고품질 OCR

Phase 7: 도메인 중심 마이그레이션 완료
실제 구현은 app/shared/services/ai/ 에 위치
"""

from .base import BaseAIProvider, AnalysisResult, ProviderConfig
from .gemini_provider import GeminiProvider
from .local_llama_provider import LocalLlamaProvider, LocalLlamaOCRProvider
from .document_ai_provider import DocumentAIProvider
from .vision_ocr import VisionOCR, OCRResult

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
