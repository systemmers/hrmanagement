"""
Company Repository

법인(기업) 데이터 관리 Repository입니다.

Phase 7: 도메인 중심 마이그레이션 완료
"""
from typing import List, Optional, Dict
from app.database import db
from app.domains.company.models import Company
from app.shared.repositories.base_repository import BaseRepository


class CompanyRepository(BaseRepository[Company]):
    """법인(기업) Repository"""

    def __init__(self):
        super().__init__(Company)

    def get_by_business_number(self, business_number: str) -> Optional[Dict]:
        """사업자등록번호로 법인 조회"""
        # 하이픈 제거 후 검색
        clean_number = business_number.replace('-', '')
        company = Company.query.filter_by(business_number=clean_number).first()
        return company.to_dict() if company else None

    def get_by_name(self, name: str) -> List[Dict]:
        """법인명으로 검색 (부분 일치)"""
        companies = Company.query.filter(
            Company.name.ilike(f'%{name}%')
        ).all()
        return [company.to_dict() for company in companies]

    def get_active_companies(self) -> List[Dict]:
        """활성화된 법인 목록 조회"""
        companies = Company.query.filter_by(is_active=True).all()
        return [company.to_dict() for company in companies]

    def get_verified_companies(self) -> List[Dict]:
        """인증된 법인 목록 조회"""
        companies = Company.query.filter_by(
            is_active=True,
            is_verified=True
        ).all()
        return [company.to_dict() for company in companies]

    def get_by_plan_type(self, plan_type: str) -> List[Dict]:
        """플랜 유형별 법인 목록 조회"""
        companies = Company.query.filter_by(
            plan_type=plan_type,
            is_active=True
        ).all()
        return [company.to_dict() for company in companies]

    def create_with_organization(self, data: Dict, organization_data: Dict = None) -> Dict:
        """
        법인 생성 및 조직 연결

        Args:
            data: 법인 정보 딕셔너리
            organization_data: 루트 조직 정보 (선택)

        Returns:
            생성된 법인 딕셔너리
        """
        # 사업자등록번호 정규화 (하이픈 제거)
        if data.get('business_number'):
            data['business_number'] = data['business_number'].replace('-', '')

        company = Company.from_dict(data)
        db.session.add(company)

        # 루트 조직 생성이 필요한 경우
        if organization_data:
            from app.domains.company.models import Organization

            # 루트 조직 생성
            root_org = Organization(
                name=organization_data.get('name', company.name),
                code=organization_data.get('code'),
                org_type=Organization.TYPE_COMPANY,
                parent_id=None,
                is_active=True,
                description=f'{company.name} 루트 조직'
            )
            db.session.add(root_org)
            db.session.flush()  # ID 생성

            company.root_organization_id = root_org.id

        db.session.commit()
        return company.to_dict()

    def verify_company(self, company_id: int) -> Optional[Dict]:
        """법인 인증 처리"""
        company = Company.query.get(company_id)
        if not company:
            return None

        company.verify()
        db.session.commit()
        return company.to_dict()

    def update_plan(self, company_id: int, plan_type: str, max_employees: int = None) -> Optional[Dict]:
        """법인 플랜 변경"""
        company = Company.query.get(company_id)
        if not company:
            return None

        if plan_type not in Company.VALID_PLANS:
            raise ValueError(f"유효하지 않은 플랜 유형: {plan_type}")

        company.plan_type = plan_type
        if max_employees is not None:
            company.max_employees = max_employees
        else:
            company.max_employees = Company.PLAN_MAX_EMPLOYEES.get(plan_type, 10)

        db.session.commit()
        return company.to_dict()

    def deactivate(self, company_id: int) -> bool:
        """법인 비활성화"""
        company = Company.query.get(company_id)
        if not company:
            return False

        company.is_active = False
        db.session.commit()
        return True

    def activate(self, company_id: int) -> bool:
        """법인 활성화"""
        company = Company.query.get(company_id)
        if not company:
            return False

        company.is_active = True
        db.session.commit()
        return True

    def get_with_stats(self, company_id: int) -> Optional[Dict]:
        """통계 정보 포함 법인 조회"""
        company = Company.query.get(company_id)
        if not company:
            return None
        return company.to_dict(include_stats=True)

    def search(
        self,
        query: str = None,
        plan_type: str = None,
        is_verified: bool = None,
        is_active: bool = True,
        page: int = 1,
        per_page: int = 20
    ) -> Dict:
        """
        법인 검색 (페이징 지원)

        Args:
            query: 검색어 (법인명, 사업자번호)
            plan_type: 플랜 유형 필터
            is_verified: 인증 상태 필터
            is_active: 활성화 상태 필터
            page: 페이지 번호
            per_page: 페이지당 결과 수

        Returns:
            검색 결과 및 페이징 정보
        """
        q = Company.query

        if is_active is not None:
            q = q.filter_by(is_active=is_active)

        if is_verified is not None:
            q = q.filter_by(is_verified=is_verified)

        if plan_type:
            q = q.filter_by(plan_type=plan_type)

        if query:
            search_term = f'%{query}%'
            q = q.filter(
                db.or_(
                    Company.name.ilike(search_term),
                    Company.business_number.ilike(search_term.replace('-', '')),
                    Company.representative.ilike(search_term)
                )
            )

        # 정렬: 최신 생성순
        q = q.order_by(Company.created_at.desc())

        # 페이징
        pagination = q.paginate(page=page, per_page=per_page, error_out=False)

        return {
            'items': [company.to_dict() for company in pagination.items],
            'total': pagination.total,
            'page': pagination.page,
            'per_page': pagination.per_page,
            'pages': pagination.pages,
            'has_next': pagination.has_next,
            'has_prev': pagination.has_prev
        }

    def exists_by_business_number(self, business_number: str) -> bool:
        """사업자등록번호 중복 확인"""
        clean_number = business_number.replace('-', '')
        return Company.query.filter_by(business_number=clean_number).first() is not None

    # ========================================
    # Phase 30: 레이어 분리용 추가 메서드
    # ========================================

    def count_all(self) -> int:
        """전체 법인 수 조회

        Returns:
            전체 법인 수
        """
        return Company.query.count()

    def count_active(self) -> int:
        """활성화된 법인 수 조회

        Returns:
            활성 법인 수
        """
        return Company.query.filter_by(is_active=True).count()

    def count_by_plan_type(self, plan_type: str) -> int:
        """플랜 유형별 법인 수 조회

        Args:
            plan_type: 플랜 유형

        Returns:
            법인 수
        """
        return Company.query.filter_by(plan_type=plan_type, is_active=True).count()

    def find_by_id(self, company_id: int) -> Optional[Company]:
        """ID로 법인 조회 (Model 반환)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            company_id: 법인 ID

        Returns:
            Company 모델 객체 또는 None
        """
        return Company.query.get(company_id)

    def find_paginated(
        self,
        page: int = 1,
        per_page: int = 20,
        search: str = None
    ) -> tuple:
        """법인 목록 조회 (페이지네이션)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            page: 페이지 번호
            per_page: 페이지당 항목 수
            search: 검색어 (name/business_number)

        Returns:
            Tuple[Company 모델 리스트, 페이지네이션 객체]
        """
        query = Company.query

        if search:
            query = query.filter(
                db.or_(
                    Company.name.ilike(f'%{search}%'),
                    Company.business_number.ilike(f'%{search}%')
                )
            )

        pagination = query.order_by(Company.created_at.desc()).paginate(
            page=page, per_page=per_page, error_out=False
        )

        return pagination.items, pagination

    def find_recent(self, limit: int = 5) -> List[Company]:
        """최근 등록 법인 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            limit: 조회 제한 (기본 5)

        Returns:
            Company 모델 리스트
        """
        return Company.query.order_by(Company.created_at.desc()).limit(limit).all()


# 싱글톤 인스턴스
company_repository = CompanyRepository()
