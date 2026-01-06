"""
Employee Repository

직원 데이터의 CRUD 및 검색 기능을 제공합니다.

Phase 28.2: Repository 레벨 필드 보호 추가
- organization_id, company_id 등 핵심 필드 보호
- update/update_partial 시 의도치 않은 덮어쓰기 방지
"""
from typing import List, Optional, Dict, Set
from app.database import db
from app.models import Employee
from app.constants.status import EmployeeStatus
from .base_repository import BaseRepository
from .mixins import TenantFilterMixin


# ========================================
# Repository 레벨 보호 필드 (Phase 28.2)
# ========================================
# update/update_partial 시 덮어쓰기 방지
# 이 필드들은 생성 시에만 설정되거나, 명시적 API로만 변경 가능
PROTECTED_FIELDS: Set[str] = {
    'id',                # PK는 변경 불가
    'company_id',        # 회사 소속은 변경 불가
    'organization_id',   # 조직 소속은 폼에서 disabled로 전송 안됨 -> None 덮어쓰기 방지
    'employee_number',   # 사번은 시스템 생성
    'profile_id',        # 프로필 연결은 계약으로만 변경
    # 관계 객체 보호 (SQLAlchemy 관계 설정 시 FK도 변경됨)
    'organization',      # organization=None 설정 시 organization_id=None 됨
    'profile',           # profile=None 설정 시 profile_id=None 됨
    'company',           # company=None 설정 시 company_id=None 됨
}


