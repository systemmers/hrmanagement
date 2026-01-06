"""
ProfileRelationService 단위 테스트

프로필 관계형 데이터 서비스의 핵심 비즈니스 로직 테스트:
- 관계형 데이터 CRUD (학력, 경력, 자격증 등)
"""
import pytest
from unittest.mock import Mock, patch

from app.domains.employee.services.profile_relation_service import ProfileRelationService, profile_relation_service
from app.types import OwnerType


class TestProfileRelationServiceInit:
    """ProfileRelationService 초기화 테스트"""

    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert profile_relation_service is not None
        assert isinstance(profile_relation_service, ProfileRelationService)


class TestProfileRelationServiceCRUD:
    """관계형 데이터 CRUD 테스트"""

    def test_get_education_list(self, session):
        """학력 목록 조회"""
        with patch.object(profile_relation_service, '_education') as mock_edu:
            mock_edu.get_all.return_value = [{'id': 1, 'school_name': '테스트대학'}]

            result = profile_relation_service.get_educations(
                owner_id=1,
                owner_type='employee'
            )

            assert len(result) == 1
            assert result[0]['school_name'] == '테스트대학'

    def test_create_education(self, session):
        """학력 생성"""
        with patch.object(profile_relation_service, '_education') as mock_edu:
            mock_edu.add.return_value = {'id': 1, 'school_name': '테스트대학'}

            result = profile_relation_service.add_education(
                owner_id=1,
                data={'school_name': '테스트대학'},
                owner_type='employee'
            )

            assert result is not None
            assert result['school_name'] == '테스트대학'

    def test_update_education(self, session):
        """학력 수정 - update 메서드가 없으므로 skip"""
        pass

    def test_delete_education(self, session):
        """학력 삭제"""
        with patch.object(profile_relation_service, '_education') as mock_edu:
            mock_edu.delete.return_value = True

            result = profile_relation_service.delete_education(
                education_id=1,
                owner_id=1,
                owner_type='employee'
            )

            assert result is True

