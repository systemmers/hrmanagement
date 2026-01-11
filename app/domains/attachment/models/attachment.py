"""
Attachment SQLAlchemy 모델

범용 첨부파일 정보를 관리합니다.
Phase 31: 독립 도메인으로 분리 + owner_type/owner_id 범용화
"""
from app.database import db
from app.shared.models.mixins import DictSerializableMixin


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

    # 복합 인덱스는 마이그레이션에서 정의됨
    # ix_attachments_owner, ix_attachments_owner_category

    def __repr__(self):
        return f'<Attachment {self.id}: {self.file_name} ({self.owner_type}:{self.owner_id})>'
