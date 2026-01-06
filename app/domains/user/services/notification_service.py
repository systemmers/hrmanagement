"""
알림 서비스

Phase 5: 알림 시스템
- 알림 생성 및 관리
- 알림 조회 및 읽음 처리
- 알림 통계

Phase 7: 도메인 중심 마이그레이션 완료
Phase 30: 레이어 분리 - Model.query, db.session 직접 사용 제거
"""
import json
from datetime import datetime, timedelta
from typing import Optional, List, Dict, Any

from flask import url_for
from app.models.notification import Notification, NotificationPreference


class NotificationService:
    """
    알림 서비스 클래스

    알림 생성, 조회, 읽음 처리 등을 담당합니다.
    """

    # ========================================
    # Repository Property 주입 (Phase 30)
    # ========================================

    @property
    def notification_repo(self):
        """지연 초기화된 알림 Repository"""
        from app.domains.user.repositories import notification_repository
        return notification_repository

    @property
    def pref_repo(self):
        """지연 초기화된 알림 설정 Repository"""
        from app.domains.user.repositories import notification_preference_repository
        return notification_preference_repository

    # ===== 알림 생성 =====

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
        extra_data: Dict = None,
        expires_at: datetime = None
    ) -> Optional[Notification]:
        """
        알림 생성

        Args:
            user_id: 수신자 ID
            notification_type: 알림 유형
            title: 제목
            message: 메시지 (선택)
            resource_type: 관련 리소스 유형 (선택)
            resource_id: 관련 리소스 ID (선택)
            sender_id: 발신자 ID (선택)
            priority: 우선순위 (선택)
            action_url: 액션 URL (선택)
            action_label: 액션 버튼 라벨 (선택)
            extra_data: 추가 데이터 (선택)
            expires_at: 만료 시간 (선택)

        Returns:
            생성된 Notification 또는 None
        """
        # 알림 수신 설정 확인
        if not self._should_receive_notification(user_id, notification_type):
            return None

        # Phase 30: Repository 사용
        notification = self.notification_repo.create_notification(
            user_id=user_id,
            notification_type=notification_type,
            title=title,
            message=message,
            resource_type=resource_type,
            resource_id=resource_id,
            sender_id=sender_id,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            extra_data=json.dumps(extra_data) if extra_data else None,
            commit=True
        )
        # expires_at는 Repository에서 지원하지 않으므로 별도 설정
        if expires_at and notification:
            notification.expires_at = expires_at

        return notification

    def _should_receive_notification(self, user_id: int, notification_type: str) -> bool:
        """알림 수신 여부 확인 (Phase 30: Repository 사용)"""
        pref = self.pref_repo.find_by_user_id(user_id)

        if not pref:
            return True  # 설정 없으면 기본적으로 수신

        # 알림 유형별 수신 설정 확인
        type_mapping = {
            Notification.TYPE_CONTRACT_REQUEST: pref.receive_contract_notifications,
            Notification.TYPE_CONTRACT_APPROVED: pref.receive_contract_notifications,
            Notification.TYPE_CONTRACT_REJECTED: pref.receive_contract_notifications,
            Notification.TYPE_CONTRACT_TERMINATED: pref.receive_contract_notifications,
            Notification.TYPE_SYNC_COMPLETED: pref.receive_sync_notifications,
            Notification.TYPE_SYNC_FAILED: pref.receive_sync_notifications,
            Notification.TYPE_TERMINATION_PROCESSED: pref.receive_termination_notifications,
            Notification.TYPE_SYSTEM: pref.receive_system_notifications,
        }

        return type_mapping.get(notification_type, True)

    # ===== 계약 관련 알림 =====

    def notify_contract_request(
        self,
        company_user_id: int,
        personal_user_id: int,
        contract_id: int,
        personal_name: str
    ) -> Optional[Notification]:
        """계약 요청 알림 (법인 관리자에게)"""
        return self.create_notification(
            user_id=company_user_id,
            notification_type=Notification.TYPE_CONTRACT_REQUEST,
            title='새로운 계약 요청',
            message=f'{personal_name}님이 계약을 요청했습니다.',
            resource_type='contract',
            resource_id=contract_id,
            sender_id=personal_user_id,
            priority=Notification.PRIORITY_HIGH,
            action_url=f'/contracts/{contract_id}',
            action_label='요청 확인'
        )

    def notify_contract_approved(
        self,
        personal_user_id: int,
        company_user_id: int,
        contract_id: int,
        company_name: str
    ) -> Optional[Notification]:
        """계약 승인 알림 (개인에게)"""
        return self.create_notification(
            user_id=personal_user_id,
            notification_type=Notification.TYPE_CONTRACT_APPROVED,
            title='계약이 승인되었습니다',
            message=f'{company_name}과의 계약이 승인되었습니다.',
            resource_type='contract',
            resource_id=contract_id,
            sender_id=company_user_id,
            priority=Notification.PRIORITY_NORMAL,
            action_url=f'/personal/contracts/{contract_id}',
            action_label='계약 확인'
        )

    def notify_contract_rejected(
        self,
        personal_user_id: int,
        company_user_id: int,
        contract_id: int,
        company_name: str,
        reason: str = None
    ) -> Optional[Notification]:
        """계약 거절 알림 (개인에게)"""
        message = f'{company_name}에서 계약을 거절했습니다.'
        if reason:
            message += f' 사유: {reason}'

        return self.create_notification(
            user_id=personal_user_id,
            notification_type=Notification.TYPE_CONTRACT_REJECTED,
            title='계약이 거절되었습니다',
            message=message,
            resource_type='contract',
            resource_id=contract_id,
            sender_id=company_user_id,
            priority=Notification.PRIORITY_NORMAL
        )

    def notify_contract_terminated(
        self,
        user_id: int,
        contract_id: int,
        other_party_name: str,
        is_personal: bool = True
    ) -> Optional[Notification]:
        """계약 종료 알림"""
        if is_personal:
            message = f'{other_party_name}과의 계약이 종료되었습니다.'
        else:
            message = f'{other_party_name}님과의 계약이 종료되었습니다.'

        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_CONTRACT_TERMINATED,
            title='계약이 종료되었습니다',
            message=message,
            resource_type='contract',
            resource_id=contract_id,
            priority=Notification.PRIORITY_NORMAL
        )

    # ===== 동기화 관련 알림 =====

    def notify_sync_completed(
        self,
        user_id: int,
        sync_type: str,
        fields_count: int,
        contract_id: int = None
    ) -> Optional[Notification]:
        """동기화 완료 알림"""
        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_SYNC_COMPLETED,
            title='데이터 동기화 완료',
            message=f'{fields_count}개 필드가 동기화되었습니다. ({sync_type})',
            resource_type='sync',
            resource_id=contract_id,
            priority=Notification.PRIORITY_LOW
        )

    def notify_sync_failed(
        self,
        user_id: int,
        error_message: str,
        contract_id: int = None
    ) -> Optional[Notification]:
        """동기화 실패 알림"""
        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_SYNC_FAILED,
            title='데이터 동기화 실패',
            message=f'동기화 중 오류가 발생했습니다: {error_message}',
            resource_type='sync',
            resource_id=contract_id,
            priority=Notification.PRIORITY_HIGH
        )

    # ===== 퇴사 관련 알림 =====

    def notify_termination_processed(
        self,
        user_id: int,
        employee_name: str,
        termination_date: str
    ) -> Optional[Notification]:
        """퇴사 처리 완료 알림"""
        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_TERMINATION_PROCESSED,
            title='퇴사 처리 완료',
            message=f'{employee_name}님의 퇴사 처리가 완료되었습니다. (퇴사일: {termination_date})',
            resource_type='termination',
            priority=Notification.PRIORITY_NORMAL
        )

    # ===== 데이터 업데이트 알림 =====

    def notify_data_updated(
        self,
        user_id: int,
        updater_name: str,
        fields_updated: List[str],
        contract_id: int = None
    ) -> Optional[Notification]:
        """데이터 업데이트 알림 (법인에게)"""
        fields_str = ', '.join(fields_updated[:3])
        if len(fields_updated) > 3:
            fields_str += f' 외 {len(fields_updated) - 3}개'

        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_DATA_UPDATED,
            title='직원 정보 업데이트',
            message=f'{updater_name}님이 정보를 업데이트했습니다. ({fields_str})',
            resource_type='contract',
            resource_id=contract_id,
            priority=Notification.PRIORITY_LOW
        )

    # ===== 시스템 알림 =====

    def notify_system(
        self,
        user_id: int,
        title: str,
        message: str,
        priority: str = None
    ) -> Optional[Notification]:
        """시스템 알림"""
        return self.create_notification(
            user_id=user_id,
            notification_type=Notification.TYPE_SYSTEM,
            title=title,
            message=message,
            priority=priority or Notification.PRIORITY_NORMAL
        )

    def broadcast_system_notification(
        self,
        user_ids: List[int],
        title: str,
        message: str,
        priority: str = None
    ) -> List[Notification]:
        """시스템 알림 일괄 발송"""
        notifications = []
        for user_id in user_ids:
            notification = self.notify_system(user_id, title, message, priority)
            if notification:
                notifications.append(notification)
        return notifications

    # ===== 알림 조회 =====

    def get_notifications(
        self,
        user_id: int,
        unread_only: bool = False,
        notification_type: str = None,
        limit: int = 50,
        offset: int = 0
    ) -> List[Dict]:
        """알림 목록 조회 (Phase 30: Repository 사용)"""
        notifications = self.notification_repo.find_paginated(
            user_id=user_id,
            unread_only=unread_only,
            notification_type=notification_type,
            limit=limit,
            offset=offset
        )
        return [n.to_dict() for n in notifications]

    def get_unread_count(self, user_id: int) -> int:
        """읽지 않은 알림 개수 (Phase 30: Repository 사용)"""
        return self.notification_repo.count_unread_valid(user_id)

    def get_notification(self, notification_id: int, user_id: int = None) -> Optional[Dict]:
        """알림 상세 조회 (Phase 30: Repository 사용)"""
        notification = self.notification_repo.find_one_by_id_and_user(
            notification_id, user_id
        )
        return notification.to_dict() if notification else None

    # ===== 알림 상태 관리 =====

    def mark_as_read(self, notification_id: int, user_id: int) -> bool:
        """알림 읽음 처리 (Phase 30: Repository 사용)"""
        notification = self.notification_repo.find_one_by_id_and_user(
            notification_id, user_id
        )

        if not notification:
            return False

        self.notification_repo.mark_as_read(notification_id)
        return True

    def mark_all_as_read(self, user_id: int, notification_type: str = None) -> int:
        """모든 알림 읽음 처리 (Phase 30: Repository 사용)"""
        return self.notification_repo.mark_all_as_read_with_type(
            user_id, notification_type
        )

    def delete_notification(self, notification_id: int, user_id: int) -> bool:
        """알림 삭제 (Phase 30: Repository 사용)"""
        return self.notification_repo.delete_one(notification_id, user_id)

    def delete_old_notifications(self, days: int = 30) -> int:
        """오래된 알림 삭제 (Phase 30: Repository 사용)"""
        return self.notification_repo.delete_old_notifications(days)

    # ===== 알림 통계 =====

    def get_notification_stats(self, user_id: int, days: int = 30) -> Dict:
        """알림 통계 조회 (Phase 30: Repository 사용)"""
        start_date = datetime.utcnow() - timedelta(days=days)

        # 전체 알림 수
        total = self.notification_repo.count_by_period(user_id, start_date)

        # 읽지 않은 알림 수
        unread = self.notification_repo.count_unread_all(user_id)

        # 유형별 통계
        type_stats = self.notification_repo.get_type_stats(user_id, start_date)

        return {
            'total': total,
            'unread': unread,
            'by_type': {t: c for t, c in type_stats},
            'period_days': days
        }

    # ===== 알림 설정 =====

    def get_preferences(self, user_id: int) -> Dict:
        """알림 설정 조회 (Phase 30: Repository 사용)"""
        pref = self.pref_repo.find_by_user_id(user_id)

        if not pref:
            # 기본 설정 반환
            return {
                'receive_contract_notifications': True,
                'receive_sync_notifications': True,
                'receive_termination_notifications': True,
                'receive_system_notifications': True,
                'email_notifications_enabled': False,
                'email_digest_frequency': 'none'
            }

        return pref.to_dict()

    def update_preferences(self, user_id: int, settings: Dict) -> Dict:
        """알림 설정 업데이트 (Phase 30: Repository 사용)"""
        # 설정 업데이트
        allowed_fields = [
            'receive_contract_notifications',
            'receive_sync_notifications',
            'receive_termination_notifications',
            'receive_system_notifications',
            'email_notifications_enabled',
            'email_digest_frequency'
        ]

        # 허용된 필드만 필터링
        filtered_settings = {k: v for k, v in settings.items() if k in allowed_fields}
        pref = self.pref_repo.update_preferences(user_id, filtered_settings)
        return pref.to_dict()


# 싱글톤 인스턴스
notification_service = NotificationService()
