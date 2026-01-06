"""
SystemSetting SQLAlchemy 모델

시스템 전역 설정을 관리합니다.
사번 규칙, 이메일 도메인, 회사 정보 등을 저장합니다.

Phase 7: 도메인 중심 마이그레이션 (app/domains/platform/models/)
"""
from datetime import datetime
from app.database import db


class SystemSetting(db.Model):
    """시스템 설정 모델"""
    __tablename__ = 'system_settings'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    key = db.Column(db.String(100), unique=True, nullable=False, index=True)
    value = db.Column(db.Text, nullable=True)
    value_type = db.Column(db.String(20), nullable=False, default='string')
    # value_type: string, integer, boolean, json, float
    description = db.Column(db.String(500), nullable=True)
    category = db.Column(db.String(50), nullable=True, index=True)
    # category: company, employee_number, email, system, etc.
    is_editable = db.Column(db.Boolean, default=True)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # Value type constants
    TYPE_STRING = 'string'
    TYPE_INTEGER = 'integer'
    TYPE_BOOLEAN = 'boolean'
    TYPE_JSON = 'json'
    TYPE_FLOAT = 'float'

    VALID_TYPES = [TYPE_STRING, TYPE_INTEGER, TYPE_BOOLEAN, TYPE_JSON, TYPE_FLOAT]

    def get_typed_value(self):
        """타입에 맞게 변환된 값 반환"""
        if self.value is None:
            return None

        if self.value_type == self.TYPE_INTEGER:
            return int(self.value)
        elif self.value_type == self.TYPE_FLOAT:
            return float(self.value)
        elif self.value_type == self.TYPE_BOOLEAN:
            return self.value.lower() in ('true', '1', 'yes')
        elif self.value_type == self.TYPE_JSON:
            import json
            return json.loads(self.value)
        else:
            return self.value

    def set_typed_value(self, value):
        """타입에 맞게 값 설정"""
        if value is None:
            self.value = None
            return

        if self.value_type == self.TYPE_JSON:
            import json
            self.value = json.dumps(value, ensure_ascii=False)
        elif self.value_type == self.TYPE_BOOLEAN:
            self.value = 'true' if value else 'false'
        else:
            self.value = str(value)

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'key': self.key,
            'value': self.value,
            'typedValue': self.get_typed_value(),
            'valueType': self.value_type,
            'description': self.description,
            'category': self.category,
            'isEditable': self.is_editable,
            'updatedAt': self.updated_at.isoformat() if self.updated_at else None,
            'createdAt': self.created_at.isoformat() if self.created_at else None,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        instance = cls(
            key=data.get('key'),
            value_type=data.get('valueType', cls.TYPE_STRING),
            description=data.get('description'),
            category=data.get('category'),
            is_editable=data.get('isEditable', True),
        )
        # typedValue가 있으면 타입에 맞게 설정
        if 'typedValue' in data:
            instance.set_typed_value(data['typedValue'])
        elif 'value' in data:
            instance.value = data['value']
        return instance

    def __repr__(self):
        return f'<SystemSetting {self.key}={self.value}>'
