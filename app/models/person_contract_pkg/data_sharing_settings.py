"""
DataSharingSettings SQLAlchemy Model

계약별 데이터 공유 설정을 관리하는 모델입니다.

Phase 5: 구조화 - contract/ 폴더로 분리
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from datetime import datetime
from app.database import db
from app.domains.employee.models import DictSerializableMixin


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

    # 실시간 동기화 설정
    is_realtime_sync = db.Column(db.Boolean, default=False)

    # 타임스탬프
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<DataSharingSettings contract_id={self.contract_id}>'
