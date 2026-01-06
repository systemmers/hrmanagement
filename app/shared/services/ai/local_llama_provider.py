"""
Local LLM Provider (LM Studio)

LM Studio의 OpenAI 호환 API를 사용한 문서 분석
- LocalLlamaProvider: 멀티모달 지원 (이미지 직접 처리)
- LocalLlamaOCRProvider: Google Vision OCR + 텍스트 분석
"""
import json
import time
import base64
from typing import Optional, List, Dict, Any

import requests

from .base import BaseAIProvider, AnalysisResult, ProviderConfig
from .prompts import get_prompt, DOCUMENT_TYPE_DETECTION_PROMPT, get_ocr_analysis_prompt


class LocalLlamaProvider(BaseAIProvider):
    """Local LLM Provider (LM Studio OpenAI 호환 API)"""

    DEFAULT_ENDPOINT = "http://localhost:1234"
    API_PATH = "/v1/chat/completions"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._endpoint = config.endpoint_url or self.DEFAULT_ENDPOINT

    @property
    def name(self) -> str:
        return "local_llama"

    @property
    def is_available(self) -> bool:
        """LM Studio 서버 연결 가능 여부 확인"""
        try:
            response = requests.get(
                f"{self._endpoint}/v1/models",
                timeout=5
            )
            return response.status_code == 200
        except requests.exceptions.RequestException:
            return False

    def analyze_document(
        self,
        file_path: str,
        document_type: str = "auto_detect"
    ) -> AnalysisResult:
        """문서 분석 실행"""
        if not self.is_available:
            return self._create_error_result(
                "LM Studio 서버에 연결할 수 없습니다. 서버 상태를 확인해주세요."
            )

        start_time = time.time()

        try:
            # 파일 읽기 및 인코딩
            file_bytes = self._read_file_as_bytes(file_path)
            mime_type = self._get_mime_type(file_path)
            base64_data = base64.standard_b64encode(file_bytes).decode('utf-8')

            # 문서 유형 자동 감지
            if document_type == "auto_detect":
                detected_type = self._detect_document_type(base64_data, mime_type)
                if detected_type:
                    document_type = detected_type

            # 프롬프트 선택
            prompt = get_prompt(document_type)

            # 멀티모달 메시지 구성
            messages = self._build_multimodal_messages(prompt, base64_data, mime_type)

            # API 호출
            response = self._call_api(messages)

            # 응답 파싱
            response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')

            # JSON 추출
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
        except requests.exceptions.Timeout:
            return self._create_error_result(
                f"요청 시간 초과 ({self.config.timeout}초). 모델 로딩 또는 서버 응답 지연."
            )
        except requests.exceptions.RequestException as e:
            return self._create_error_result(f"API 요청 오류: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"분석 오류: {str(e)}")

    def _detect_document_type(
        self,
        base64_data: str,
        mime_type: str
    ) -> Optional[str]:
        """문서 유형 자동 감지"""
        try:
            messages = self._build_multimodal_messages(
                DOCUMENT_TYPE_DETECTION_PROMPT,
                base64_data,
                mime_type
            )
            response = self._call_api(messages)
            response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')

            json_text = self._extract_json(response_text)
            result = json.loads(json_text)
            return result.get('document_type')
        except Exception:
            return None

    def _build_multimodal_messages(
        self,
        prompt: str,
        base64_data: str,
        mime_type: str
    ) -> List[Dict[str, Any]]:
        """OpenAI 호환 멀티모달 메시지 구성"""
        return [{
            "role": "user",
            "content": [
                {
                    "type": "text",
                    "text": prompt
                },
                {
                    "type": "image_url",
                    "image_url": {
                        "url": f"data:{mime_type};base64,{base64_data}"
                    }
                }
            ]
        }]

    def _call_api(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LM Studio API 호출"""
        url = f"{self._endpoint}{self.API_PATH}"

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()
        return response.json()


class LocalLlamaOCRProvider(BaseAIProvider):
    """Local LLM Provider with Google Vision OCR

    멀티모달 대신 Google Vision OCR로 텍스트 추출 후 LLM 분석
    텍스트 전용 모델에서도 사용 가능
    """

    DEFAULT_ENDPOINT = "http://localhost:1234"
    API_PATH = "/v1/chat/completions"

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._endpoint = config.endpoint_url or self.DEFAULT_ENDPOINT
        self._vision_ocr = None

    @property
    def name(self) -> str:
        return "local_llama_ocr"

    @property
    def is_available(self) -> bool:
        """LM Studio 서버 및 Vision OCR 사용 가능 여부"""
        try:
            # LM Studio 서버 확인
            response = requests.get(
                f"{self._endpoint}/v1/models",
                timeout=5
            )
            if response.status_code != 200:
                return False

            # Vision OCR 확인 (lazy import)
            return self._get_vision_ocr().is_available
        except Exception:
            return False

    def _get_vision_ocr(self):
        """VisionOCR 인스턴스 (lazy loading)"""
        if self._vision_ocr is None:
            from .vision_ocr import VisionOCR
            self._vision_ocr = VisionOCR(
                credentials_path=self.config.credentials_path,
                project_id=self.config.project_id
            )
        return self._vision_ocr

    def analyze_document(
        self,
        file_path: str,
        document_type: str = "auto_detect"
    ) -> AnalysisResult:
        """OCR + LLM 문서 분석 실행"""
        start_time = time.time()

        try:
            # 1. Vision OCR로 텍스트 추출
            ocr = self._get_vision_ocr()
            ocr_result = ocr.extract_text(file_path)

            if not ocr_result.success:
                return self._create_error_result(
                    f"OCR 텍스트 추출 실패: {ocr_result.error}"
                )

            if not ocr_result.text.strip():
                return self._create_error_result(
                    "OCR 결과가 비어있습니다. 이미지 품질을 확인해주세요."
                )

            # 2. OCR 텍스트로 분석 프롬프트 생성
            prompt = get_ocr_analysis_prompt(document_type, ocr_result.text)

            # 3. 텍스트 전용 메시지 구성
            messages = self._build_text_messages(prompt)

            # 4. LLM API 호출
            response = self._call_api(messages)

            # 5. 응답 파싱
            response_text = response.get('choices', [{}])[0].get('message', {}).get('content', '')

            # JSON 추출
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
        except requests.exceptions.Timeout:
            return self._create_error_result(
                f"요청 시간 초과 ({self.config.timeout}초). 모델 로딩 또는 서버 응답 지연."
            )
        except requests.exceptions.RequestException as e:
            return self._create_error_result(f"API 요청 오류: {str(e)}")
        except Exception as e:
            return self._create_error_result(f"분석 오류: {str(e)}")

    def _build_text_messages(self, prompt: str) -> List[Dict[str, Any]]:
        """텍스트 전용 메시지 구성"""
        return [{
            "role": "user",
            "content": prompt
        }]

    def _call_api(self, messages: List[Dict[str, Any]]) -> Dict[str, Any]:
        """LM Studio API 호출"""
        url = f"{self._endpoint}{self.API_PATH}"

        payload = {
            "model": self.config.model_name,
            "messages": messages,
            "max_tokens": self.config.max_tokens,
            "temperature": self.config.temperature,
            "stream": False
        }

        response = requests.post(
            url,
            json=payload,
            timeout=self.config.timeout,
            headers={"Content-Type": "application/json"}
        )

        response.raise_for_status()
        return response.json()
