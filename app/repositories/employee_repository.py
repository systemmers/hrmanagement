"""
Employee Repository

직원 데이터의 CRUD 및 검색 기능을 제공합니다.
"""
from typing import List, Optional, Dict
from app.database import db
from app.models import Employee
from .base_repository import BaseRepository


class EmployeeRepository(BaseRepository):
    """직원 저장소 - 멀티테넌시 지원"""

    def __init__(self):
        super().__init__(Employee)

    # ========================================
    # 멀티테넌시 헬퍼 메서드
    # ========================================

    def _build_query(self, organization_id: int = None):
        """organization_id 필터가 적용된 기본 쿼리 생성

        Args:
            organization_id: 조직 ID (None이면 필터 미적용)

        Returns:
            SQLAlchemy Query 객체
        """
        query = Employee.query
        if organization_id:
            query = query.filter_by(organization_id=organization_id)
        return query

    def get_by_company(self, company_id: int) -> List[Dict]:
        """회사 ID로 직원 조회 (편의 메서드)

        Args:
            company_id: 회사 ID

        Returns:
            해당 회사의 직원 목록
        """
        from app.models.company import Company
        company = Company.query.get(company_id)
        if not company or not company.root_organization_id:
            return []
        return self.get_all(organization_id=company.root_organization_id)

    def verify_ownership(self, employee_id: int, organization_id: int) -> bool:
        """직원이 해당 조직에 속하는지 확인

        Args:
            employee_id: 직원 ID
            organization_id: 조직 ID

        Returns:
            소속 여부 (True/False)
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return False
        return employee.organization_id == organization_id

    # ========================================
    # CRUD 메서드
    # ========================================

    def get_all(self, organization_id: int = None) -> List[Dict]:
        """모든 직원 조회

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        employees = query.order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def get_by_id(self, employee_id: str) -> Optional[Dict]:
        """ID로 직원 조회 (dict 반환)"""
        employee = Employee.query.get(employee_id)
        return employee.to_dict() if employee else None

    def get_model_by_id(self, employee_id: int) -> Optional[Employee]:
        """ID로 직원 모델 인스턴스 조회 (관계 접근 필요시 사용)

        Returns:
            Employee 모델 인스턴스 또는 None
        """
        return Employee.query.get(employee_id)

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

    def update_partial(self, employee_id: str, data: Dict) -> Optional[Dict]:
        """직원 정보 부분 수정 (지정된 필드만 업데이트)"""
        employee = Employee.query.get(employee_id)
        if not employee:
            return None

        # 지정된 필드만 업데이트
        for key, value in data.items():
            if hasattr(employee, key) and key != 'id':
                setattr(employee, key, value)

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

    def search(self, query: str, organization_id: int = None) -> List[Dict]:
        """직원 검색 (이름, 부서, 직급)

        Args:
            query: 검색어
            organization_id: 조직 ID (None이면 전체 검색)
        """
        if not query:
            return self.get_all(organization_id=organization_id)

        search_term = f'%{query}%'
        base_query = self._build_query(organization_id)
        employees = base_query.filter(
            db.or_(
                Employee.name.ilike(search_term),
                Employee.department.ilike(search_term),
                Employee.position.ilike(search_term),
                Employee.id.ilike(search_term)
            )
        ).order_by(Employee.id).all()

        return [emp.to_dict() for emp in employees]

    def filter_by_department(self, department: str, organization_id: int = None) -> List[Dict]:
        """부서별 직원 조회

        Args:
            department: 부서명
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        employees = query.filter_by(department=department).order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def filter_by_status(self, status: str, organization_id: int = None) -> List[Dict]:
        """재직상태별 직원 조회

        Args:
            status: 재직상태
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        employees = query.filter_by(status=status).order_by(Employee.id).all()
        return [emp.to_dict() for emp in employees]

    def get_count(self, organization_id: int = None) -> int:
        """전체 직원 수

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        return query.count()

    def get_count_by_department(self, organization_id: int = None) -> Dict[str, int]:
        """부서별 직원 수

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = db.session.query(
            Employee.department,
            db.func.count(Employee.id)
        )
        if organization_id:
            query = query.filter(Employee.organization_id == organization_id)
        result = query.group_by(Employee.department).all()

        return {dept or '미지정': count for dept, count in result}

    def get_count_by_status(self, organization_id: int = None) -> Dict[str, int]:
        """재직상태별 직원 수

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = db.session.query(
            Employee.status,
            db.func.count(Employee.id)
        )
        if organization_id:
            query = query.filter(Employee.organization_id == organization_id)
        result = query.group_by(Employee.status).all()

        return {status or '미지정': count for status, count in result}

    def get_statistics(self, organization_id: int = None) -> Dict:
        """직원 통계 정보

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        total = query.count()
        active = self._build_query(organization_id).filter_by(status='재직').count()
        on_leave = self._build_query(organization_id).filter_by(status='휴직').count()
        resigned = self._build_query(organization_id).filter_by(status='퇴사').count()

        return {
            'total': total,
            'active': active,
            'onLeave': on_leave,
            'resigned': resigned
        }

    def get_department_statistics(self, organization_id: int = None) -> Dict[str, int]:
        """부서별 통계 정보

        Args:
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = db.session.query(
            Employee.department,
            db.func.count(Employee.id)
        )
        if organization_id:
            query = query.filter(Employee.organization_id == organization_id)
        result = query.group_by(Employee.department).all()

        return {dept or '미지정': count for dept, count in result}

    def get_recent_employees(self, limit: int = 5, organization_id: int = None) -> List[Dict]:
        """최근 입사 직원

        Args:
            limit: 조회할 직원 수
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)
        employees = query.filter(
            Employee.hire_date.isnot(None)
        ).order_by(Employee.hire_date.desc()).limit(limit).all()
        return [emp.to_dict() for emp in employees]

    def filter_employees(self, department: str = None, position: str = None, status: str = None,
                         departments: List[str] = None, positions: List[str] = None, statuses: List[str] = None,
                         sort_by: str = None, sort_order: str = 'asc', organization_id: int = None) -> List[Dict]:
        """다중 필터링 및 정렬

        Args:
            department: 단일 부서 필터
            position: 단일 직급 필터
            status: 단일 상태 필터
            departments: 복수 부서 필터
            positions: 복수 직급 필터
            statuses: 복수 상태 필터
            sort_by: 정렬 기준 컬럼
            sort_order: 정렬 순서 (asc/desc)
            organization_id: 조직 ID (None이면 전체 조회)
        """
        query = self._build_query(organization_id)

        # 단일 필터 (하위 호환성)
        if department:
            query = query.filter(Employee.department == department)
        if position:
            query = query.filter(Employee.position == position)
        if status:
            query = query.filter(Employee.status == status)

        # 다중 필터
        if departments:
            query = query.filter(Employee.department.in_(departments))
        if positions:
            query = query.filter(Employee.position.in_(positions))
        if statuses:
            query = query.filter(Employee.status.in_(statuses))

        # 정렬
        if sort_by:
            sort_column = getattr(Employee, sort_by, None)
            if sort_column is not None:
                if sort_order == 'desc':
                    query = query.order_by(sort_column.desc())
                else:
                    query = query.order_by(sort_column.asc())
            else:
                query = query.order_by(Employee.id)
        else:
            query = query.order_by(Employee.id)

        employees = query.all()
        return [emp.to_dict() for emp in employees]

    def _generate_new_id(self) -> int:
        """새 직원 ID 생성 (Integer 자동 증가)"""
        last_employee = Employee.query.order_by(Employee.id.desc()).first()
        if last_employee:
            return last_employee.id + 1
        return 1
