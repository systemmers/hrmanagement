"""
SyncLog SQLAlchemy Model

데이터 동기화 이력을 관리하는 모델입니다.

Phase 5: 구조화 - contract/ 폴더로 분리
Phase 8: DictSerializableMixin 적용
Phase 29: __dict_camel_mapping__ 제거
"""
from datetime import datetime
from app.database import db
from app.domains.employee.models import DictSerializableMixin


class SyncLog(DictSerializableMixin, db.Model):
    """동기화 이력 모델"""
    __tablename__ = 'sync_logs'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    contract_id = db.Column(
        db.Integer,
        db.ForeignKey('person_corporate_contracts.id'),
        nullable=False,
        index=True
    )

    # 동기화 정보
    sync_type = db.Column(db.String(30), nullable=False)
    entity_type = db.Column(db.String(50), nullable=False)
    field_name = db.Column(db.String(100), nullable=True)
    old_value = db.Column(db.Text, nullable=True)
    new_value = db.Column(db.Text, nullable=True)
    direction = db.Column(db.String(20), nullable=True)

    # 실행 정보
    executed_by = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    executed_at = db.Column(db.DateTime, default=datetime.utcnow)

    # 동기화 유형 상수
    SYNC_TYPE_AUTO = 'auto'
    SYNC_TYPE_MANUAL = 'manual'
    SYNC_TYPE_INITIAL = 'initial'

    def __repr__(self):
        return f'<SyncLog {self.id}: {self.sync_type} {self.entity_type}>'

    @classmethod
    def create_log(cls, contract_id, sync_type, entity_type, **kwargs):
        """동기화 로그 생성"""
        return cls(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type=entity_type,
            field_name=kwargs.get('field_name'),
            old_value=kwargs.get('old_value'),
            new_value=kwargs.get('new_value'),
            direction=kwargs.get('direction'),
            executed_by=kwargs.get('user_id'),
        )
