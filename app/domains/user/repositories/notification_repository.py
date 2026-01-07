"""
Notification Repository

알림의 CRUD 및 조회를 처리합니다.

Phase 7: 도메인 중심 마이그레이션 완료
Phase 30: 레이어 분리 - Service의 Model.query 직접 사용 제거
"""
from typing import Optional, List, Dict, Any
from datetime import datetime
from app.database import db
from app.domains.user.models import Notification, NotificationPreference
from app.shared.repositories.base_repository import BaseRepository


class NotificationRepository(BaseRepository[Notification]):
    """알림 Repository"""

    def __init__(self):
        super().__init__(Notification)

    def find_by_user_id(
        self,
        user_id: int,
        unread_only: bool = False,
        limit: int = 50
    ) -> List[Notification]:
        """사용자 ID로 알림 조회

        Args:
            user_id: User ID
            unread_only: True면 읽지 않은 알림만
            limit: 최대 조회 건수

        Returns:
            Notification 목록
        """
        query = Notification.query.filter_by(user_id=user_id)
        if unread_only:
            query = query.filter_by(is_read=False)
        return query.order_by(Notification.created_at.desc()).limit(limit).all()

    def create_notification(
        self,
        user_id: int,
        notification_type: str,
        title: str,
        message: str = None,
        resource_type: str = None,
        resource_id: int = None,
        sender_id: int = None,
        priority: str = None,
        action_url: str = None,
        action_label: str = None,
        extra_data: str = None,
        commit: bool = True
    ) -> Notification:
        """알림 생성

        Args:
            user_id: 수신자 User ID
            notification_type: 알림 유형
            title: 알림 제목
            message: 알림 메시지 (선택)
            resource_type: 관련 리소스 유형 (선택)
            resource_id: 관련 리소스 ID (선택)
            sender_id: 발신자 User ID (선택)
            priority: 우선순위 (선택)
            action_url: 액션 URL (선택)
            action_label: 액션 라벨 (선택)
            extra_data: 추가 데이터 JSON (선택)
            commit: True면 즉시 커밋

        Returns:
            생성된 Notification 모델
        """
        notification = Notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            sender_id=sender_id,
            priority=priority or Notification.PRIORITY_NORMAL,
            action_url=action_url,
            action_label=action_label,
            extra_data=extra_data
        )
        db.session.add(notification)
        if commit:
            db.session.commit()
        return notification

    def mark_as_read(
        self,
        notification_id: int,
        commit: bool = True
    ) -> Optional[Notification]:
        """알림을 읽음으로 표시

        Args:
            notification_id: 알림 ID
            commit: True면 즉시 커밋

        Returns:
            업데이트된 Notification 또는 None
        """
        notification = self.find_by_id(notification_id)
        if notification:
            notification.mark_as_read()
            if commit:
                db.session.commit()
        return notification

    def mark_all_as_read(
        self,
        user_id: int,
        commit: bool = True
    ) -> int:
        """사용자의 모든 알림을 읽음으로 표시

        Args:
            user_id: User ID
            commit: True면 즉시 커밋

        Returns:
            업데이트된 알림 건수
        """
        count = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })
        if commit:
            db.session.commit()
        return count

    def count_unread(self, user_id: int) -> int:
        """읽지 않은 알림 건수 조회

        Args:
            user_id: User ID

        Returns:
            읽지 않은 알림 건수
        """
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).count()

    def find_by_type(
        self,
        user_id: int,
        notification_type: str,
        limit: int = 50
    ) -> List[Notification]:
        """알림 유형별 조회

        Args:
            user_id: User ID
            notification_type: 알림 유형
            limit: 최대 조회 건수

        Returns:
            Notification 목록
        """
        return Notification.query.filter_by(
            user_id=user_id,
            notification_type=notification_type
        ).order_by(Notification.created_at.desc()).limit(limit).all()

    def delete_by_user_id(self, user_id: int, commit: bool = True) -> int:
        """사용자의 모든 알림 삭제

        Args:
            user_id: User ID
            commit: True면 즉시 커밋

        Returns:
            삭제된 알림 건수
        """
        count = Notification.query.filter_by(user_id=user_id).delete()
        if commit:
            db.session.commit()
        return count

    def delete_old_notifications(
        self,
        days: int = 30,
        commit: bool = True
    ) -> int:
        """오래된 알림 삭제

        Args:
            days: 기준 일수
            commit: True면 즉시 커밋

        Returns:
            삭제된 알림 건수
        """
        from datetime import timedelta
        cutoff_date = datetime.utcnow() - timedelta(days=days)
        count = Notification.query.filter(
            Notification.created_at < cutoff_date,
            Notification.is_read == True
        ).delete()
        if commit:
            db.session.commit()
        return count

    def find_paginated(
        self,
        user_id: int,
        unread_only: bool = False,
        notification_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Notification]:
        """알림 목록 조회 (페이지네이션 + 만료 체크)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID
            unread_only: 읽지 않은 알림만
            notification_type: 알림 유형 필터
            limit: 최대 조회 건수
            offset: 시작 오프셋

        Returns:
            Notification 목록
        """
        query = Notification.query.filter_by(user_id=user_id)

        # 만료되지 않은 알림만
        query = query.filter(
            db.or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        )

        if unread_only:
            query = query.filter_by(is_read=False)

        if notification_type:
            query = query.filter_by(notification_type=notification_type)

        return query.order_by(
            Notification.created_at.desc()
        ).offset(offset).limit(limit).all()

    def count_unread_valid(self, user_id: int) -> int:
        """읽지 않은 유효한 알림 건수 (만료 체크 포함)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID

        Returns:
            읽지 않은 유효 알림 건수
        """
        return Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        ).filter(
            db.or_(
                Notification.expires_at.is_(None),
                Notification.expires_at > datetime.utcnow()
            )
        ).count()

    def find_one_by_id_and_user(
        self,
        notification_id: int,
        user_id: int = None
    ) -> Optional[Notification]:
        """ID와 사용자로 알림 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            notification_id: 알림 ID
            user_id: 사용자 ID (선택)

        Returns:
            Notification 또는 None
        """
        query = Notification.query.filter_by(id=notification_id)
        if user_id:
            query = query.filter_by(user_id=user_id)
        return query.first()

    def mark_all_as_read_with_type(
        self,
        user_id: int,
        notification_type: str = None,
        commit: bool = True
    ) -> int:
        """알림 유형별 읽음 처리

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID
            notification_type: 알림 유형 (선택)
            commit: 즉시 커밋 여부

        Returns:
            업데이트된 건수
        """
        query = Notification.query.filter_by(
            user_id=user_id,
            is_read=False
        )

        if notification_type:
            query = query.filter_by(notification_type=notification_type)

        count = query.update({
            'is_read': True,
            'read_at': datetime.utcnow()
        })

        if commit:
            db.session.commit()
        return count

    def count_by_period(
        self,
        user_id: int,
        start_date: datetime
    ) -> int:
        """기간별 알림 건수 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID
            start_date: 시작 일시

        Returns:
            알림 건수
        """
        return Notification.query.filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_date
        ).count()

    def count_unread_all(self, user_id: int) -> int:
        """읽지 않은 전체 알림 건수 (만료 무관)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID

        Returns:
            읽지 않은 알림 건수
        """
        return Notification.query.filter(
            Notification.user_id == user_id,
            Notification.is_read == False
        ).count()

    def get_type_stats(
        self,
        user_id: int,
        start_date: datetime
    ) -> List[tuple]:
        """유형별 알림 통계 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            user_id: 사용자 ID
            start_date: 시작 일시

        Returns:
            (notification_type, count) 튜플 리스트
        """
        return db.session.query(
            Notification.notification_type,
            db.func.count(Notification.id)
        ).filter(
            Notification.user_id == user_id,
            Notification.created_at >= start_date
        ).group_by(Notification.notification_type).all()

    def delete_one(
        self,
        notification_id: int,
        user_id: int,
        commit: bool = True
    ) -> bool:
        """단일 알림 삭제

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            notification_id: 알림 ID
            user_id: 사용자 ID
            commit: 즉시 커밋 여부

        Returns:
            삭제 성공 여부
        """
        notification = self.find_one_by_id_and_user(notification_id, user_id)
        if not notification:
            return False

        db.session.delete(notification)
        if commit:
            db.session.commit()
        return True


