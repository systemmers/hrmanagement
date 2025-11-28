"""
ClassificationOption SQLAlchemy 모델

분류 옵션 (부서, 직급, 재직상태 등) 정보를 관리합니다.
"""
from app.database import db


class ClassificationOption(db.Model):
    """분류 옵션 모델"""
    __tablename__ = 'classification_options'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    category = db.Column(db.String(50), nullable=False, index=True)
    value = db.Column(db.String(100), nullable=False)
    label = db.Column(db.String(200), nullable=True)
    sort_order = db.Column(db.Integer, default=0)

    __table_args__ = (
        db.UniqueConstraint('category', 'value', name='uq_category_value'),
    )

    def to_dict(self):
        """딕셔너리 반환"""
        return {
            'id': self.id,
            'category': self.category,
            'value': self.value,
            'label': self.label,
            'sortOrder': self.sort_order,
        }

    @classmethod
    def from_dict(cls, data):
        """딕셔너리에서 모델 생성"""
        return cls(
            category=data.get('category'),
            value=data.get('value'),
            label=data.get('label'),
            sort_order=data.get('sortOrder', 0),
        )

    def __repr__(self):
        return f'<ClassificationOption {self.category}: {self.value}>'
