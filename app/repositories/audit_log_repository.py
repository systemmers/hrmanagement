"""
AuditLog Repository

감사 로그 CRUD 및 조회를 처리합니다.

Phase 31: 컨벤션 준수 - Service의 Model.query/db.session 직접 사용 제거
"""
from typing import List, Optional, Dict, Any
from datetime import datetime

from app.database import db
from app.models.audit_log import AuditLog
from .base_repository import BaseRepository


class AuditLogRepository(BaseRepository[AuditLog]):
    """감사 로그 Repository"""

    def __init__(self):
        super().__init__(AuditLog)

    def create_log(
        self,
        action: str,
        resource_type: str,
        resource_id: int = None,
        user_id: int = None,
        account_type: str = None,
        company_id: int = None,
        details: str = None,
        ip_address: str = None,
        user_agent: str = None,
        endpoint: str = None,
        method: str = None,
        status: str = AuditLog.STATUS_SUCCESS,
        error_message: str = None,
        commit: bool = True
    ) -> AuditLog:
        """감사 로그 생성

        Args:
            action: 액션 유형 (view, create, update, delete 등)
            resource_type: 리소스 유형
            기타 파라미터: 로그 상세 정보
            commit: True면 즉시 커밋

        Returns:
            생성된 AuditLog 모델
        """
        log = AuditLog(
            user_id=user_id,
            account_type=account_type,
            company_id=company_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            details=details,
            ip_address=ip_address,
            user_agent=user_agent,
            endpoint=endpoint,
            method=method,
            status=status,
            error_message=error_message,
        )
        db.session.add(log)
        if commit:
            db.session.commit()
        return log

    def find_logs(
        self,
        user_id: int = None,
        company_id: int = None,
        action: str = None,
        resource_type: str = None,
        resource_id: int = None,
        status: str = None,
        start_date: datetime = None,
        end_date: datetime = None,
        limit: int = 100,
        offset: int = 0
    ) -> List[AuditLog]:
        """감사 로그 조회

        Args:
            다양한 필터 조건

        Returns:
            AuditLog 모델 리스트
        """
        query = AuditLog.query

        if user_id:
            query = query.filter_by(user_id=user_id)
        if company_id:
            query = query.filter_by(company_id=company_id)
        if action:
            query = query.filter_by(action=action)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)
        if resource_id:
            query = query.filter_by(resource_id=resource_id)
        if status:
            query = query.filter_by(status=status)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)
        if end_date:
            query = query.filter(AuditLog.created_at <= end_date)

        return query.order_by(AuditLog.created_at.desc()).offset(offset).limit(limit).all()

    def count_logs(
        self,
        user_id: int = None,
        company_id: int = None,
        action: str = None,
        resource_type: str = None
    ) -> int:
        """감사 로그 개수 조회

        Args:
            다양한 필터 조건

        Returns:
            로그 개수
        """
        query = AuditLog.query

        if company_id:
            query = query.filter_by(company_id=company_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        if action:
            query = query.filter_by(action=action)
        if resource_type:
            query = query.filter_by(resource_type=resource_type)

        return query.count()

    def find_for_resource(
        self,
        resource_type: str,
        resource_id: int,
        action: str = None,
        start_date: datetime = None,
        limit: int = 50
    ) -> List[AuditLog]:
        """특정 리소스의 로그 조회

        Args:
            resource_type: 리소스 유형
            resource_id: 리소스 ID
            action: 액션 필터 (선택)
            start_date: 시작 날짜 (선택)
            limit: 조회 제한

        Returns:
            AuditLog 모델 리스트
        """
        query = AuditLog.query.filter(
            AuditLog.resource_type == resource_type,
            AuditLog.resource_id == resource_id
        )

        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.created_at >= start_date)

        return query.order_by(AuditLog.created_at.desc()).limit(limit).all()


# 싱글톤 인스턴스
audit_log_repository = AuditLogRepository()
