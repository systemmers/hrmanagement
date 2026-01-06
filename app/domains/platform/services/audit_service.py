"""
감사 로그 서비스

정보 접근 및 변경 사항을 기록하고 관리합니다.

Phase 4: 데이터 동기화 및 퇴사 처리
Phase 6: 백엔드 리팩토링 - AuditLog 모델 분리
Phase 7: 도메인 중심 마이그레이션 완료
Phase 8: 상수 모듈 적용
Phase 31: 컨벤션 준수 - Repository 패턴 적용
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from functools import wraps
import json

from flask import request, session, g, current_app
from app.shared.constants.session_keys import SessionKeys
from app.models.audit_log import AuditLog


class AuditService:
    """
    감사 로그 서비스

    주요 기능:
    - 정보 접근 로깅
    - 데이터 변경 추적
    - 감사 로그 조회 및 검색
    - 통계 및 리포트
    """

    # 로깅 대상 리소스 타입
    TRACKED_RESOURCES = [
        'employee', 'contract', 'personal_profile',
        'sync', 'termination',
        'user', 'company', 'organization'
    ]

    # 민감 정보 필드 (상세 로깅에서 마스킹)
    SENSITIVE_FIELDS = [
        'password', 'password_hash', 'resident_number',
        'token', 'secret', 'api_key'
    ]

    def __init__(self):
        self._enabled = True
        self._repo = None

    @property
    def repo(self):
        """지연 초기화된 AuditLog Repository"""
        if self._repo is None:
            from app.domains.platform import get_audit_log_repo
            self._repo = get_audit_log_repo()
        return self._repo

    def enable(self):
        """감사 로깅 활성화"""
        self._enabled = True

    def disable(self):
        """감사 로깅 비활성화"""
        self._enabled = False

    def is_enabled(self) -> bool:
        """활성화 상태 확인"""
        return self._enabled

    # ===== 로그 생성 =====

    def log(
        self,
        action: str,
        resource_type: str,
        resource_id: int = None,
        details: Dict = None,
        status: str = AuditLog.STATUS_SUCCESS,
        error_message: str = None
    ) -> Optional[AuditLog]:
        """
        감사 로그 기록

        Args:
            action: 액션 유형 (view, create, update, delete, export)
            resource_type: 리소스 유형 (employee, contract, etc.)
            resource_id: 리소스 ID (선택)
            details: 추가 상세 정보 (선택)
            status: 결과 상태
            error_message: 에러 메시지 (실패 시)

        Returns:
            생성된 AuditLog 또는 None
        """
        if not self._enabled:
            return None

        try:
            # 세션에서 사용자 정보 가져오기
            user_id = session.get(SessionKeys.USER_ID)
            account_type = session.get(SessionKeys.ACCOUNT_TYPE)
            company_id = session.get(SessionKeys.COMPANY_ID)

            # 요청 정보
            ip_address = self._get_client_ip()
            user_agent = request.user_agent.string if request else None
            endpoint = request.endpoint if request else None
            method = request.method if request else None

            # 민감 정보 마스킹
            if details:
                details = self._mask_sensitive_data(details)

            # Phase 31: Repository 패턴 적용
            log = self.repo.create_log(
                action=action,
                resource_type=resource_type,
                resource_id=resource_id,
                user_id=user_id,
                account_type=account_type,
                company_id=company_id,
                details=json.dumps(details) if details else None,
                ip_address=ip_address,
                user_agent=user_agent,
                endpoint=endpoint,
                method=method,
                status=status,
                error_message=error_message,
            )

            return log

        except Exception as e:
            if current_app:
                current_app.logger.error(f"Audit log error: {str(e)}")
            return None

    def log_view(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """조회 로그"""
        return self.log(AuditLog.ACTION_VIEW, resource_type, resource_id, details)

    def log_create(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """생성 로그"""
        return self.log(AuditLog.ACTION_CREATE, resource_type, resource_id, details)

    def log_update(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """수정 로그"""
        return self.log(AuditLog.ACTION_UPDATE, resource_type, resource_id, details)

    def log_delete(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """삭제 로그"""
        return self.log(AuditLog.ACTION_DELETE, resource_type, resource_id, details)

    def log_export(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """내보내기 로그"""
        return self.log(AuditLog.ACTION_EXPORT, resource_type, resource_id, details)

    def log_sync(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """동기화 로그"""
        return self.log(AuditLog.ACTION_SYNC, resource_type, resource_id, details)

    def log_access_denied(self, resource_type: str, resource_id: int = None, details: Dict = None):
        """접근 거부 로그"""
        return self.log(
            AuditLog.ACTION_ACCESS_DENIED,
            resource_type,
            resource_id,
            details,
            status=AuditLog.STATUS_DENIED
        )

    def log_failure(
        self,
        action: str,
        resource_type: str,
        error_message: str,
        resource_id: int = None,
        details: Dict = None
    ):
        """실패 로그"""
        return self.log(
            action,
            resource_type,
            resource_id,
            details,
            status=AuditLog.STATUS_FAILURE,
            error_message=error_message
        )

    # ===== 조회 =====

    def get_logs(
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
    ) -> List[Dict]:
        """
        감사 로그 조회

        Args:
            다양한 필터 조건

        Returns:
            로그 목록
        """
        # Phase 31: Repository 패턴 적용
        logs = self.repo.find_logs(
            user_id=user_id,
            company_id=company_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            status=status,
            start_date=start_date,
            end_date=end_date,
            limit=limit,
            offset=offset
        )

        return [log.to_dict() for log in logs]

    def get_logs_for_resource(
        self,
        resource_type: str,
        resource_id: int,
        limit: int = 50
    ) -> List[Dict]:
        """특정 리소스의 로그 조회"""
        return self.get_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit
        )

    def get_user_activity(self, user_id: int, days: int = 30) -> List[Dict]:
        """사용자 활동 이력 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_logs(user_id=user_id, start_date=start_date)

    def count_logs(
        self,
        user_id: int = None,
        company_id: int = None,
        action: str = None,
        resource_type: str = None
    ) -> int:
        """
        감사 로그 개수 조회 (페이지네이션용)

        Args:
            user_id: 사용자 ID 필터
            company_id: 법인 ID 필터
            action: 액션 유형 필터
            resource_type: 리소스 유형 필터

        Returns:
            로그 개수
        """
        # Phase 31: Repository 패턴 적용
        return self.repo.count_logs(
            user_id=user_id,
            company_id=company_id,
            action=action,
            resource_type=resource_type
        )

    def get_company_audit_trail(self, company_id: int, days: int = 30) -> List[Dict]:
        """법인 감사 추적 조회"""
        start_date = datetime.utcnow() - timedelta(days=days)
        return self.get_logs(company_id=company_id, start_date=start_date)

    # ===== 통계 =====

    def get_statistics(
        self,
        company_id: int = None,
        start_date: datetime = None,
        end_date: datetime = None
    ) -> Dict:
        """
        감사 로그 통계

        Returns:
            {
                'total': int,
                'by_action': {...},
                'by_resource': {...},
                'by_status': {...},
                'by_date': {...}
            }
        """
        # Phase 31: Repository 패턴 적용
        logs = self.repo.find_logs(
            company_id=company_id,
            start_date=start_date,
            end_date=end_date,
            limit=10000  # 통계용 대량 조회
        )

        stats = {
            'total': len(logs),
            'by_action': {},
            'by_resource': {},
            'by_status': {},
        }

        for log in logs:
            # 액션별
            stats['by_action'][log.action] = stats['by_action'].get(log.action, 0) + 1

            # 리소스별
            stats['by_resource'][log.resource_type] = stats['by_resource'].get(log.resource_type, 0) + 1

            # 상태별
            stats['by_status'][log.status] = stats['by_status'].get(log.status, 0) + 1

        return stats

    def get_access_summary(
        self,
        resource_type: str,
        resource_id: int,
        days: int = 30
    ) -> Dict:
        """
        리소스 접근 요약

        Returns:
            {
                'total_views': int,
                'unique_users': int,
                'last_access': datetime,
                'access_by_user': {...}
            }
        """
        start_date = datetime.utcnow() - timedelta(days=days)

        # Phase 31: Repository 패턴 적용
        logs = self.repo.find_for_resource(
            resource_type=resource_type,
            resource_id=resource_id,
            action=AuditLog.ACTION_VIEW,
            start_date=start_date,
            limit=1000
        )

        users = {}
        for log in logs:
            if log.user_id:
                users[log.user_id] = users.get(log.user_id, 0) + 1

        return {
            'total_views': len(logs),
            'unique_users': len(users),
            'last_access': max([l.created_at for l in logs]).isoformat() if logs else None,
            'access_by_user': users,
        }

    # ===== Private 헬퍼 =====

    def _get_client_ip(self) -> Optional[str]:
        """클라이언트 IP 주소 가져오기"""
        if not request:
            return None

        # 프록시 뒤에 있는 경우
        if request.headers.get('X-Forwarded-For'):
            return request.headers.get('X-Forwarded-For').split(',')[0].strip()

        if request.headers.get('X-Real-IP'):
            return request.headers.get('X-Real-IP')

        return request.remote_addr

    def _mask_sensitive_data(self, data: Dict) -> Dict:
        """민감 정보 마스킹"""
        if not isinstance(data, dict):
            return data

        masked = data.copy()
        for key in self.SENSITIVE_FIELDS:
            if key in masked:
                masked[key] = '[MASKED]'

        return masked


# 싱글톤 인스턴스
audit_service = AuditService()


# ===== 데코레이터 =====

def audit_log(action: str, resource_type: str):
    """
    감사 로그 데코레이터

    사용법:
    @audit_log('view', 'employee')
    def get_employee(employee_id):
        ...
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            # 리소스 ID 추출 시도
            resource_id = kwargs.get('id') or kwargs.get('employee_id') or kwargs.get('contract_id')

            try:
                result = f(*args, **kwargs)

                # 성공 로그
                audit_service.log(
                    action=action,
                    resource_type=resource_type,
                    resource_id=resource_id,
                    status=AuditLog.STATUS_SUCCESS
                )

                return result

            except Exception as e:
                # 실패 로그
                audit_service.log_failure(
                    action=action,
                    resource_type=resource_type,
                    error_message=str(e),
                    resource_id=resource_id
                )
                raise

        return decorated_function
    return decorator
