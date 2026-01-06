"""
CorporateAdminProfileService 단위 테스트

법인 관리자 프로필 서비스의 CRUD 및 어댑터 통합 테스트
"""
import pytest
from unittest.mock import Mock, patch
from app.services.corporate_admin_profile_service import (
    CorporateAdminProfileService,
    corporate_admin_profile_service
)
from app.models import CorporateAdminProfile
from app.models import User
from app.models import Company


class TestCorporateAdminProfileServiceInit:
    """CorporateAdminProfileService 초기화 테스트"""

    @pytest.mark.unit
    def test_singleton_instance_exists(self, app):
        """싱글톤 인스턴스 존재 확인"""
        assert corporate_admin_profile_service is not None
        assert isinstance(corporate_admin_profile_service, CorporateAdminProfileService)

    @pytest.mark.unit
    def test_service_has_repos(self, app):
        """서비스에 repository 속성 존재 확인"""
        assert hasattr(corporate_admin_profile_service, 'profile_repo')
        assert hasattr(corporate_admin_profile_service, 'user_repo')


class TestCorporateAdminProfileServiceQueries:
    """CorporateAdminProfileService 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_corporate):
        """테스트 설정"""
        self.session = session
        self.service = CorporateAdminProfileService()
        self.company_id = test_company.id
        self.user_id = test_user_corporate.id

    @pytest.mark.unit
    def test_get_profile_by_user_id(self):
        """사용자 ID로 프로필 조회"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        result = self.service.get_profile_by_user_id(self.user_id)

        assert result is not None
        assert isinstance(result, CorporateAdminProfile)
        assert result.user_id == self.user_id

    @pytest.mark.unit
    def test_get_profile_by_user_id_not_found(self):
        """존재하지 않는 프로필 조회"""
        result = self.service.get_profile_by_user_id(99999)

        assert result is None

    @pytest.mark.unit
    def test_get_user_with_profile(self):
        """사용자와 프로필 동시 조회"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        user, profile_result = self.service.get_user_with_profile(self.user_id)

        assert user is not None
        assert profile_result is not None
        assert isinstance(user, User)
        assert isinstance(profile_result, CorporateAdminProfile)

    @pytest.mark.unit
    def test_get_user_with_profile_no_user(self):
        """존재하지 않는 사용자 조회"""
        user, profile = self.service.get_user_with_profile(99999)

        assert user is None
        assert profile is None

    @pytest.mark.unit
    def test_get_adapter(self):
        """프로필 어댑터 반환"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        adapter = self.service.get_adapter(self.user_id)

        assert adapter is not None
        from app.adapters.profile_adapter import CorporateAdminProfileAdapter
        assert isinstance(adapter, CorporateAdminProfileAdapter)

    @pytest.mark.unit
    def test_get_adapter_no_profile(self):
        """프로필이 없을 때 어댑터 반환"""
        adapter = self.service.get_adapter(99999)

        assert adapter is None

    @pytest.mark.unit
    def test_get_dashboard_data(self):
        """대시보드용 데이터 조회"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        data = self.service.get_dashboard_data(self.user_id)

        assert data is not None
        assert 'user' in data
        assert 'profile' in data
        assert 'company' in data
        assert 'adapter' in data

    @pytest.mark.unit
    def test_get_dashboard_data_no_profile(self):
        """프로필이 없을 때 대시보드 데이터 조회"""
        data = self.service.get_dashboard_data(99999)

        assert data is None


class TestCorporateAdminProfileServiceCRUD:
    """CorporateAdminProfileService CRUD 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_corporate):
        """테스트 설정"""
        self.session = session
        self.service = CorporateAdminProfileService()
        self.company_id = test_company.id
        self.user_id = test_user_corporate.id

    @pytest.mark.unit
    def test_ensure_profile_exists_new(self):
        """프로필이 없을 때 생성"""
        profile = self.service.ensure_profile_exists(
            user_id=self.user_id,
            company_id=self.company_id,
            default_name='새 관리자'
        )

        assert profile is not None
        assert isinstance(profile, CorporateAdminProfile)
        assert profile.user_id == self.user_id
        assert profile.name == '새 관리자'

    @pytest.mark.unit
    def test_ensure_profile_exists_existing(self):
        """프로필이 이미 있을 때 반환"""
        # 프로필 생성
        existing_profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='기존 관리자'
        )
        self.session.add(existing_profile)
        self.session.commit()

        profile = self.service.ensure_profile_exists(
            user_id=self.user_id,
            company_id=self.company_id,
            default_name='새 관리자'
        )

        assert profile is not None
        assert profile.id == existing_profile.id
        assert profile.name == '기존 관리자'

    @pytest.mark.unit
    def test_create_profile(self):
        """새 프로필 생성"""
        data = {
            'name': '새 관리자',
            'position': '대표이사',
            'email': 'admin@test.com',
            'mobile_phone': '010-1234-5678'
        }

        success, profile, error = self.service.create_profile(
            user_id=self.user_id,
            company_id=self.company_id,
            data=data
        )

        assert success is True
        assert profile is not None
        assert error is None
        assert isinstance(profile, CorporateAdminProfile)

    @pytest.mark.unit
    def test_create_profile_duplicate(self):
        """중복 프로필 생성 시도"""
        # 첫 번째 프로필 생성
        data1 = {'name': '첫 관리자'}
        self.service.create_profile(
            user_id=self.user_id,
            company_id=self.company_id,
            data=data1
        )

        # 두 번째 프로필 생성 시도
        data2 = {'name': '두 번째 관리자'}
        success, profile, error = self.service.create_profile(
            user_id=self.user_id,
            company_id=self.company_id,
            data=data2
        )

        assert success is False
        assert profile is None
        assert error is not None
        assert '이미 프로필이 존재합니다' in error

    @pytest.mark.unit
    def test_update_profile(self):
        """프로필 정보 수정"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='기존 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        # 수정
        data = {
            'name': '수정된 관리자',
            'position': '대표이사'
        }

        success, error = self.service.update_profile(
            user_id=self.user_id,
            data=data
        )

        assert success is True
        assert error is None

        # 확인
        updated = self.service.get_profile_by_user_id(self.user_id)
        assert updated.name == '수정된 관리자'

    @pytest.mark.unit
    def test_update_profile_not_found(self):
        """존재하지 않는 프로필 수정"""
        data = {'name': '수정된 관리자'}

        success, error = self.service.update_profile(
            user_id=99999,
            data=data
        )

        assert success is False
        assert error is not None
        assert '프로필을 찾을 수 없습니다' in error


class TestCorporateAdminProfileServiceStatus:
    """CorporateAdminProfileService 상태 관리 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_corporate):
        """테스트 설정"""
        self.session = session
        self.service = CorporateAdminProfileService()
        self.company_id = test_company.id
        self.user_id = test_user_corporate.id

        # 프로필 생성
        self.profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자',
            is_active=True
        )
        session.add(self.profile)
        session.commit()

    @pytest.mark.unit
    def test_deactivate_profile(self):
        """프로필 비활성화"""
        success, error = self.service.deactivate_profile(self.user_id)

        assert success is True
        assert error is None

        # 확인
        profile = self.service.get_profile_by_user_id(self.user_id)
        assert profile.is_active is False

    @pytest.mark.unit
    def test_activate_profile(self):
        """프로필 활성화"""
        # 먼저 비활성화
        self.profile.is_active = False
        self.session.commit()

        # 활성화
        success, error = self.service.activate_profile(self.user_id)

        assert success is True
        assert error is None

        # 확인
        profile = self.service.get_profile_by_user_id(self.user_id)
        assert profile.is_active is True

    @pytest.mark.unit
    def test_deactivate_profile_not_found(self):
        """존재하지 않는 프로필 비활성화"""
        success, error = self.service.deactivate_profile(99999)

        assert success is False
        assert error is not None
        assert '프로필을 찾을 수 없습니다' in error


