"""
퇴사 처리 서비스

계약 종료 시 데이터 처리 및 아카이브를 관리합니다.
Phase 4: 데이터 동기화 및 퇴사 처리
"""
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta, date
import json

from app.database import db
from app.models.employee import Employee
from app.models.user import User
from app.models.personal_profile import PersonalProfile
from app.models.person_contract import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog
)


class TerminationService:
    """
    퇴사/계약종료 처리 서비스

    주요 기능:
    - 계약 종료 시 권한 해제
    - 데이터 아카이브 처리
    - 3년 보관 정책 적용
    - 자동 정리 스케줄링
    """

    # 데이터 보관 기간 (일)
    DATA_RETENTION_DAYS = 365 * 3  # 3년

    # 아카이브 상태
    ARCHIVE_STATUS_PENDING = 'pending'
    ARCHIVE_STATUS_ARCHIVED = 'archived'
    ARCHIVE_STATUS_DELETED = 'deleted'

    def __init__(self):
        self._current_user_id = None

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정"""
        self._current_user_id = user_id

    # ===== 계약 종료 처리 =====

    def terminate_contract(
        self,
        contract_id: int,
        reason: str = None,
        terminate_by_user_id: int = None
    ) -> Dict[str, Any]:
        """
        계약 종료 처리

        Args:
            contract_id: 종료할 계약 ID
            reason: 종료 사유
            terminate_by_user_id: 종료 처리자 ID

        Returns:
            처리 결과
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status == PersonCorporateContract.STATUS_TERMINATED:
            return {'success': False, 'error': '이미 종료된 계약입니다.'}

        # 계약 상태 변경
        contract.terminate(terminate_by_user_id or self._current_user_id, reason)

        # 권한 해제
        revoke_result = self._revoke_permissions(contract)

        # 데이터 공유 설정 비활성화
        self._disable_sharing_settings(contract_id)

        # 아카이브 마킹 (3년 후 삭제 예정)
        archive_result = self._mark_for_archive(contract)

        # 종료 로그 기록
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type='termination',
            entity_type='contract',
            field_name='status',
            old_value=PersonCorporateContract.STATUS_APPROVED,
            new_value=PersonCorporateContract.STATUS_TERMINATED,
            direction='system',
            user_id=terminate_by_user_id or self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        return {
            'success': True,
            'contract_id': contract_id,
            'terminated_at': contract.terminated_at.isoformat(),
            'revoked_permissions': revoke_result,
            'archive_scheduled': archive_result,
        }

    def _revoke_permissions(self, contract: PersonCorporateContract) -> Dict[str, Any]:
        """
        계약 종료에 따른 권한 해제

        Args:
            contract: 종료된 계약

        Returns:
            해제된 권한 정보
        """
        revoked = {
            'employee_access': False,
            'data_sync': False,
            'api_access': False,
        }

        # 1. 데이터 동기화 비활성화
        settings = DataSharingSettings.query.filter_by(contract_id=contract.id).first()
        if settings:
            settings.is_realtime_sync = False
            revoked['data_sync'] = True

        # 2. 직원 계정 접근 권한 해제
        # employee_number 또는 User.employee_id로 Employee 조회
        employee = None
        if contract.employee_number:
            employee = Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()

        user = User.query.get(contract.person_user_id)

        if not employee and user:
            if user.employee_id:
                employee = db.session.get(Employee, user.employee_id)
            else:
                # Employee가 없는 경우 (personal 계정) - Employee 생성 후 terminated 설정
                profile = PersonalProfile.query.filter_by(user_id=user.id).first()
                if profile:
                    from app.services.sync_service import sync_service
                    employee = sync_service._find_or_create_employee(contract, profile)
                    if employee:
                        user.employee_id = employee.id

        if employee:
            # 직원 상태를 퇴사로 변경
            employee.status = 'terminated'
            employee.resignation_date = date.today()
            revoked['employee_access'] = True

        # 3. 개인 사용자의 해당 법인 접근 권한 로그
        revoked['api_access'] = True

        return revoked

    def _disable_sharing_settings(self, contract_id: int):
        """데이터 공유 설정 모두 비활성화"""
        settings = DataSharingSettings.query.filter_by(contract_id=contract_id).first()
        if settings:
            settings.share_basic_info = False
            settings.share_contact = False
            settings.share_education = False
            settings.share_career = False
            settings.share_certificates = False
            settings.share_languages = False
            settings.share_military = False
            settings.is_realtime_sync = False

    def _mark_for_archive(self, contract: PersonCorporateContract) -> Dict[str, Any]:
        """
        아카이브 대상으로 마킹

        Args:
            contract: 종료된 계약

        Returns:
            아카이브 예정 정보
        """
        retention_end = datetime.utcnow() + timedelta(days=self.DATA_RETENTION_DAYS)

        return {
            'contract_id': contract.id,
            'retention_end_date': retention_end.isoformat(),
            'status': self.ARCHIVE_STATUS_PENDING,
        }

    # ===== 아카이브 처리 =====

    def get_contracts_to_archive(self) -> List[Dict]:
        """
        아카이브 대상 계약 목록 조회
        (종료 후 3년이 지난 계약)

        Returns:
            아카이브 대상 계약 목록
        """
        cutoff_date = datetime.utcnow() - timedelta(days=self.DATA_RETENTION_DAYS)

        contracts = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == PersonCorporateContract.STATUS_TERMINATED,
            PersonCorporateContract.terminated_at <= cutoff_date
        ).all()

        return [c.to_dict(include_relations=True) for c in contracts]

    def archive_contract_data(self, contract_id: int) -> Dict[str, Any]:
        """
        계약 관련 데이터 아카이브 처리

        개인정보를 익명화하고 통계용 데이터만 보관합니다.

        Args:
            contract_id: 아카이브할 계약 ID

        Returns:
            아카이브 결과
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_TERMINATED:
            return {'success': False, 'error': '종료된 계약만 아카이브할 수 있습니다.'}

        # 직원 데이터 익명화
        if contract.employee_number:
            employee = Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()

            if employee:
                self._anonymize_employee(employee)

        # 동기화 로그 정리 (개인정보 제거)
        self._clean_sync_logs(contract_id)

        # 데이터 공유 설정 삭제
        DataSharingSettings.query.filter_by(contract_id=contract_id).delete()

        # 아카이브 로그
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type='archive',
            entity_type='contract',
            field_name=None,
            old_value=None,
            new_value=None,
            direction='system',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        return {
            'success': True,
            'contract_id': contract_id,
            'archived_at': datetime.utcnow().isoformat(),
        }

    def _anonymize_employee(self, employee: Employee):
        """
        직원 데이터 익명화

        법적 보관 의무가 있는 최소 데이터만 유지하고
        나머지 개인정보는 익명화합니다.
        """
        # 익명화 마킹
        anonymized_prefix = f"[ANONYMIZED-{employee.id}]"

        # 개인 식별 정보 익명화
        employee.name = anonymized_prefix
        employee.email = f"anonymized_{employee.id}@deleted.local"
        employee.phone = None
        employee.mobile_phone = None
        employee.home_phone = None
        employee.address = None
        employee.detailed_address = None
        employee.postal_code = None
        employee.resident_number = None
        employee.photo = None
        employee.english_name = None
        employee.chinese_name = None
        employee.birth_date = None
        employee.gender = None
        employee.nationality = None
        employee.blood_type = None
        employee.religion = None
        employee.hobby = None
        employee.specialty = None
        employee.disability_info = None

        # 상태 업데이트
        employee.status = 'anonymized'

    def _clean_sync_logs(self, contract_id: int):
        """동기화 로그에서 개인정보 제거"""
        logs = SyncLog.query.filter_by(contract_id=contract_id).all()

        for log in logs:
            # old_value, new_value에서 개인정보 마스킹
            if log.old_value:
                log.old_value = self._mask_personal_info(log.old_value)
            if log.new_value:
                log.new_value = self._mask_personal_info(log.new_value)

    def _mask_personal_info(self, value: str) -> str:
        """개인정보 마스킹"""
        if not value:
            return value

        # JSON인 경우 파싱 후 마스킹
        try:
            data = json.loads(value)
            if isinstance(data, dict):
                sensitive_keys = [
                    'name', 'email', 'phone', 'address', 'resident_number',
                    'birth_date', 'photo'
                ]
                for key in sensitive_keys:
                    if key in data:
                        data[key] = '[MASKED]'
                return json.dumps(data)
        except (json.JSONDecodeError, TypeError):
            pass

        # 문자열인 경우 길이 제한
        if len(value) > 50:
            return '[MASKED-DATA]'

        return value

    # ===== 정리 스케줄러 =====

    def run_cleanup_job(self) -> Dict[str, Any]:
        """
        정기 정리 작업 실행

        - 보관 기간이 지난 계약 아카이브 처리
        - 익명화된 데이터 정리

        Returns:
            정리 작업 결과
        """
        results = {
            'archived_contracts': [],
            'errors': [],
            'executed_at': datetime.utcnow().isoformat(),
        }

        # 아카이브 대상 조회
        contracts_to_archive = self.get_contracts_to_archive()

        for contract_data in contracts_to_archive:
            try:
                result = self.archive_contract_data(contract_data['id'])
                if result['success']:
                    results['archived_contracts'].append(contract_data['id'])
                else:
                    results['errors'].append({
                        'contract_id': contract_data['id'],
                        'error': result.get('error')
                    })
            except Exception as e:
                results['errors'].append({
                    'contract_id': contract_data['id'],
                    'error': str(e)
                })

        return results

    # ===== 조회 메서드 =====

    def get_termination_history(
        self,
        company_id: int = None,
        person_user_id: int = None,
        limit: int = 50
    ) -> List[Dict]:
        """
        종료된 계약 이력 조회

        Args:
            company_id: 법인 ID (선택)
            person_user_id: 개인 사용자 ID (선택)
            limit: 조회 제한

        Returns:
            종료 이력 목록
        """
        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == PersonCorporateContract.STATUS_TERMINATED
        )

        if company_id:
            query = query.filter_by(company_id=company_id)
        if person_user_id:
            query = query.filter_by(person_user_id=person_user_id)

        contracts = query.order_by(
            PersonCorporateContract.terminated_at.desc()
        ).limit(limit).all()

        return [c.to_dict(include_relations=True) for c in contracts]

    def get_retention_status(self, contract_id: int) -> Dict[str, Any]:
        """
        계약의 데이터 보관 상태 조회

        Args:
            contract_id: 계약 ID

        Returns:
            보관 상태 정보
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_TERMINATED:
            return {
                'success': True,
                'status': 'active',
                'message': '활성 계약입니다.',
            }

        if not contract.terminated_at:
            return {
                'success': True,
                'status': 'unknown',
                'message': '종료일이 기록되지 않았습니다.',
            }

        retention_end = contract.terminated_at + timedelta(days=self.DATA_RETENTION_DAYS)
        days_remaining = (retention_end - datetime.utcnow()).days

        if days_remaining <= 0:
            status = self.ARCHIVE_STATUS_ARCHIVED
        else:
            status = self.ARCHIVE_STATUS_PENDING

        return {
            'success': True,
            'contract_id': contract_id,
            'status': status,
            'terminated_at': contract.terminated_at.isoformat(),
            'retention_end': retention_end.isoformat(),
            'days_remaining': max(0, days_remaining),
            'retention_days': self.DATA_RETENTION_DAYS,
        }


# 싱글톤 인스턴스
termination_service = TerminationService()
