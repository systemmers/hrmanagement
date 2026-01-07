"""
Corporate Admin Profile Repository 테스트

법인 관리자 프로필 저장소 테스트
"""
import pytest
from app.domains.user.repositories.corporate_admin_profile_repository import CorporateAdminProfileRepository
from app.domains.user.models import CorporateAdminProfile
from app.domains.company.models import Company
from app.domains.user.models import User


class TestCorporateAdminProfileRepositoryInit:
    """Repository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = CorporateAdminProfileRepository()
        assert repo is not None
        assert repo.model_class == CorporateAdminProfile


class TestCorporateAdminProfileRepositoryCRUD:
    """CRUD 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CorporateAdminProfileRepository()
        
        # 테스트용 회사와 사용자 생성
        self.company = Company(
            name='테스트회사',
            business_number='1234567890',
            representative='대표'
        )
        session.add(self.company)
        
        self.user = User(
            username='testadmin',
            email='admin@test.com',
            role='corporate_admin',
            company_id=self.company.id
        )
        self.user.set_password('password')
        session.add(self.user)
        session.commit()

    def test_get_by_user_id_not_exists(self, session):
        """존재하지 않는 프로필 조회"""
        result = self.repo.get_by_user_id(999)
        assert result is None

    def test_get_by_user_id_exists(self, session):
        """존재하는 프로필 조회"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자'
        )
        session.add(profile)
        session.commit()

        result = self.repo.get_by_user_id(self.user.id)

        assert result is not None
        assert result.user_id == self.user.id

    def test_get_dict_by_user_id(self, session):
        """딕셔너리 형식으로 프로필 조회"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자'
        )
        session.add(profile)
        session.commit()

        result = self.repo.get_dict_by_user_id(self.user.id)

        assert result is not None
        assert isinstance(result, dict)
        assert 'name' in result

    def test_get_dict_by_user_id_not_exists(self, session):
        """존재하지 않을 때 None 반환"""
        result = self.repo.get_dict_by_user_id(999)
        assert result is None

    def test_get_by_company_id(self, session):
        """회사별 프로필 목록 조회"""
        profile1 = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자1'
        )
        session.add(profile1)
        session.commit()

        result = self.repo.get_by_company_id(self.company.id)

        assert len(result) >= 1
        assert all(p.company_id == self.company.id for p in result)

    def test_get_active_by_company_id(self, session):
        """활성 프로필만 조회"""
        profile1 = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자1',
            is_active=True
        )
        session.add(profile1)
        session.commit()

        result = self.repo.get_active_by_company_id(self.company.id)

        assert len(result) >= 1
        assert all(p.is_active for p in result)

    def test_create_profile_minimal(self, session):
        """최소 정보로 프로필 생성"""
        profile = self.repo.create_profile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='새 관리자'
        )

        assert profile is not None
        assert profile.name == '새 관리자'
        assert profile.user_id == self.user.id
        assert profile.company_id == self.company.id

    def test_create_profile_full(self, session):
        """전체 정보로 프로필 생성"""
        profile = self.repo.create_profile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='새 관리자',
            english_name='New Admin',
            position='Manager',
            mobile_phone='010-1234-5678',
            email='newadmin@test.com'
        )

        assert profile is not None
        assert profile.english_name == 'New Admin'
        assert profile.position == 'Manager'
        assert profile.mobile_phone == '010-1234-5678'

    def test_create_profile_no_commit(self, session):
        """커밋 없이 프로필 생성"""
        profile = self.repo.create_profile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='새 관리자',
            commit=False
        )

        assert profile is not None
        # 세션에 추가되었지만 아직 커밋되지 않음
        # flush()를 호출하면 ID는 할당되지만 트랜잭션은 커밋되지 않음
        session.flush()
        
        # 수동 커밋
        session.commit()
        queried = CorporateAdminProfile.query.filter_by(user_id=self.user.id).first()
        assert queried is not None

    def test_update_profile(self, session):
        """프로필 업데이트"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자'
        )
        session.add(profile)
        session.commit()

        update_data = {
            'name': '수정된 이름',
            'position': 'Senior Manager'
        }

        updated = self.repo.update_profile(profile, update_data)

        assert updated.name == '수정된 이름'
        assert updated.position == 'Senior Manager'

    def test_update_profile_no_commit(self, session):
        """커밋 없이 프로필 업데이트"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자'
        )
        session.add(profile)
        session.commit()

        update_data = {'name': '수정된 이름'}
        self.repo.update_profile(profile, update_data, commit=False)

        # 세션 롤백
        session.rollback()
        
        # 수정이 롤백되었는지 확인
        queried = CorporateAdminProfile.query.filter_by(user_id=self.user.id).first()
        assert queried.name == '관리자'

    def test_exists_for_user_true(self, session):
        """프로필 존재 확인 (있음)"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자'
        )
        session.add(profile)
        session.commit()

        result = self.repo.exists_for_user(self.user.id)
        assert result is True

    def test_exists_for_user_false(self, session):
        """프로필 존재 확인 (없음)"""
        result = self.repo.exists_for_user(999)
        assert result is False

    def test_deactivate_profile(self, session):
        """프로필 비활성화"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자',
            is_active=True
        )
        session.add(profile)
        session.commit()

        result = self.repo.deactivate(profile)

        assert result.is_active is False

    def test_activate_profile(self, session):
        """프로필 활성화"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자',
            is_active=False
        )
        session.add(profile)
        session.commit()

        result = self.repo.activate(profile)

        assert result.is_active is True

    def test_deactivate_no_commit(self, session):
        """커밋 없이 비활성화"""
        profile = CorporateAdminProfile(
            user_id=self.user.id,
            company_id=self.company.id,
            name='관리자',
            is_active=True
        )
        session.add(profile)
        session.commit()

        self.repo.deactivate(profile, commit=False)
        session.rollback()

        queried = CorporateAdminProfile.query.filter_by(user_id=self.user.id).first()
        assert queried.is_active is True

