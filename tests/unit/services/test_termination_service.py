"""
TerminationService 단위 테스트

퇴사 처리 서비스의 핵심 비즈니스 로직 테스트:
- 계약 종료 처리
- 권한 해제
- 데이터 아카이브
"""
import pytest
from unittest.mock import Mock, patch

from app.services.termination_service import TerminationService, termination_service


class TestTerminationServiceInit:
    """TerminationService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert termination_service is not None
        assert isinstance(termination_service, TerminationService)

    def test_set_current_user(self):
        """현재 사용자 설정"""
        termination_service.set_current_user(1)
        assert termination_service._current_user_id == 1


class TestTerminationServiceTerminateContract:
    """계약 종료 처리 테스트"""

    def test_terminate_contract_success(self, session):
        """계약 종료 성공"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.status = 'approved'
        mock_contract.terminate = Mock()

        with patch('app.services.termination_service.PersonCorporateContract') as mock_pcc:
            mock_pcc.query.get.return_value = mock_contract

            with patch.object(termination_service, '_revoke_permissions') as mock_revoke, \
                 patch.object(termination_service, '_disable_sharing_settings') as mock_disable, \
                 patch.object(termination_service, '_mark_for_archive') as mock_archive, \
                 patch('app.services.termination_service.SyncLog') as mock_log, \
                 patch('app.services.termination_service.db') as mock_db:
                mock_revoke.return_value = {'success': True}
                mock_archive.return_value = {'success': True}

                result = termination_service.terminate_contract(
                    contract_id=1,
                    reason='테스트',
                    terminate_by_user_id=1
                )

                assert result['success'] is True
                mock_contract.terminate.assert_called_once()

    def test_terminate_contract_not_found(self):
        """계약을 찾을 수 없을 때"""
        with patch('app.services.termination_service.PersonCorporateContract') as mock_pcc:
            mock_pcc.query.get.return_value = None

            result = termination_service.terminate_contract(
                contract_id=999,
                reason='테스트'
            )

            assert result['success'] is False
            assert '찾을 수 없습니다' in result['error']

    def test_terminate_contract_already_terminated(self, session):
        """이미 종료된 계약일 때"""
        mock_contract = Mock()
        mock_contract.status = 'terminated'

        with patch('app.services.termination_service.PersonCorporateContract') as mock_pcc:
            mock_pcc.query.get.return_value = mock_contract
            mock_pcc.STATUS_TERMINATED = 'terminated'

            result = termination_service.terminate_contract(
                contract_id=1,
                reason='테스트'
            )

            assert result['success'] is False
            assert '이미 종료된' in result['error']


class TestTerminationServiceArchive:
    """데이터 아카이브 테스트"""

    def test_mark_for_archive_success(self, session):
        """아카이브 마킹 성공"""
        mock_contract = Mock()
        mock_contract.id = 1

        result = termination_service._mark_for_archive(mock_contract)

        assert 'contract_id' in result
        assert 'status' in result
        assert result['status'] == termination_service.ARCHIVE_STATUS_PENDING


class TestTerminationServicePermissions:
    """권한 해제 테스트"""

    def test_revoke_permissions_success(self):
        """권한 해제 성공"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.employee_number = 'EMP001'
        mock_contract.person_user_id = 1

        with patch('app.services.termination_service.DataSharingSettings') as mock_settings, \
             patch('app.services.termination_service.Employee') as mock_emp, \
             patch('app.services.termination_service.User') as mock_user:
            
            mock_settings_obj = Mock()
            mock_settings.query.filter_by.return_value.first.return_value = mock_settings_obj
            
            mock_employee = Mock()
            mock_emp.query.filter_by.return_value.first.return_value = mock_employee
            
            mock_user_obj = Mock()
            mock_user.query.get.return_value = mock_user_obj
            
            result = termination_service._revoke_permissions(mock_contract)
            
            assert 'employee_access' in result
            assert 'data_sync' in result
            assert 'api_access' in result

    def test_disable_sharing_settings_success(self):
        """데이터 공유 설정 비활성화"""
        mock_settings = Mock()
        mock_settings.share_basic_info = True
        mock_settings.share_contact = True
        
        with patch('app.services.termination_service.DataSharingSettings') as mock_ds:
            mock_ds.query.filter_by.return_value.first.return_value = mock_settings
            
            termination_service._disable_sharing_settings(contract_id=1)
            
            assert mock_settings.share_basic_info is False
            assert mock_settings.share_contact is False
            assert mock_settings.is_realtime_sync is False




class TestTerminationServiceRetention:
    """데이터 보관 정책 테스트"""

    def test_data_retention_period(self):
        """데이터 보관 기간 확인"""
        assert termination_service.DATA_RETENTION_DAYS == 365 * 3

    def test_archive_status_constants(self):
        """아카이브 상태 상수 확인"""
        assert termination_service.ARCHIVE_STATUS_PENDING == 'pending'
        assert termination_service.ARCHIVE_STATUS_ARCHIVED == 'archived'
        assert termination_service.ARCHIVE_STATUS_DELETED == 'deleted'