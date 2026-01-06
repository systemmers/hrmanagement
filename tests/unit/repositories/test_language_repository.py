"""
LanguageRepository 단위 테스트
"""
import pytest
from app.domains.employee.repositories import LanguageRepository
from app.domains.employee.models import Language


class TestLanguageRepository:
    """LanguageRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = LanguageRepository()

    @pytest.mark.unit
    def test_create_language(self, session, test_employee):
        """어학 능력 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'language_name': '영어',
            'level': 'advanced'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['language_name'] == '영어'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 어학 능력 조회"""
        language = Language(
            employee_id=test_employee.id,
            language_name='영어',
            level='advanced'
        )
        session.add(language)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert len(result) >= 1
        assert any(l.language_name == '영어' for l in result)

