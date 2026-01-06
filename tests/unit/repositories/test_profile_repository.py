"""
ProfileRepository 단위 테스트
"""
import pytest
from app.domains.employee.repositories import ProfileRepository
from app.domains.employee.models import Profile


class TestProfileRepository:
    """ProfileRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = ProfileRepository()

    @pytest.mark.unit
    def test_create_profile(self, session):
        """프로필 생성 테스트"""
        data = {
            'name': '홍길동',
            'email': 'hong@test.com'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['name'] == '홍길동'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_get_by_user_id(self, session, test_user_personal):
        """User ID로 프로필 조회"""
        profile = Profile(
            user_id=test_user_personal.id,
            name='홍길동',
            email='hong@test.com'
        )
        session.add(profile)
        session.commit()

        result = self.repo.get_by_user_id(test_user_personal.id)

        assert result is not None
        assert isinstance(result, Profile)
        assert result.name == '홍길동'

    @pytest.mark.unit
    def test_get_or_create_for_user(self, session, test_user_personal):
        """User에 대한 프로필 조회 또는 생성"""
        result = self.repo.get_or_create_for_user(
            user_id=test_user_personal.id,
            name='홍길동',
            email='hong@test.com'
        )

        assert result is not None
        assert isinstance(result, Profile)
        assert result.name == '홍길동'

    @pytest.mark.unit
    def test_update_by_user_id(self, session, test_user_personal):
        """User ID로 프로필 업데이트"""
        profile = Profile(
            user_id=test_user_personal.id,
            name='홍길동'
        )
        session.add(profile)
        session.commit()

        result = self.repo.update_by_user_id(
            user_id=test_user_personal.id,
            data={'name': '김철수'}
        )

        assert result is not None
        assert result.name == '김철수'

    @pytest.mark.unit
    def test_search_by_name(self, session):
        """이름으로 프로필 검색"""
        profile1 = Profile(name='홍길동', email='hong1@test.com')
        profile2 = Profile(name='홍길순', email='hong2@test.com')
        session.add_all([profile1, profile2])
        session.commit()

        result = self.repo.search_by_name('홍길')

        assert len(result) >= 2

    @pytest.mark.unit
    def test_get_by_user_id_dict(self, session, test_user_personal):
        """User ID로 프로필 조회 (딕셔너리 반환)"""
        profile = Profile(
            user_id=test_user_personal.id,
            name='홍길동',
            email='hong@test.com'
        )
        session.add(profile)
        session.commit()

        result = self.repo.get_by_user_id_dict(test_user_personal.id)

        assert result is not None
        assert isinstance(result, dict)
        assert result['name'] == '홍길동'

    @pytest.mark.unit
    def test_get_by_id_model(self, session):
        """ID로 프로필 모델 조회"""
        profile = Profile(name='홍길동', email='hong@test.com')
        session.add(profile)
        session.commit()

        result = self.repo.get_by_id_model(profile.id)

        assert result is not None
        assert isinstance(result, Profile)
        assert result.name == '홍길동'

    @pytest.mark.unit
    def test_create_for_employee(self, session):
        """직원용 프로필 생성"""
        data = {
            'name': '직원홍길동',
            'email': 'employee@test.com'
        }
        result = self.repo.create_for_employee(data)

        assert result is not None
        assert isinstance(result, Profile)
        assert result.name == '직원홍길동'

    @pytest.mark.unit
    def test_update_profile(self, session):
        """프로필 업데이트"""
        profile = Profile(name='홍길동', email='hong@test.com')
        session.add(profile)
        session.commit()

        result = self.repo.update_profile(profile.id, {'name': '김철수'})

        assert result is not None
        assert result.name == '김철수'

    @pytest.mark.unit
    def test_update_profile_not_found(self, session):
        """존재하지 않는 프로필 업데이트"""
        result = self.repo.update_profile(999, {'name': '김철수'})

        assert result is None

    @pytest.mark.unit
    def test_get_public_profiles(self, session):
        """공개된 프로필 목록 조회"""
        profile1 = Profile(name='홍길동', email='hong1@test.com', is_public=True)
        profile2 = Profile(name='김철수', email='hong2@test.com', is_public=False)
        session.add_all([profile1, profile2])
        session.commit()

        result = self.repo.get_public_profiles(limit=10)

        assert len(result) >= 1
        assert all(p['is_public'] is True for p in result)

    @pytest.mark.unit
    def test_get_profiles_without_user(self, session):
        """User 연결 없는 프로필 조회"""
        profile1 = Profile(name='홍길동', email='hong1@test.com', user_id=None)
        profile2 = Profile(name='김철수', email='hong2@test.com', user_id=1)
        session.add_all([profile1, profile2])
        session.commit()

        result = self.repo.get_profiles_without_user()

        assert len(result) >= 1
        assert all(p.user_id is None for p in result)

    @pytest.mark.unit
    def test_link_to_user(self, session, test_user_personal):
        """프로필을 User에 연결"""
        profile = Profile(name='홍길동', email='hong@test.com', user_id=None)
        session.add(profile)
        session.commit()

        result = self.repo.link_to_user(profile.id, test_user_personal.id)

        assert result is not None
        assert result.user_id == test_user_personal.id

    @pytest.mark.unit
    def test_link_to_user_not_found(self, session, test_user_personal):
        """존재하지 않는 프로필 연결"""
        result = self.repo.link_to_user(999, test_user_personal.id)

        assert result is None

