"""
Google Document AI Provider

Google Cloud Document AI를 사용한 문서 분석
- 고품질 OCR 및 구조화된 데이터 추출
- 다양한 문서 유형 지원 (PDF, 이미지)
- 사전 학습된 프로세서 활용
"""
import json
import time
import mimetypes
from typing import Optional, Dict, Any

from .base import BaseAIProvider, AnalysisResult, ProviderConfig


class DocumentAIProvider(BaseAIProvider):
    """Google Cloud Document AI Provider"""

    def __init__(self, config: ProviderConfig):
        super().__init__(config)
        self._client = None

    @property
    def name(self) -> str:
        return "document_ai"

    @property
    def is_available(self) -> bool:
        """Document AI 사용 가능 여부"""
        return bool(
            self.config.project_id and
            self.config.location and
            self.config.processor_id
        )

    def _get_client(self):
        """Document AI 클라이언트 초기화 (lazy loading)"""
        if self._client is None:
            try:
                from google.cloud import documentai_v1 as documentai
                import os

                # 인증 설정
                if self.config.credentials_path:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self.config.credentials_path

                self._client = documentai.DocumentProcessorServiceClient()
            except ImportError:
                raise ImportError(
                    "google-cloud-documentai 패키지가 설치되지 않았습니다. "
                    "pip install google-cloud-documentai 명령으로 설치해주세요."
                )
        return self._client

    def analyze_document(
        self,
        file_path: str,
        document_type: str = "auto_detect"
    ) -> AnalysisResult:
        """Document AI로 문서 분석"""
        if not self.is_available:
            return self._create_error_result(
                "Document AI 설정이 완료되지 않았습니다. "
                "GOOGLE_PROJECT_ID, GOOGLE_LOCATION, DOCUMENTAI_PROCESSOR_ID를 확인해주세요."
            )

        start_time = time.time()

        try:
            from google.cloud import documentai_v1 as documentai

            client = self._get_client()

            # 파일 읽기
            file_bytes = self._read_file_as_bytes(file_path)
            mime_type = self._get_mime_type(file_path)

            # 프로세서 이름 구성
            processor_name = client.processor_path(
                self.config.project_id,
                self.config.location,
                self.config.processor_id
            )

            # Document AI 요청 구성
            raw_document = documentai.RawDocument(
                content=file_bytes,
                mime_type=mime_type
            )

            request = documentai.ProcessRequest(
                name=processor_name,
                raw_document=raw_document
            )

            # 문서 처리
            result = client.process_document(request=request)
            document = result.document

            # 텍스트 추출
            extracted_text = document.text

            # 엔티티 추출
            extracted_fields = self._extract_entities(document)

            # 신뢰도 계산
            confidence = self._calculate_confidence(document)

            processing_time = time.time() - start_time

            # 문서 유형 결정
            detected_type = self._detect_document_type(extracted_fields, document_type)

            return AnalysisResult(
                success=True,
                document_type=detected_type,
                confidence=confidence,
                extracted_fields=extracted_fields,
                raw_response=extracted_text,
                processing_time=processing_time,
                provider=self.name
            )

        except ImportError as e:
            return self._create_error_result(str(e))
        except Exception as e:
            return self._create_error_result(f"Document AI 처리 오류: {str(e)}")

    def _extract_entities(self, document) -> Dict[str, Any]:
        """Document AI 응답에서 엔티티 추출"""
        entities = {}

        try:
            # 엔티티 추출
            for entity in document.entities:
                key = entity.type_
                value = entity.mention_text

                # 중복 키 처리 (리스트로 변환)
                if key in entities:
                    if isinstance(entities[key], list):
                        entities[key].append(value)
                    else:
                        entities[key] = [entities[key], value]
                else:
                    entities[key] = value

            # 전체 텍스트도 포함
            entities['full_text'] = document.text

            # 페이지 정보
            entities['page_count'] = len(document.pages)

        except Exception:
            entities['full_text'] = document.text if hasattr(document, 'text') else ""

        return entities

    def _calculate_confidence(self, document) -> float:
        """문서 신뢰도 계산"""
        try:
            confidences = []

            # 엔티티 신뢰도
            for entity in document.entities:
                if hasattr(entity, 'confidence') and entity.confidence:
                    confidences.append(entity.confidence)

            # 페이지별 블록 신뢰도
            for page in document.pages:
                for block in page.blocks:
                    if hasattr(block.layout, 'confidence') and block.layout.confidence:
                        confidences.append(block.layout.confidence)

            if confidences:
                return sum(confidences) / len(confidences)

            return 0.8  # 기본 신뢰도

        except Exception:
            return 0.5

    def _detect_document_type(self, extracted_fields: Dict, hint: str) -> str:
        """추출된 필드로 문서 유형 추정"""
        if hint != "auto_detect":
            return hint

        # 키워드 기반 문서 유형 판별
        full_text = extracted_fields.get('full_text', '').lower()

        if '이력서' in full_text or 'resume' in full_text:
            return 'resume'
        elif '경력증명서' in full_text or '재직증명서' in full_text:
            return 'career_certificate'
        elif '졸업증명서' in full_text or '학위증명서' in full_text:
            return 'education_certificate'
        elif '주민등록' in full_text:
            return 'id_card'
        elif '통장' in full_text or '계좌' in full_text:
            return 'bank_statement'

        return 'other'