class EmployeeRepository(BaseRepository[Employee], TenantFilterMixin):
    """직원 저장소 - 멀티테넌시 지원 (TenantFilterMixin)"""

    def __init__(self):
        super().__init__(Employee)

    # ========================================
    # 멀티테넌시 헬퍼 메서드
    # ========================================

    def _build_query(self, organization_id: int = None):
        """organization_id 필터가 적용된 기본 쿼리 생성

        루트 조직과 모든 하위 조직의 직원을 포함합니다.

        Args:
            organization_id: 루트 조직 ID (None이면 필터 미적용)

        Returns:
            SQLAlchemy Query 객체
        """
        query = Employee.query
        if organization_id:
            # TenantFilterMixin 사용
            query = self.apply_tenant_filter(query, Employee.organization_id, organization_id)
        return query

    def _get_organization_ids_under_root(self, root_org_id: int) -> List[int]:
        """루트 조직과 모든 하위 조직의 ID 목록 반환

        [DEPRECATED] TenantFilterMixin.get_tenant_org_ids_list() 사용 권장

        Args:
            root_org_id: 루트 조직 ID

        Returns:
            조직 ID 목록 (루트 포함)
        """
        return self.get_tenant_org_ids_list(root_org_id)

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
        models = self.find_all(organization_id=company.root_organization_id)
        return [m.to_dict() for m in models]

    def verify_ownership(self, employee_id: int, root_organization_id: int) -> bool:
        """직원이 해당 조직 계층에 속하는지 확인

        Args:
            employee_id: 직원 ID
            root_organization_id: 루트 조직 ID (회사의 root_organization_id)

        Returns:
            소속 여부 (True/False) - 직원의 organization이 root 아래 계층에 있으면 True
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return False
        if not employee.organization_id:
            return False
        # 조직 계층 구조를 고려하여 검증
        from .organization_repository import OrganizationRepository
        org_repo = OrganizationRepository()
        return org_repo.verify_ownership(employee.organization_id, root_organization_id)

    # ========================================
    # CRUD 메서드
    # ========================================

    def find_all(self, organization_id: int = None) -> List[Employee]:
        """모든 직원 조회 (Model 반환 - 신규 표준)

        Args:
            organization_id: 조직 ID (None이면 전체 조회)

        Returns:
            Employee 모델 객체 리스트
        """
        query = self._build_query(organization_id)
        return query.order_by(Employee.id).all()

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
        """직원 정보 수정

        Phase 28.2: PROTECTED_FIELDS 보호 적용
        - organization_id, company_id 등 핵심 필드는 업데이트에서 제외
        - 의도치 않은 None 덮어쓰기 방지
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return None

        # 데이터 업데이트 (보호 필드 제외)
        for key, value in data.items():
            snake_key = self._camel_to_snake(key)
            # Phase 28.2: 보호 필드는 스킵
            if snake_key in PROTECTED_FIELDS:
                continue
            if hasattr(employee, snake_key):
                setattr(employee, snake_key, value)

        db.session.commit()
        return employee.to_dict()

    def update_partial(self, employee_id: str, data: Dict) -> Optional[Dict]:
        """직원 정보 부분 수정 (지정된 필드만 업데이트)

        Phase 28.2: PROTECTED_FIELDS 보호 적용
        - organization_id, company_id 등 핵심 필드는 업데이트에서 제외
        - 의도치 않은 None 덮어쓰기 방지
        """
        employee = Employee.query.get(employee_id)
        if not employee:
            return None

        # 지정된 필드만 업데이트 (보호 필드 제외)
        for key, value in data.items():
            # Phase 28.2: 보호 필드는 스킵
            if key in PROTECTED_FIELDS:
                continue
            if hasattr(employee, key):
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
            models = self.find_all(organization_id=organization_id)
            return [m.to_dict() for m in models]

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
        active = self._build_query(organization_id).filter_by(status=EmployeeStatus.ACTIVE).count()
        on_leave = self._build_query(organization_id).filter_by(status='on_leave').count()
        resigned = self._build_query(organization_id).filter_by(status=EmployeeStatus.RESIGNED).count()

        return {
            'total': total,
            EmployeeStatus.ACTIVE: active,
            'onLeave': on_leave,
            EmployeeStatus.RESIGNED: resigned
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
                         search: str = None, sort_by: str = None, sort_order: str = 'asc',
                         organization_id: int = None) -> List[Dict]:
        """다중 필터링 및 정렬

        Args:
            department: 단일 부서 필터
            position: 단일 직급 필터
            status: 단일 상태 필터
            departments: 복수 부서 필터
            positions: 복수 직급 필터
            statuses: 복수 상태 필터
            search: 검색어 (이름, 부서, 직급)
            sort_by: 정렬 기준 컬럼
            sort_order: 정렬 순서 (asc/desc)
            organization_id: 조직 ID (None이면 전체 조회)
        """
        from sqlalchemy import or_
        query = self._build_query(organization_id)

        # 검색어 필터 (이름, 부서, 직급)
        if search:
            search_pattern = f'%{search}%'
            query = query.filter(or_(
                Employee.name.ilike(search_pattern),
                Employee.department.ilike(search_pattern),
                Employee.position.ilike(search_pattern)
            ))

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

    # ========================================
    # Phase 30: 레이어 분리용 추가 메서드
    # ========================================

    def find_by_employee_number(self, employee_number: str) -> Optional[Employee]:
        """사번으로 직원 조회

        Args:
            employee_number: 직원 사번

        Returns:
            Employee 모델 객체 또는 None
        """
        return Employee.query.filter_by(employee_number=employee_number).first()

    def find_by_employee_number_and_company(
        self,
        employee_number: str,
        company_id: int
    ) -> Optional[Employee]:
        """사번과 회사 ID로 직원 조회

        Args:
            employee_number: 직원 사번
            company_id: 회사 ID

        Returns:
            Employee 모델 객체 또는 None
        """
        return Employee.query.filter_by(
            employee_number=employee_number,
            company_id=company_id
        ).first()

    def count_by_company_id(self, company_id: int) -> int:
        """회사별 직원 수 조회

        Args:
            company_id: 회사 ID

        Returns:
            직원 수
        """
        from app.models.company import Company
        company = Company.query.get(company_id)
        if not company or not company.root_organization_id:
            return 0
        return self._build_query(company.root_organization_id).count()

    def count_by_status_and_company(
        self,
        status: str,
        company_id: int
    ) -> int:
        """상태와 회사 ID로 직원 수 조회

        Args:
            status: 재직 상태
            company_id: 회사 ID

        Returns:
            직원 수
        """
        from app.models.company import Company
        company = Company.query.get(company_id)
        if not company or not company.root_organization_id:
            return 0
        return self._build_query(company.root_organization_id).filter_by(status=status).count()

    def find_by_company_id(self, company_id: int) -> List[Employee]:
        """회사 ID로 직원 목록 조회 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드
        - get_by_company()는 Dict 반환, 이 메서드는 Model 반환

        Args:
            company_id: 회사 ID

        Returns:
            Employee 모델 객체 리스트
        """
        from app.models.company import Company
        company = Company.query.get(company_id)
        if not company or not company.root_organization_id:
            return []
        return self._build_query(company.root_organization_id).all()

    def find_by_id(self, employee_id: int) -> Optional[Employee]:
        """ID로 직원 조회 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            employee_id: 직원 ID

        Returns:
            Employee 모델 객체 또는 None
        """
        return Employee.query.get(employee_id)

    def create_from_model(
        self,
        employee: 'Employee',
        flush: bool = False,
        commit: bool = False
    ) -> 'Employee':
        """Employee 모델 객체를 DB에 추가

        Phase 30: sync_service 레이어 분리용 메서드
        - 이미 생성된 Employee 객체를 세션에 추가
        - flush=True로 ID 할당 가능

        Args:
            employee: Employee 모델 객체
            flush: True면 flush 실행 (ID 할당)
            commit: True면 commit 실행

        Returns:
            추가된 Employee 모델 객체
        """
        db.session.add(employee)
        if flush:
            db.session.flush()
        if commit:
            db.session.commit()
        return employee

    def find_by_company_and_statuses(
        self,
        company_id: int,
        statuses: List[str]
    ) -> List[Employee]:
        """회사 ID와 복수 상태로 직원 목록 조회

        Phase 30: contract_core_service 레이어 분리용 메서드

        Args:
            company_id: 회사 ID
            statuses: 상태 목록 ['pending_info', 'pending_contract', ...]

        Returns:
            Employee 모델 객체 리스트
        """
        return Employee.query.filter(
            Employee.company_id == company_id,
            Employee.status.in_(statuses)
        ).all()

    def find_by_company_and_employee_numbers(
        self,
        company_id: int,
        employee_numbers: List[str]
    ) -> List[Employee]:
        """회사 ID와 복수 사번으로 직원 목록 조회

        Phase 30: user_employee_link_service 레이어 분리용 메서드

        Args:
            company_id: 회사 ID
            employee_numbers: 사번 목록

        Returns:
            Employee 모델 객체 리스트
        """
        if not employee_numbers:
            return []
        return Employee.query.filter(
            Employee.company_id == company_id,
            Employee.employee_number.in_(employee_numbers)
        ).all()

    def find_by_company_and_emails(
        self,
        company_id: int,
        emails: List[str]
    ) -> List[Employee]:
        """회사 ID와 복수 이메일로 직원 목록 조회

        Phase 30: user_employee_link_service 레이어 분리용 메서드

        Args:
            company_id: 회사 ID
            emails: 이메일 목록

        Returns:
            Employee 모델 객체 리스트
        """
        if not emails:
            return []
        return Employee.query.filter(
            Employee.company_id == company_id,
            Employee.email.in_(emails)
        ).all()

    def find_by_company_ids(self, company_ids: List[int]) -> List[Employee]:
        """복수 회사 ID로 직원 목록 조회

        Phase 30: user_employee_link_service 레이어 분리용 메서드

        Args:
            company_ids: 회사 ID 목록

        Returns:
            Employee 모델 객체 리스트
        """
        if not company_ids:
            return []
        return Employee.query.filter(Employee.company_id.in_(company_ids)).all()

    # ========================================
    # Phase 31: 컨벤션 준수용 추가 메서드
    # ========================================

    def find_last_by_number_pattern(self, pattern: str) -> Optional[Employee]:
        """패턴으로 마지막 사번 직원 조회 (사번 생성용)

        Phase 31: employee_number.py 컨벤션 준수

        Args:
            pattern: LIKE 패턴 (예: 'EMP-2025-%')

        Returns:
            Employee 모델 객체 또는 None
        """
        return (
            Employee.query
            .filter(Employee.employee_number.like(pattern))
            .order_by(Employee.employee_number.desc())
            .first()
        )

    def exists_by_employee_number(
        self,
        employee_number: str,
        exclude_id: int = None
    ) -> bool:
        """사번 존재 여부 확인

        Phase 31: employee_number.py 컨벤션 준수

        Args:
            employee_number: 확인할 사번
            exclude_id: 제외할 직원 ID (수정 시 사용)

        Returns:
            존재 여부
        """
        query = Employee.query.filter(Employee.employee_number == employee_number)
        if exclude_id:
            query = query.filter(Employee.id != exclude_id)
        return query.first() is not None


# 싱글톤 인스턴스
employee_repository = EmployeeRepository()
