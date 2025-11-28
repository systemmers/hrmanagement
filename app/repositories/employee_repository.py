"""
Employee Repository

직원 데이터의 CRUD 및 검색 기능을 제공합니다.
"""
from typing import List, Optional, Dict
from app.database import db
from app.models import Employee
from .base_repository import BaseRepository


class EmployeeRepository(BaseRepository):
    """직원 저장소"""

    def __init__(self):
        super().__init__(Employee)

    def get_all(self) -> List[Dict]:
        """모든 직원 조회"""
        employees = Employee.query.order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def get_by_id(self, employee_id: str) -> Optional[Dict]:
        """ID로 직원 조회"""
        employee = Employee.query.get(employee_id)
        return employee.to_dict() if employee else None

    def create(self, data: Dict) -> Dict:
        """새 직원 생성"""
        # ID 자동 생성 (기존 로직 유지)
        if not data.get('id'):
            data['id'] = self._generate_new_id()

        employee = Employee.from_dict(data)
        db.session.add(employee)
        db.session.commit()
        return employee.to_dict()

    def update(self, employee_id: str, data: Dict) -> Optional[Dict]:
        """직원 정보 수정"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return None

        # 데이터 업데이트
        for key, value in data.items():
            snake_key = self._camel_to_snake(key)
            if hasattr(employee, snake_key) and key != 'id':
                setattr(employee, snake_key, value)

        db.session.commit()
        return employee.to_dict()

    def delete(self, employee_id: str) -> bool:
        """직원 삭제 (관련 데이터 cascade 삭제)"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return False

        db.session.delete(employee)
        db.session.commit()
        return True

    def search(self, query: str) -> List[Dict]:
        """직원 검색 (이름, 부서, 직급)"""
        if not query:
            return self.get_all()

        search_term = f'%{query}%'
        employees = Employee.query.filter(
            db.or_(
                Employee.name.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.position.ilike(search_term),
                Employee.id.ilike(search_term)
            )
        ).order_by(Employee.id).all()

        return [emp.to_dict() for emp in employees]

    def filter_by_department(self, department: str) -> List[Dict]:
        """부서별 직원 조회"""
        employees = Employee.query.filter_by(department=department).order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def filter_by_status(self, status: str) -> List[Dict]:
        """재직상태별 직원 조회"""
        employees = Employee.query.filter_by(status=status).order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def get_count(self) -> int:
        """전체 직원 수"""
        return Employee.query.count()

    def get_count_by_department(self) -> Dict[str, int]:
        """부서별 직원 수"""
        result = db.session.query(
            Employee.department,
            db.func.count(Employee.id)
        ).group_by(Employee.department).all()

        return {dept or '미지정': count for dept, count in result}

    def get_count_by_status(self) -> Dict[str, int]:
        """재직상태별 직원 수"""
        result = db.session.query(
            Employee.status,
            db.func.count(Employee.id)
        ).group_by(Employee.status).all()

        return {status or '미지정': count for status, count in result}

    def _generate_new_id(self) -> str:
        """새 직원 ID 생성 (EMP001 형식)"""
        last_employee = Employee.query.order_by(Employee.id.desc()).first()
        if last_employee:
            try:
                # EMP001 형식에서 숫자 추출
                num = int(last_employee.id.replace('EMP', ''))
                return f'EMP{num + 1:03d}'
            except (ValueError, AttributeError):
                pass
        return 'EMP001'
