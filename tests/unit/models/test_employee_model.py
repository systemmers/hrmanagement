"""
Employee Model 테스트

Employee 모델의 메서드 테스트:
- to_dict()
- from_dict()
- 관계형 메서드
"""
import pytest
from datetime import date

from app.models.employee import Employee


class TestEmployeeModel:
    """Employee 모델 테스트 클래스"""

    @pytest.fixture(autouse=True)
    def setup(self, session):
        """테스트 설정"""
        self.session = session

    @pytest.mark.unit
    def test_to_dict(self, session, test_company):
        """to_dict() 메서드 테스트"""
        employee = Employee(
            name='홍길동',
            department='개발팀',
            position='사원',
            status='active',
            company_id=test_company.id
        )
        session.add(employee)
        session.commit()

        result = employee.to_dict()

        assert isinstance(result, dict)
        assert result['name'] == '홍길동'
        assert result['department'] == '개발팀'
        assert result['id'] == employee.id

    @pytest.mark.unit
    def test_from_dict(self, session, test_company):
        """from_dict() 메서드 테스트"""
        data = {
            'name': '김철수',
            'department': '인사팀',
            'position': '대리',
            'status': 'active',
            'company_id': test_company.id
        }

        employee = Employee.from_dict(data)
        session.add(employee)
        session.commit()

        assert employee.name == '김철수'
        assert employee.department == '인사팀'
        assert employee.position == '대리'

    @pytest.mark.unit
    def test_employment_type_property(self, session, test_company):
        """employment_type 프로퍼티 테스트"""
        employee = Employee(
            name='홍길동',
            company_id=test_company.id
        )
        session.add(employee)
        session.commit()

        # contract가 없을 때
        assert employee.employment_type is None

        # contract가 있을 때
        from app.models.contract import Contract
        contract = Contract(
            employee_id=employee.id,
            employee_type='정규직'
        )
        session.add(contract)
        session.commit()

        assert employee.employment_type == '정규직'

