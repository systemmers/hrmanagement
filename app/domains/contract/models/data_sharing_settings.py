"""
DataSharingSettings SQLAlchemy Model

계약별 데이터 공유 설정을 관리하는 모델입니다.

Phase 5: 구조화 - contract/ 폴더로 분리
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
Phase 2 Migration: app/domains/contract/models/로 이동
Phase 33: 파일 공유 설정 필드 추가
"""
from datetime import datetime
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class DataSharingSettings(DictSerializableMixin, db.Model):
    """데이터 공유 설정 모델"""
    __tablename__ = 'data_sharing_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('person_corporate_contracts.id'),
        nullable=False,
        unique=True
    )

    # 공유 항목 설정
    share_basic_info = db.Column(db.Boolean, default=True)
    share_contact = db.Column(db.Boolean, default=True)
    share_education = db.Column(db.Boolean, default=False)
    share_career = db.Column(db.Boolean, default=False)
    share_certificates = db.Column(db.Boolean, default=False)
    share_languages = db.Column(db.Boolean, default=False)
    share_military = db.Column(db.Boolean, default=False)

    # Phase 33: 파일 공유 설정
    share_profile_photo = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='프로필 사진 공유 여부'
    )
    share_documents = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment='일반 첨부 문서 공유 여부'
    )
    share_certificate_files = db.Column(
        db.Boolean,
        default=False,
        nullable=False,
        comment='자격증 증빙 파일 공유 여부'
    )

    # 실시간 동기화 설정
    is_realtime_sync = db.Column(db.Boolean, default=False)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DataSharingSettings contract_id={self.contract_id}>'

    def should_share_attachments(self, category: str) -> bool:
        """특정 카테고리의 첨부파일 공유 여부 확인

        Args:
            category: 첨부파일 카테고리 (profile_photo, document, certificate 등)

        Returns:
            공유 여부
        """
        from app.domains.attachment.constants import AttachmentCategory

        category_mapping = {
            AttachmentCategory.PROFILE_PHOTO: self.share_profile_photo,
            AttachmentCategory.DOCUMENT: self.share_documents,
            'certificate': self.share_certificate_files,  # 자격증 증빙
        }
        return category_mapping.get(category, False)
