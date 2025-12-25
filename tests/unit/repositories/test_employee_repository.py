"""
EmployeeRepository 단위 테스트
"""
import pytest
from app.repositories.employee_repository import EmployeeRepository
from app.models.employee import Employee


class TestEmployeeRepository:
    """EmployeeRepository 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session
        self.repo = EmployeeRepository()

    @pytest.mark.unit
    def test_create_employee(self, session):
        """직원 생성 테스트"""
        data = {
            'name': '김테스트',
            'department': '개발팀',
            'position': '사원',
            'status': '재직',
            'email': 'test@test.com'
        }
        result = self.repo.create(data)

        assert result is not None
        assert result['name'] == '김테스트'
        assert result['department'] == '개발팀'
        assert result['id'] is not None

    @pytest.mark.unit
    def test_get_by_id(self, session):
        """ID로 직원 조회 테스트"""
        # 직원 생성
        employee = Employee(
            name='홍길동',
            department='인사팀',
            position='대리',
            status='active'
        )
        session.add(employee)
        session.commit()

        # 조회
        result = self.repo.get_by_id(employee.id)

        assert result is not None
        assert result['name'] == '홍길동'
        assert result['department'] == '인사팀'

    @pytest.mark.unit
    def test_get_by_id_not_found(self):
        """존재하지 않는 직원 조회"""
        result = self.repo.get_by_id(9999)
        assert result is None

    @pytest.mark.unit
    def test_get_all(self, session):
        """전체 직원 조회 테스트"""
        # 직원 2명 생성
        emp1 = Employee(name='직원1', department='개발팀', status='active')
        emp2 = Employee(name='직원2', department='인사팀', status='active')
        session.add_all([emp1, emp2])
        session.commit()

        result = self.repo.get_all()

        assert len(result) >= 2
        names = [e['name'] for e in result]
        assert '직원1' in names
        assert '직원2' in names

    @pytest.mark.unit
    def test_update_employee(self, session):
        """직원 정보 수정 테스트"""
        # 직원 생성
        employee = Employee(
            name='수정전',
            department='개발팀',
            position='사원',
            status='active'
        )
        session.add(employee)
        session.commit()

        # 수정
        update_data = {
            'name': '수정후',
            'position': '대리'
        }
        result = self.repo.update(employee.id, update_data)

        assert result is not None
        assert result['name'] == '수정후'
        assert result['position'] == '대리'
        assert result['department'] == '개발팀'  # 변경하지 않은 필드 유지

    @pytest.mark.unit
    def test_delete_employee(self, session):
        """직원 삭제 테스트"""
        # 직원 생성
        employee = Employee(
            name='삭제대상',
            department='개발팀',
            status='active'
        )
        session.add(employee)
        session.commit()
        emp_id = employee.id

        # 삭제
        result = self.repo.delete(emp_id)
        assert result is True

        # 삭제 확인
        assert self.repo.get_by_id(emp_id) is None

    @pytest.mark.unit
    def test_delete_not_found(self):
        """존재하지 않는 직원 삭제"""
        result = self.repo.delete(9999)
        assert result is False

    @pytest.mark.unit
    def test_search_by_name(self, session):
        """이름으로 검색 테스트"""
        # 직원 생성
        emp1 = Employee(name='김철수', department='개발팀', status='active')
        emp2 = Employee(name='박영희', department='인사팀', status='active')
        session.add_all([emp1, emp2])
        session.commit()

        # 검색
        result = self.repo.search('김철')

        assert len(result) >= 1
        assert any(e['name'] == '김철수' for e in result)

    @pytest.mark.unit
    def test_filter_by_department(self, session):
        """부서별 필터 테스트"""
        # 직원 생성
        emp1 = Employee(name='개발1', department='개발팀', status='active')
        emp2 = Employee(name='인사1', department='인사팀', status='active')
        session.add_all([emp1, emp2])
        session.commit()

        # 필터
        result = self.repo.filter_by_department('개발팀')

        assert all(e['department'] == '개발팀' for e in result)

    @pytest.mark.unit
    def test_get_count(self, session):
        """직원 수 조회 테스트"""
        # 초기 상태 저장
        initial_count = self.repo.get_count()

        # 직원 생성
        emp = Employee(name='테스트', department='개발팀', status='active')
        session.add(emp)
        session.commit()

        # 카운트 확인
        assert self.repo.get_count() == initial_count + 1

    @pytest.mark.unit
    def test_get_statistics(self, session):
        """통계 조회 테스트"""
        # 직원 생성
        emp1 = Employee(name='재직1', status='active')
        emp2 = Employee(name='휴직1', status='on_leave')
        session.add_all([emp1, emp2])
        session.commit()

        # 통계
        stats = self.repo.get_statistics()

        assert 'total' in stats
        assert 'active' in stats
        assert 'onLeave' in stats
        assert 'resigned' in stats
        assert stats['total'] >= 2
