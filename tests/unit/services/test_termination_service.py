"""
TerminationService 단위 테스트

퇴사 처리 서비스의 핵심 비즈니스 로직 테스트:
- 계약 종료 처리
- 권한 해제
- 데이터 아카이브
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.sync.services.termination_service import TerminationService, termination_service
from app.shared.constants.status import ContractStatus


@pytest.fixture
def mock_repos(app):
    """TerminationService의 Repository를 Mock으로 대체하는 fixture"""
    mock_contract_repo = Mock()
    mock_sync_log_repo = Mock()
    mock_data_sharing_repo = Mock()

    with patch('app.domains.contract.get_person_contract_repo', return_value=mock_contract_repo), \
         patch('app.domains.sync.get_sync_log_repo', return_value=mock_sync_log_repo), \
         patch('app.domains.company.get_data_sharing_settings_repo', return_value=mock_data_sharing_repo):
        yield termination_service, mock_contract_repo, mock_sync_log_repo, mock_data_sharing_repo


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

    def test_terminate_contract_success(self, mock_repos):
        """계약 종료 성공"""
        service, mock_contract_repo, mock_sync_log_repo, _ = mock_repos

        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.status = ContractStatus.APPROVED
        mock_contract.terminate = Mock()
        mock_contract.terminated_at = Mock()
        mock_contract.terminated_at.isoformat = Mock(return_value='2026-01-07T00:00:00')
        mock_contract_repo.find_by_id.return_value = mock_contract

        with patch.object(service, '_revoke_permissions') as mock_revoke, \
             patch.object(service, '_disable_sharing_settings') as mock_disable, \
             patch.object(service, '_mark_for_archive') as mock_archive:
            mock_revoke.return_value = {'success': True}
            mock_archive.return_value = {'success': True}

            result = service.terminate_contract(
                contract_id=1,
                reason='테스트',
                terminate_by_user_id=1
            )

            assert result['success'] is True
            mock_contract.terminate.assert_called_once()

    def test_terminate_contract_not_found(self, mock_repos):
        """계약을 찾을 수 없을 때"""
        service, mock_contract_repo, _, _ = mock_repos

        mock_contract_repo.find_by_id.return_value = None

        result = service.terminate_contract(
            contract_id=999,
            reason='테스트'
        )

        assert result['success'] is False
        assert '찾을 수 없습니다' in result['error']

    def test_terminate_contract_already_terminated(self, mock_repos):
        """이미 종료된 계약일 때"""
        service, mock_contract_repo, _, _ = mock_repos

        mock_contract = Mock()
        mock_contract.status = ContractStatus.TERMINATED
        mock_contract_repo.find_by_id.return_value = mock_contract

        result = service.terminate_contract(
            contract_id=1,
            reason='테스트'
        )

        assert result['success'] is False
        assert '이미 종료된' in result['error']


class TestTerminationServiceArchive:
    """데이터 아카이브 테스트"""

    def test_mark_for_archive_success(self, app):
        """아카이브 마킹 성공"""
        mock_contract = Mock()
        mock_contract.id = 1

        result = termination_service._mark_for_archive(mock_contract)

        assert 'contract_id' in result
        assert 'status' in result
        assert result['status'] == termination_service.ARCHIVE_STATUS_PENDING


class TestTerminationServicePermissions:
    """권한 해제 테스트"""

    def test_revoke_permissions_success(self, app):
        """권한 해제 성공"""
        mock_contract = Mock()
        mock_contract.id = 1
        mock_contract.employee_number = 'EMP001'
        mock_contract.person_user_id = 1

        mock_data_sharing_repo = Mock()
        mock_settings = Mock()
        mock_data_sharing_repo.find_by_contract_id.return_value = mock_settings

        mock_emp_repo = Mock()
        mock_employee = Mock()
        mock_emp_repo.find_by_employee_number.return_value = mock_employee

        mock_user_repo = Mock()
        mock_user_obj = Mock()
        mock_user_repo.find_by_id.return_value = mock_user_obj

        with patch('app.domains.company.get_data_sharing_settings_repo', return_value=mock_data_sharing_repo), \
             patch('app.domains.employee.get_employee_repo', return_value=mock_emp_repo), \
             patch('app.domains.user.get_user_repo', return_value=mock_user_repo):
            result = termination_service._revoke_permissions(mock_contract)

        assert 'employee_access' in result
        assert 'data_sync' in result
        assert 'api_access' in result

    def test_disable_sharing_settings_success(self, app):
        """데이터 공유 설정 비활성화"""
        mock_data_sharing_repo = Mock()
        mock_settings = Mock()
        mock_settings.share_basic_info = True
        mock_settings.share_contact = True
        mock_data_sharing_repo.find_by_contract_id.return_value = mock_settings

        with patch('app.domains.company.get_data_sharing_settings_repo', return_value=mock_data_sharing_repo):
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
