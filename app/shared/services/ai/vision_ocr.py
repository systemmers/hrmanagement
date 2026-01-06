"""
Google Cloud Vision OCR

Google Cloud Vision API를 사용한 고품질 OCR 텍스트 추출
- 이미지 파일: jpg, png, gif, bmp, webp 등
- 문서 파일: PDF (첫 페이지 또는 전체 페이지)
기존 GCP 서비스 계정 인증 활용
"""
from dataclasses import dataclass
from typing import Optional, List
import os
import mimetypes


@dataclass
class OCRResult:
    """OCR 추출 결과"""
    success: bool
    text: str
    confidence: float
    language: Optional[str] = None
    error: Optional[str] = None

    def to_dict(self) -> dict:
        """딕셔너리로 변환"""
        return {
            'success': self.success,
            'text': self.text,
            'confidence': self.confidence,
            'language': self.language,
            'error': self.error
        }


class VisionOCR:
    """Google Cloud Vision OCR 유틸리티"""

    def __init__(
        self,
        credentials_path: Optional[str] = None,
        project_id: Optional[str] = None
    ):
        """초기화

        Args:
            credentials_path: GCP 서비스 계정 JSON 경로
            project_id: GCP 프로젝트 ID
        """
        self._credentials_path = credentials_path
        self._project_id = project_id
        self._client = None

    @property
    def is_available(self) -> bool:
        """Vision API 사용 가능 여부"""
        try:
            self._get_client()
            return True
        except Exception:
            return False

    def _get_client(self):
        """Vision API 클라이언트 초기화 (lazy loading)"""
        if self._client is None:
            try:
                from google.cloud import vision

                # 인증 설정
                if self._credentials_path:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = self._credentials_path

                self._client = vision.ImageAnnotatorClient()
            except ImportError:
                raise ImportError(
                    "google-cloud-vision 패키지가 설치되지 않았습니다. "
                    "pip install google-cloud-vision 명령으로 설치해주세요."
                )
        return self._client

    def extract_text(self, file_path: str, max_pages: int = 5) -> OCRResult:
        """파일에서 텍스트 추출

        Args:
            file_path: 이미지 또는 PDF 파일 경로
            max_pages: PDF의 경우 최대 처리 페이지 수

        Returns:
            OCRResult: OCR 추출 결과
        """
        try:
            mime_type, _ = mimetypes.guess_type(file_path)

            # PDF 파일 처리
            if mime_type == 'application/pdf' or file_path.lower().endswith('.pdf'):
                return self._extract_text_from_pdf(file_path, max_pages)

            # 이미지 파일 처리
            with open(file_path, 'rb') as f:
                content = f.read()
            return self.extract_text_from_bytes(content)

        except FileNotFoundError:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error=f"파일을 찾을 수 없습니다: {file_path}"
            )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error=f"파일 읽기 오류: {str(e)}"
            )

    def _extract_text_from_pdf(self, file_path: str, max_pages: int = 5) -> OCRResult:
        """PDF 파일에서 텍스트 추출

        PyMuPDF를 사용하여 PDF를 이미지로 변환 후 OCR 처리

        Args:
            file_path: PDF 파일 경로
            max_pages: 최대 처리 페이지 수

        Returns:
            OCRResult: OCR 추출 결과
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            total_pages = len(doc)
            pages_to_process = min(total_pages, max_pages)

            all_texts = []
            all_confidences = []
            detected_language = None

            for page_num in range(pages_to_process):
                page = doc[page_num]
                # 페이지를 이미지로 변환 (300 DPI)
                pix = page.get_pixmap(matrix=fitz.Matrix(300/72, 300/72))
                img_bytes = pix.tobytes("png")

                # Vision API로 OCR
                result = self.extract_text_from_bytes(img_bytes)

                if result.success and result.text:
                    all_texts.append(f"[페이지 {page_num + 1}]\n{result.text}")
                    if result.confidence > 0:
                        all_confidences.append(result.confidence)
                    if result.language and not detected_language:
                        detected_language = result.language

            doc.close()

            if not all_texts:
                return OCRResult(
                    success=False,
                    text="",
                    confidence=0.0,
                    error="PDF에서 텍스트를 추출할 수 없습니다."
                )

            avg_confidence = sum(all_confidences) / len(all_confidences) if all_confidences else 0.0

            return OCRResult(
                success=True,
                text="\n\n".join(all_texts),
                confidence=avg_confidence,
                language=detected_language
            )

        except ImportError:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error="PyMuPDF 패키지가 설치되지 않았습니다. pip install pymupdf 명령으로 설치해주세요."
            )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error=f"PDF OCR 처리 오류: {str(e)}"
            )

    def extract_text_from_bytes(self, content: bytes) -> OCRResult:
        """바이트 데이터에서 텍스트 추출

        Args:
            content: 이미지 바이트 데이터

        Returns:
            OCRResult: OCR 추출 결과
        """
        try:
            from google.cloud import vision

            client = self._get_client()

            image = vision.Image(content=content)

            # 문서 텍스트 감지 (DOCUMENT_TEXT_DETECTION)
            response = client.document_text_detection(image=image)

            if response.error.message:
                return OCRResult(
                    success=False,
                    text="",
                    confidence=0.0,
                    error=f"Vision API 오류: {response.error.message}"
                )

            # 전체 텍스트 추출
            full_text = response.full_text_annotation.text if response.full_text_annotation else ""

            # 신뢰도 계산 (페이지별 평균)
            confidence = self._calculate_confidence(response)

            # 언어 감지
            language = self._detect_language(response)

            return OCRResult(
                success=True,
                text=full_text,
                confidence=confidence,
                language=language
            )

        except ImportError as e:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error=str(e)
            )
        except Exception as e:
            return OCRResult(
                success=False,
                text="",
                confidence=0.0,
                error=f"OCR 처리 오류: {str(e)}"
            )

    def _calculate_confidence(self, response) -> float:
        """응답에서 평균 신뢰도 계산"""
        try:
            if not response.full_text_annotation or not response.full_text_annotation.pages:
                return 0.0

            confidences = []
            for page in response.full_text_annotation.pages:
                for block in page.blocks:
                    if hasattr(block, 'confidence') and block.confidence:
                        confidences.append(block.confidence)

            if confidences:
                return sum(confidences) / len(confidences)
            return 0.0
        except Exception:
            return 0.0

    def _detect_language(self, response) -> Optional[str]:
        """응답에서 주요 언어 감지"""
        try:
            if not response.full_text_annotation or not response.full_text_annotation.pages:
                return None

            for page in response.full_text_annotation.pages:
                if page.property and page.property.detected_languages:
                    # 가장 신뢰도 높은 언어 반환
                    languages = sorted(
                        page.property.detected_languages,
                        key=lambda x: x.confidence if hasattr(x, 'confidence') else 0,
                        reverse=True
                    )
                    if languages:
                        return languages[0].language_code
            return None
        except Exception:
            return None
