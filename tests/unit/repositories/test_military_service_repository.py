"""
MilitaryServiceRepository 단위 테스트
"""
import pytest
from app.domains.employee.repositories import MilitaryServiceRepository
from app.domains.employee.models import MilitaryService


class TestMilitaryServiceRepository:
    """MilitaryServiceRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = MilitaryServiceRepository()

    @pytest.mark.unit
    def test_create_military_service(self, session, test_employee):
        """병역 정보 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'military_status': '군필',
            'service_type': 'army'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['military_status'] == '군필'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 병역 정보 조회"""
        military = MilitaryService(
            employee_id=test_employee.id,
            military_status='군필'
        )
        session.add(military)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert result is not None
        assert result.military_status == '군필'

