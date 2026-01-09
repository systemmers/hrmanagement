"""
shared/models - 공유 모델 유틸리티

DictSerializableMixin 등 모든 도메인에서 사용하는 Mixin 제공
"""
from .mixins import DictSerializableMixin, TimestampMixin, SoftDeleteMixin

__all__ = ['DictSerializableMixin', 'TimestampMixin', 'SoftDeleteMixin']