class TestCorporateAdminProfileServiceUtils:
    """CorporateAdminProfileService 유틸리티 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session, test_company, test_user_corporate):
        """테스트 설정"""
        self.session = session
        self.service = CorporateAdminProfileService()
        self.company_id = test_company.id
        self.user_id = test_user_corporate.id

    @pytest.mark.unit
    def test_is_corporate_admin_true(self):
        """법인 관리자 여부 확인 (True)"""
        user = User.query.get(self.user_id)
        result = self.service.is_corporate_admin(user)

        assert result is True

    @pytest.mark.unit
    def test_is_corporate_admin_false(self, session, test_user_personal):
        """법인 관리자 여부 확인 (False)"""
        user = test_user_personal
        result = self.service.is_corporate_admin(user)

        assert result is False

    @pytest.mark.unit
    def test_has_profile_true(self):
        """프로필 존재 여부 확인 (True)"""
        # 프로필 생성
        profile = CorporateAdminProfile(
            user_id=self.user_id,
            company_id=self.company_id,
            name='테스트 관리자'
        )
        self.session.add(profile)
        self.session.commit()

        result = self.service.has_profile(self.user_id)

        assert result is True

    @pytest.mark.unit
    def test_has_profile_false(self):
        """프로필 존재 여부 확인 (False)"""
        result = self.service.has_profile(99999)

        assert result is False

