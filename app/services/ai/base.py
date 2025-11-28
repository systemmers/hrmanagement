"""
AI Provider 기본 클래스

모든 AI Provider가 구현해야 하는 인터페이스를 정의합니다.
"""
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, List
from enum import Enum


class DocumentType(Enum):
    """문서 유형"""
    AUTO_DETECT = "auto_detect"
    RESUME = "resume"
    CAREER_CERTIFICATE = "career_certificate"
    EDUCATION_CERTIFICATE = "education_certificate"
    ID_CARD = "id_card"
    BANK_STATEMENT = "bank_statement"
    PHOTO = "photo"
    OTHER = "other"


@dataclass
class AnalysisResult:
    """AI 분석 결과"""
    success: bool
    document_type: str
    confidence: float
    extracted_fields: Dict[str, Any]
    raw_response: Optional[str] = None
    processing_time: float = 0.0
    provider: str = ""
    error: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리로 변환"""
        return {
            'success': self.success,
            'document_type': self.document_type,
            'confidence': self.confidence,
            'extracted_fields': self.extracted_fields,
            'raw_response': self.raw_response,
            'processing_time': self.processing_time,
            'provider': self.provider,
            'error': self.error
        }


@dataclass
class ProviderConfig:
    """Provider 설정"""
    api_key: Optional[str] = None
    project_id: Optional[str] = None
    location: str = "asia-northeast3"
    credentials_path: Optional[str] = None
    processor_id: Optional[str] = None
    model_name: str = "gemini-1.5-flash"
    max_tokens: int = 4096
    temperature: float = 0.1


class BaseAIProvider(ABC):
    """AI Provider 기본 클래스"""

    def __init__(self, config: ProviderConfig):
        self.config = config

    @property
    @abstractmethod
    def name(self) -> str:
        """Provider 이름"""
        pass

    @property
    @abstractmethod
    def is_available(self) -> bool:
        """사용 가능 여부"""
        pass

    @abstractmethod
    def analyze_document(
        self,
        file_path: str,
        document_type: str = "auto_detect"
    ) -> AnalysisResult:
        """문서 분석 실행

        Args:
            file_path: 분석할 파일 경로
            document_type: 문서 유형 (auto_detect면 자동 감지)

        Returns:
            AnalysisResult: 분석 결과
        """
        pass

    def _read_file_as_bytes(self, file_path: str) -> bytes:
        """파일을 바이트로 읽기"""
        with open(file_path, 'rb') as f:
            return f.read()

    def _get_mime_type(self, file_path: str) -> str:
        """파일 MIME 타입 추론"""
        import mimetypes
        mime_type, _ = mimetypes.guess_type(file_path)
        return mime_type or 'application/octet-stream'

    def _create_error_result(self, error: str) -> AnalysisResult:
        """에러 결과 생성"""
        return AnalysisResult(
            success=False,
            document_type="unknown",
            confidence=0.0,
            extracted_fields={},
            error=error,
            provider=self.name
        )
