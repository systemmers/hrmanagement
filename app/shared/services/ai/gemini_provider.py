"""
Gemini AI Provider

Google AI Studio의 Gemini API를 사용한 문서 분석
"""
import json
import time
import base64
from typing import Optional

from .base import BaseAIProvider, AnalysisResult, ProviderConfig
from .prompts import get_prompt, DOCUMENT_TYPE_DETECTION_PROMPT


class GeminiProvider(BaseAIProvider):
    """Gemini API Provider (AI Studio)"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = None
        self._model = None

    @property
    def name(self) -> str:
        return "gemini"

    @property
    def is_available(self) -> bool:
        """API 키가 설정되어 있으면 사용 가능"""
        return bool(self.config.api_key)

    def _get_client(self):
        """Gemini 클라이언트 초기화 (lazy loading)"""
        if self._client is None:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.config.api_key)
                self._client = genai
                self._model = genai.GenerativeModel(self.config.model_name)
            except ImportError:
                raise ImportError(
                    "google-generativeai 패키지가 설치되지 않았습니다. "
                    "pip install google-generativeai 명령으로 설치해주세요."
                )
        return self._client, self._model

    def analyze_document(
        self,
        file_path: str,
        document_type: str = "auto_detect"
    ) -> AnalysisResult:
        """문서 분석 실행"""
        if not self.is_available:
            return self._create_error_result("Gemini API 키가 설정되지 않았습니다.")

        start_time = time.time()

        try:
            # 클라이언트 초기화
            genai, model = self._get_client()

            # 파일 읽기
            file_bytes = self._read_file_as_bytes(file_path)
            mime_type = self._get_mime_type(file_path)

            # 문서 유형 자동 감지가 필요한 경우
            if document_type == "auto_detect":
                detected_type = self._detect_document_type(model, file_bytes, mime_type)
                if detected_type:
                    document_type = detected_type

            # 프롬프트 선택
            prompt = get_prompt(document_type)

            # Gemini API 호출
            response = model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": base64.standard_b64encode(file_bytes).decode('utf-8')
                },
                prompt
            ])

            # 응답 파싱
            response_text = response.text

            # JSON 추출 (마크다운 코드 블록 제거)
            json_text = self._extract_json(response_text)
            result_data = json.loads(json_text)

            processing_time = time.time() - start_time

            return AnalysisResult(
                success=True,
                document_type=result_data.get('document_type', document_type),
                confidence=float(result_data.get('confidence', 0.0)),
                extracted_fields=result_data.get('extracted_fields', result_data),
                raw_response=response_text,
                processing_time=processing_time,
                provider=self.name
            )

        except json.JSONDecodeError as e:
            return self._create_error_result(f"JSON 파싱 오류: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"분석 오류: {str(e)}")

    def _detect_document_type(
        self,
        model,
        file_bytes: bytes,
        mime_type: str
    ) -> Optional[str]:
        """문서 유형 자동 감지"""
        try:
            response = model.generate_content([
                {
                    "mime_type": mime_type,
                    "data": base64.standard_b64encode(file_bytes).decode('utf-8')
                },
                DOCUMENT_TYPE_DETECTION_PROMPT
            ])

            json_text = self._extract_json(response.text)
            result = json.loads(json_text)
            return result.get('document_type')
        except Exception:
            return None

    # _extract_json() 메서드는 BaseAIProvider에서 상속받아 사용
