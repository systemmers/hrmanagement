"""
EducationRepository 단위 테스트
"""
import pytest
from app.repositories.education_repository import EducationRepository
from app.models.education import Education


class TestEducationRepository:
    """EducationRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = EducationRepository()

    @pytest.mark.unit
    def test_create_education(self, session, test_employee):
        """학력 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'school_name': '테스트대학',
            'school_type': 'university',
            'degree': 'bachelor',
            'major': '컴퓨터공학'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['school_name'] == '테스트대학'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 학력 조회"""
        education = Education(
            employee_id=test_employee.id,
            school_name='테스트대학',
            school_type='university'
        )
        session.add(education)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert len(result) >= 1
        assert any(e.school_name == '테스트대학' for e in result)

    @pytest.mark.unit
    def test_update_education(self, session, test_employee):
        """학력 수정"""
        education = Education(
            employee_id=test_employee.id,
            school_name='테스트대학'
        )
        session.add(education)
        session.commit()

        result = self.repo.update(education.id, {'school_name': '수정된대학'})

        assert result is not None
        assert result['school_name'] == '수정된대학'

    @pytest.mark.unit
    def test_delete_education(self, session, test_employee):
        """학력 삭제"""
        education = Education(
            employee_id=test_employee.id,
            school_name='테스트대학'
        )
        session.add(education)
        session.commit()
        edu_id = education.id

        result = self.repo.delete(edu_id)

        assert result is True
        assert self.repo.find_by_id(edu_id) is None

