"""
Attachment 도메인 상수 정의

첨부파일 카테고리 및 소유자 타입 상수 (SSOT)
"""


class AttachmentCategory:
    """첨부파일 카테고리 상수"""
    ATTACHMENT = 'attachments'
    PROFILE_PHOTO = 'profile_photo'
    BUSINESS_CARD_FRONT = 'business_card_front'
    BUSINESS_CARD_BACK = 'business_card_back'
    COMPANY_DOCUMENT = 'documents'
    ADMIN_PHOTO = 'admin_photos'

    # 카테고리 목록
    ALL_CATEGORIES = [
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
