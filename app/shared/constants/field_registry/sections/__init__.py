"""
Field Registry Sections

섹션 정의 모듈. 각 파일에서 섹션을 정의하고 FieldRegistry에 등록.
"""
# 섹션 정의 임포트 (자동 등록)
from . import personal
from . import organization
from . import relations

__all__ = ['personal', 'organization', 'relations']
