"""
SyncRelationService 단위 테스트

관계형 데이터 동기화 서비스의 핵심 비즈니스 로직 테스트:
- 학력, 경력, 자격증 등 관계형 데이터 동기화
"""
import pytest
from unittest.mock import Mock, patch

from app.services.sync.sync_relation_service import SyncRelationService


class TestSyncRelationServiceInit:
    """SyncRelationService 초기화 테스트"""

    def test_init_without_user(self):
        """사용자 없이 초기화"""
        service = SyncRelationService()
        assert service._current_user_id is None

    def test_init_with_user(self):
        """사용자와 함께 초기화"""
        service = SyncRelationService(current_user_id=1)
        assert service._current_user_id == 1

    def test_set_current_user(self):
        """현재 사용자 설정"""
        service = SyncRelationService()
        service.set_current_user(2)
        assert service._current_user_id == 2


class TestSyncRelationServiceSyncRelations:
    """관계 데이터 동기화 테스트"""

    def test_sync_relations_with_education(self, session):
        """학력 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_edu = Mock()
        mock_profile.educations.all.return_value = [mock_edu]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.educations = Mock()
        mock_employee.educations.delete = Mock()

        syncable = {'education': True}

        with patch('app.models.education.Education') as mock_edu_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'education' in result['synced_relations']
            assert len(result['changes']) > 0

    def test_sync_relations_with_career(self, session):
        """경력 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_career = Mock()
        mock_profile.careers.all.return_value = [mock_career]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.careers = Mock()
        mock_employee.careers.delete = Mock()

        syncable = {'career': True}

        with patch('app.models.career.Career') as mock_career_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'career' in result['synced_relations']

    def test_sync_relations_no_data(self, session):
        """동기화할 데이터가 없을 때"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_profile.educations.all.return_value = []

        mock_employee = Mock()
        mock_employee.id = 1

        syncable = {'education': True}

        result = service.sync_relations(
            contract_id=1,
            profile=mock_profile,
            employee=mock_employee,
            syncable=syncable,
            sync_type='manual'
        )

        assert len(result['synced_relations']) == 0

    def test_sync_relations_with_certificates(self, session):
        """자격증 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_cert = Mock()
        mock_profile.certificates.all.return_value = [mock_cert]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.certificates = Mock()
        mock_employee.certificates.delete = Mock()

        syncable = {'certificates': True}

        with patch('app.models.certificate.Certificate') as mock_cert_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'certificates' in result['synced_relations']

    def test_sync_relations_with_languages(self, session):
        """어학 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_lang = Mock()
        mock_profile.languages.all.return_value = [mock_lang]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.languages = Mock()
        mock_employee.languages.delete = Mock()

        syncable = {'languages': True}

        with patch('app.models.language.Language') as mock_lang_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'languages' in result['synced_relations']

    def test_sync_relations_with_military(self, session):
        """병역 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_military = Mock()
        mock_profile.military_service = mock_military

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.military_service = None

        syncable = {'military': True}

        with patch('app.models.military_service.MilitaryService') as mock_mil_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'military' in result['synced_relations']

    def test_sync_relations_with_family(self, session):
        """가족 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_family = Mock()
        mock_profile.family_members.all.return_value = [mock_family]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.family_members = Mock()
        mock_employee.family_members.delete = Mock()

        syncable = {'family': True}

        with patch('app.models.family_member.FamilyMember') as mock_family_model, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert 'family' in result['synced_relations']

    def test_sync_relations_multiple_types(self, session):
        """여러 유형 동시 동기화"""
        service = SyncRelationService(current_user_id=1)

        mock_profile = Mock()
        mock_profile.educations.all.return_value = [Mock()]
        mock_profile.careers.all.return_value = [Mock()]
        mock_profile.certificates.all.return_value = [Mock()]

        mock_employee = Mock()
        mock_employee.id = 1
        mock_employee.educations = Mock()
        mock_employee.educations.delete = Mock()
        mock_employee.careers = Mock()
        mock_employee.careers.delete = Mock()
        mock_employee.certificates = Mock()
        mock_employee.certificates.delete = Mock()

        syncable = {
            'education': True,
            'career': True,
            'certificates': True
        }

        with patch('app.models.education.Education') as mock_edu, \
             patch('app.models.career.Career') as mock_car, \
             patch('app.models.certificate.Certificate') as mock_cert, \
             patch('app.services.sync.sync_relation_service.SyncLog') as mock_log, \
             patch('app.services.sync.sync_relation_service.db') as mock_db, \
             patch('app.services.sync.sync_relation_service.json') as mock_json:
            mock_log_instance = Mock()
            mock_log_instance.id = 1
            mock_log.create_log.return_value = mock_log_instance
            mock_json.dumps.return_value = '{"count": 1}'

            result = service.sync_relations(
                contract_id=1,
                profile=mock_profile,
                employee=mock_employee,
                syncable=syncable,
                sync_type='manual'
            )

            assert len(result['synced_relations']) == 3
            assert 'education' in result['synced_relations']
            assert 'career' in result['synced_relations']
            assert 'certificates' in result['synced_relations']

