"""
Attachment 도메인 상수 정의

첨부파일 카테고리 및 소유자 타입 상수 (SSOT)
"""


class AttachmentCategory:
    """첨부파일 카테고리 상수"""
    # 일반 카테고리
    DOCUMENT = 'document'           # 일반 문서 (기본값)
    ATTACHMENT = 'attachments'      # 첨부파일 (레거시)

    # 특수 카테고리
    PROFILE_PHOTO = 'profile_photo'
    BUSINESS_CARD_FRONT = 'business_card_front'
    BUSINESS_CARD_BACK = 'business_card_back'
    COMPANY_DOCUMENT = 'documents'  # 법인 문서
    ADMIN_PHOTO = 'admin_photos'

    # 카테고리 목록
    ALL_CATEGORIES = [
        DOCUMENT,
        ATTACHMENT,
        PROFILE_PHOTO,
        BUSINESS_CARD_FRONT,
        BUSINESS_CARD_BACK,
        COMPANY_DOCUMENT,
        ADMIN_PHOTO,
    ]


class OwnerType:
    """첨부파일 소유자 타입 상수"""
    EMPLOYEE = 'employee'
    PROFILE = 'profile'
    COMPANY = 'company'
    USER = 'user'

    # 소유자 타입 목록
    ALL_TYPES = [
        EMPLOYEE,
        PROFILE,
        COMPANY,
        USER,
    ]


class LinkedEntityType:
    """
    연결 엔티티 타입 상수 (Phase 4.2)

    학력/경력/자격증 등의 항목에 증빙 서류를 연결할 때 사용
    """
    EDUCATION = 'education'      # 학력 증빙 (졸업증명서 등)
    CAREER = 'career'            # 경력 증빙 (경력증명서 등)
    CERTIFICATE = 'certificate'  # 자격증 증빙 (자격증 사본 등)
    LANGUAGE = 'language'        # 어학 증빙 (성적표 등)
    TRAINING = 'training'        # 교육 증빙 (수료증 등)
    AWARD = 'award'              # 수상 증빙 (상장 사본 등)
    MILITARY = 'military'        # 병역 증빙 (병역증명서 등)

    # 연결 엔티티 타입 목록
    ALL_TYPES = [
        EDUCATION,
        CAREER,
        CERTIFICATE,
        LANGUAGE,
        TRAINING,
        AWARD,
        MILITARY,
    ]

    # 한글 레이블
    LABELS = {
        EDUCATION: '학력',
        CAREER: '경력',
        CERTIFICATE: '자격증',
        LANGUAGE: '어학',
        TRAINING: '교육/연수',
        AWARD: '수상/표창',
        MILITARY: '병역',
    }

    @classmethod
    def get_label(cls, entity_type: str) -> str:
        """연결 엔티티 타입의 한글 레이블 반환"""
        return cls.LABELS.get(entity_type, entity_type)
