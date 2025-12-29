"""
관계형 데이터 동기화 서비스 (호환성 래퍼)

[DEPRECATED] 기존 경로 호환성 유지
새 코드는 다음을 사용하세요:
    from app.services.sync import SyncRelationService

Phase 5: 구조화 - sync/ 폴더로 이동, 이 파일은 호환성 래퍼로 유지
"""

from app.services.sync.sync_relation_service import SyncRelationService

__all__ = ['SyncRelationService']
