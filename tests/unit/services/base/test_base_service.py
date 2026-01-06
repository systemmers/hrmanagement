"""
Base Service Classes 테스트

Base 서비스 클래스들 테스트
"""
import pytest
from unittest.mock import Mock, patch

from app.services.base.history_service import BaseHistoryService
from app.services.base.relation_updater import RelationDataUpdater


class TestBaseHistoryService:
    """BaseHistoryService 테스트"""

    def test_history_service_init(self):
        """히스토리 서비스 초기화"""
        service = BaseHistoryService()
        assert service is not None


class TestRelationDataUpdater:
    """RelationDataUpdater 테스트"""

    def test_relation_updater_init(self):
        """관계 데이터 업데이터 초기화"""
        updater = RelationDataUpdater()
        assert updater is not None

    def test_update_relation_data(self):
        """관계 데이터 업데이트"""
        from app.services.base.relation_updater import RelationDataConfig
        updater = RelationDataUpdater()

        mock_repo = Mock()
        mock_repo.delete_by_employee_id = Mock()
        mock_repo.create = Mock()
        mock_model = Mock()

        config = RelationDataConfig(
            model_class=mock_model,
            repository=mock_repo,
            form_prefix='test_',
            required_field='name',
            field_mapping={'name': 'name'},
            owner_field='employee_id'
        )

        form_data = {'test_name[]': ['김철수']}
        result = updater.update(owner_id=1, form_data=form_data, config=config)

        assert result == 1
        mock_repo.delete_by_employee_id.assert_called_once_with(1)

