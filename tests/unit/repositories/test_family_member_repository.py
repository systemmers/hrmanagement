"""
FamilyMemberRepository 단위 테스트
"""
import pytest
from app.domains.employee.repositories import FamilyMemberRepository
from app.domains.employee.models import FamilyMember


class TestFamilyMemberRepository:
    """FamilyMemberRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = FamilyMemberRepository()

    @pytest.mark.unit
    def test_create_family_member(self, session, test_employee):
        """가족 구성원 생성 테스트"""
        data = {
            'employee_id': test_employee.id,
            'relation': '배우자',
            'name': '홍길순'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['relation'] == '배우자'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_find_by_employee_id(self, session, test_employee):
        """직원 ID로 가족 구성원 조회"""
        family = FamilyMember(
            employee_id=test_employee.id,
            relation='배우자',
            name='홍길순'
        )
        session.add(family)
        session.commit()

        result = self.repo.find_by_employee_id(test_employee.id)

        assert len(result) >= 1
        assert any(f.relation == '배우자' for f in result)

