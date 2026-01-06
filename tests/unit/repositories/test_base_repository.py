"""
BaseRepository 테스트

BaseRepository의 CRUD 메서드 테스트
"""
import pytest

from app.repositories.base_repository import BaseRepository
from app.models.employee import Employee


class TestBaseRepository:
    """BaseRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = BaseRepository(Employee)

    @pytest.mark.unit
    def test_find_all(self, session, test_company):
        """find_all() 메서드 테스트"""
        emp1 = Employee(name='직원1', company_id=test_company.id, status='active')
        emp2 = Employee(name='직원2', company_id=test_company.id, status='active')
        session.add_all([emp1, emp2])
        session.commit()

        result = self.repo.find_all()

        assert len(result) >= 2
        assert all(isinstance(e, Employee) for e in result)

    @pytest.mark.unit
    def test_find_by_id(self, session, test_company):
        """find_by_id() 메서드 테스트"""
        employee = Employee(
            name='홍길동',
            company_id=test_company.id,
            status='active'
        )
        session.add(employee)
        session.commit()

        result = self.repo.find_by_id(employee.id)

        assert result is not None
        assert isinstance(result, Employee)
        assert result.name == '홍길동'

    @pytest.mark.unit
    def test_find_by_id_not_found(self):
        """존재하지 않는 ID 조회"""
        result = self.repo.find_by_id(99999)
        assert result is None

    @pytest.mark.unit
    def test_create(self, session, test_company):
        """create() 메서드 테스트"""
        data = {
            'name': '신규직원',
            'department': '개발팀',
            'position': '사원',
            'status': 'active',
            'company_id': test_company.id
        }

        result = self.repo.create(data)

        assert result is not None
        assert isinstance(result, dict)
        assert result['name'] == '신규직원'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_create_without_commit(self, session, test_company):
        """create() 메서드 commit=False 테스트"""
        data = {
            'name': '신규직원',
            'company_id': test_company.id,
            'status': 'active'
        }

        result = self.repo.create(data, commit=False)

        assert result is not None
        # commit=False이므로 세션에만 추가되고 커밋되지 않음

    @pytest.mark.unit
    def test_update(self, session, test_company):
        """update() 메서드 테스트"""
        employee = Employee(
            name='수정전',
            company_id=test_company.id,
            status='active'
        )
        session.add(employee)
        session.commit()

        result = self.repo.update(employee.id, {
            'name': '수정후',
            'position': '대리'
        })

        assert result is not None
        assert result['name'] == '수정후'
        assert result['position'] == '대리'

    @pytest.mark.unit
    def test_update_not_found(self):
        """존재하지 않는 레코드 수정"""
        result = self.repo.update(99999, {'name': '수정'})
        assert result is None

    @pytest.mark.unit
    def test_delete(self, session, test_company):
        """delete() 메서드 테스트"""
        employee = Employee(
            name='삭제대상',
            company_id=test_company.id,
            status='active'
        )
        session.add(employee)
        session.commit()
        emp_id = employee.id

        result = self.repo.delete(emp_id)

        assert result is True
        assert self.repo.find_by_id(emp_id) is None

    @pytest.mark.unit
    def test_delete_not_found(self):
        """존재하지 않는 레코드 삭제"""
        result = self.repo.delete(99999)
        assert result is False

    @pytest.mark.unit
    def test_create_model(self, session, test_company):
        """create_model() 메서드 테스트"""
        employee = Employee(
            name='직접생성',
            company_id=test_company.id,
            status='active'
        )

        result = self.repo.create_model(employee)

        assert result is not None
        assert isinstance(result, Employee)
        assert result.id is not None

    @pytest.mark.unit
    def test_delete_model(self, session, test_company):
        """delete_model() 메서드 테스트"""
        employee = Employee(
            name='삭제대상',
            company_id=test_company.id,
            status='active'
        )
        session.add(employee)
        session.commit()
        emp_id = employee.id

        result = self.repo.delete_model(employee)

        assert result is True
        assert self.repo.find_by_id(emp_id) is None

