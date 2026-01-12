"""
Attachment SQLAlchemy 모델

범용 첨부파일 정보를 관리합니다.
Phase 31: 독립 도메인으로 분리 + owner_type/owner_id 범용화
Phase 33: source 추적 필드 추가 (계약 기반 동기화/분리)
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


class SourceType:
    """첨부파일 출처 타입"""
    SYNCED = 'synced'        # 개인 → 법인 동기화됨
    CORPORATE = 'corporate'  # 법인에서 직접 생성
    PERSONAL = 'personal'    # 개인에서 직접 생성


class Attachment(DictSerializableMixin, db.Model):
    """첨부파일 모델 (범용)"""
    __tablename__ = 'attachments'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    # 범용 소유자 (Polymorphic)
    owner_type = db.Column(db.String(50), nullable=False, index=True)  # 'employee', 'profile', 'company'
    owner_id = db.Column(db.Integer, nullable=False, index=True)

    # 레거시 호환성 (Phase 6까지 유지)
    employee_id = db.Column(db.Integer, db.ForeignKey('employees.id'), nullable=True, index=True)

    # 파일 정보
    file_name = db.Column(db.String(500), nullable=True)
    file_path = db.Column(db.String(1000), nullable=True)
    file_type = db.Column(db.String(100), nullable=True)
    file_size = db.Column(db.Integer, default=0)
    category = db.Column(db.String(100), nullable=True, index=True)
    upload_date = db.Column(db.String(20), nullable=True)
    note = db.Column(db.Text, nullable=True)

    # 순서 정렬
    display_order = db.Column(db.Integer, default=0, nullable=False)

    # Phase 33: 계약 기반 동기화/분리 추적
    source_type = db.Column(
        db.String(20),
        nullable=True,
        index=True,
        comment='출처 타입: synced(동기화), corporate(법인생성), personal(개인생성)'
    )
    source_contract_id = db.Column(
        db.Integer,
        db.ForeignKey('person_corporate_contracts.id'),
        nullable=True,
        index=True,
        comment='동기화 출처 계약 ID'
    )
    is_deletable_on_termination = db.Column(
        db.Boolean,
        default=True,
        nullable=False,
        comment='계약 해지 시 삭제 여부'
    )

    # 복합 인덱스는 마이그레이션에서 정의됨
    # ix_attachments_owner, ix_attachments_owner_category

    def __repr__(self):
        return f'<Attachment {self.id}: {self.file_name} ({self.owner_type}:{self.owner_id})>'

    def is_synced(self) -> bool:
        """동기화된 파일인지 확인"""
        return self.source_type == SourceType.SYNCED

    def can_delete_on_termination(self) -> bool:
        """계약 해지 시 삭제 가능 여부"""
        return self.is_deletable_on_termination and self.is_synced()
