"""
SystemSettingRepository 단위 테스트

시스템 설정 CRUD 및 캐싱 기능 테스트
"""
import pytest
from app.repositories.system_setting_repository import SystemSettingRepository
from app.models import SystemSetting


class TestSystemSettingRepositoryInit:
    """SystemSettingRepository 초기화 테스트"""

    def test_repository_creation(self):
        """저장소 생성"""
        repo = SystemSettingRepository()
        assert repo is not None
        assert repo.model_class == SystemSetting


class TestSystemSettingRepositoryGet:
    """설정 조회 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = SystemSettingRepository()
        self.repo.clear_cache()

    def test_get_by_key_exists(self, session):
        """키로 설정 조회 (존재)"""
        setting = SystemSetting(key='test.key', value='test_value', value_type='string')
        session.add(setting)
        session.commit()

        result = self.repo.get_by_key('test.key')

        assert result is not None
        assert result['key'] == 'test.key'
        assert result['value'] == 'test_value'

    def test_get_by_key_not_exists(self, session):
        """키로 설정 조회 (미존재)"""
        result = self.repo.get_by_key('nonexistent.key')
        assert result is None

    def test_get_by_key_with_cache(self, session):
        """캐시를 통한 설정 조회"""
        setting = SystemSetting(key='cache.key', value='cached', value_type='string')
        session.add(setting)
        session.commit()

        # 첫 조회 - DB에서
        result1 = self.repo.get_by_key('cache.key')

        # 두 번째 조회 - 캐시에서
        result2 = self.repo.get_by_key('cache.key')

        assert result1 == result2

    def test_get_value(self, session):
        """타입 변환된 값 조회"""
        setting = SystemSetting(key='test.int', value='42', value_type='integer')
        session.add(setting)
        session.commit()

        result = self.repo.get_value('test.int')
        assert result == 42
        assert isinstance(result, int)

    def test_get_value_with_default(self, session):
        """기본값과 함께 값 조회"""
        result = self.repo.get_value('nonexistent.key', default='default_value')
        assert result == 'default_value'

    def test_get_by_category(self, session):
        """카테고리별 설정 조회"""
        setting1 = SystemSetting(key='email.domain', value='test.com', value_type='string', category='email')
        setting2 = SystemSetting(key='email.format', value='{first}.{last}', value_type='string', category='email')
        setting3 = SystemSetting(key='company.name', value='Test', value_type='string', category='company')
        session.add_all([setting1, setting2, setting3])
        session.commit()

        result = self.repo.get_by_category('email')

        assert len(result) == 2
        assert all(s['category'] == 'email' for s in result)

    def test_get_all_grouped(self, session):
        """카테고리별 그룹화된 모든 설정 조회"""
        setting1 = SystemSetting(key='email.domain', value='test.com', value_type='string', category='email')
        setting2 = SystemSetting(key='company.name', value='Test', value_type='string', category='company')
        session.add_all([setting1, setting2])
        session.commit()

        result = self.repo.get_all_grouped()

        assert 'email' in result
        assert 'company' in result
        assert len(result['email']) >= 1
        assert len(result['company']) >= 1


class TestSystemSettingRepositorySet:
    """설정 저장 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = SystemSettingRepository()
        self.repo.clear_cache()

    def test_set_value_new(self, session):
        """새 설정 저장"""
        result = self.repo.set_value('new.key', 'new_value', value_type='string', description='Test')

        assert result is not None
        assert result['key'] == 'new.key'
        assert result['value'] == 'new_value'

    def test_set_value_update(self, session):
        """기존 설정 업데이트"""
        setting = SystemSetting(key='update.key', value='old', value_type='string')
        session.add(setting)
        session.commit()

        result = self.repo.set_value('update.key', 'new', value_type='string')

        assert result['value'] == 'new'

    def test_bulk_set_simple(self, session):
        """여러 설정 일괄 저장 (단순값)"""
        settings = {
            'test.key1': 'value1',
            'test.key2': 42,
            'test.key3': True
        }

        results = self.repo.bulk_set(settings, category='test')

        assert len(results) == 3
        assert all(r['category'] == 'test' for r in results)

    def test_bulk_set_with_details(self, session):
        """여러 설정 일괄 저장 (상세정보 포함)"""
        settings = {
            'detailed.key1': {
                'value': 'value1',
                'type': 'string',
                'description': 'Test setting'
            },
            'detailed.key2': {
                'value': 100,
                'type': 'integer'
            }
        }

        results = self.repo.bulk_set(settings)

        assert len(results) == 2
        assert results[0]['value'] == 'value1'


class TestSystemSettingRepositoryDelete:
    """설정 삭제 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = SystemSettingRepository()
        self.repo.clear_cache()

    def test_delete_by_key_exists(self, session):
        """기존 설정 삭제"""
        setting = SystemSetting(key='delete.key', value='value', value_type='string')
        session.add(setting)
        session.commit()

        result = self.repo.delete_by_key('delete.key')
        assert result is True

        # 실제로 삭제되었는지 확인
        deleted = SystemSetting.query.filter_by(key='delete.key').first()
        assert deleted is None

    def test_delete_by_key_not_exists(self, session):
        """존재하지 않는 설정 삭제"""
        result = self.repo.delete_by_key('nonexistent.key')
        assert result is False


class TestSystemSettingRepositoryCache:
    """캐시 관리 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = SystemSettingRepository()
        self.repo.clear_cache()

    def test_clear_cache(self, session):
        """전체 캐시 클리어"""
        setting = SystemSetting(key='cache.test', value='value', value_type='string')
        session.add(setting)
        session.commit()

        # 캐시에 로드
        self.repo.get_by_key('cache.test')

        # 캐시 클리어
        self.repo.clear_cache()

        # 캐시가 비어있는지 확인
        assert len(self.repo._cache) == 0

    def test_enable_disable_cache(self, session):
        """캐시 활성화/비활성화"""
        # 캐시 비활성화
        self.repo.enable_cache(False)
        assert self.repo._cache_enabled is False

        # 캐시 활성화
        self.repo.enable_cache(True)
        assert self.repo._cache_enabled is True


class TestSystemSettingRepositoryConvenience:
    """편의 메서드 테스트"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = SystemSettingRepository()
        self.repo.clear_cache()

    def test_get_company_info(self, session):
        """회사 정보 조회"""
        setting = SystemSetting(
            key='company.name',
            value='Test Company',
            value_type='string',
            category='company'
        )
        session.add(setting)
        session.commit()

        result = self.repo.get_company_info()

        assert 'name' in result
        assert result['name'] == 'Test Company'

    def test_set_company_info(self, session):
        """회사 정보 저장"""
        info = {
            'name': 'New Company',
            'address': '123 Test St'
        }

        results = self.repo.set_company_info(info)

        assert len(results) == 2
        assert all('company.' in r['key'] for r in results)

    def test_get_employee_number_config(self, session):
        """사번 설정 조회"""
        result = self.repo.get_employee_number_config()

        assert 'format' in result
        assert 'auto_generate' in result
        assert 'prefix' in result

    def test_get_email_config(self, session):
        """이메일 설정 조회"""
        result = self.repo.get_email_config()

        assert 'domain' in result
        assert 'auto_generate' in result
        assert 'format' in result

