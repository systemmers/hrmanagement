"""
CareerRepository 단위 테스트
"""
import pytest
from app.repositories.career_repository import CareerRepository
from app.models.career import Career


class TestCareerRepository:
    """CareerRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = CareerRepository()

    @pytest.mark.unit
    def test_create_career(self, session, test_employee):
        """경력 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'company_name': '테스트회사',
            'department': '개발팀',
            'position': '사원',
            'start_date': '2020-01-01'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['company_name'] == '테스트회사'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 경력 조회"""
        career = Career(
            employee_id=test_employee.id,
            company_name='테스트회사',
            position='사원'
        )
        session.add(career)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert len(result) >= 1
        assert any(c.company_name == '테스트회사' for c in result)

    @pytest.mark.unit
    def test_update_career(self, session, test_employee):
        """경력 수정"""
        career = Career(
            employee_id=test_employee.id,
            company_name='테스트회사',
            position='사원'
        )
        session.add(career)
        session.commit()

        result = self.repo.update(career.id, {'position': '대리'})

        assert result is not None
        assert result['position'] == '대리'