class NotificationPreferenceRepository(BaseRepository[NotificationPreference]):
    """알림 설정 Repository"""

    def __init__(self):
        super().__init__(NotificationPreference)

    def find_by_user_id(self, user_id: int) -> Optional[NotificationPreference]:
        """사용자 ID로 알림 설정 조회

        Args:
            user_id: User ID

        Returns:
            NotificationPreference 또는 None
        """
        return NotificationPreference.query.filter_by(user_id=user_id).first()

    def find_or_create_for_user(
        self,
        user_id: int,
        commit: bool = True
    ) -> NotificationPreference:
        """사용자의 알림 설정 조회 또는 생성

        Args:
            user_id: User ID
            commit: True면 즉시 커밋

        Returns:
            NotificationPreference 모델
        """
        pref = self.find_by_user_id(user_id)
        if pref:
            return pref

        pref = NotificationPreference(user_id=user_id)
        db.session.add(pref)
        if commit:
            db.session.commit()
        return pref

    def update_preferences(
        self,
        user_id: int,
        settings: Dict[str, Any],
        commit: bool = True
    ) -> Optional[NotificationPreference]:
        """알림 설정 업데이트

        Args:
            user_id: User ID
            settings: 업데이트할 설정 값
            commit: True면 즉시 커밋

        Returns:
            업데이트된 NotificationPreference 또는 None
        """
        pref = self.find_or_create_for_user(user_id, commit=False)

        for key, value in settings.items():
            if hasattr(pref, key):
                setattr(pref, key, value)

        if commit:
            db.session.commit()
        return pref


# 싱글톤 인스턴스
notification_repository = NotificationRepository()
notification_preference_repository = NotificationPreferenceRepository()
