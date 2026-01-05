"""
PersonCorporateContract Repository

개인-법인 계약 관리의 CRUD 및 기본 조회를 처리합니다.

Phase 3 구조화: repositories/contract/ 폴더로 이동
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import db
from app.models.person_contract import PersonCorporateContract, DataSharingSettings, SyncLog
from app.models.user import User
from app.models.employee import Employee
from app.models.personal_profile import PersonalProfile
from app.constants.status import EmployeeStatus, ContractStatus
from ..base_repository import BaseRepository


class PersonContractRepository(BaseRepository[PersonCorporateContract]):
    """개인-법인 계약 관리 Repository"""

    def __init__(self):
        super().__init__(PersonCorporateContract)

    # ===== 조회 메서드 =====

    def get_by_person_user_id(self, person_user_id: int) -> List[Dict]:
        """개인 사용자의 모든 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id
        ).order_by(PersonCorporateContract.created_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_by_company_id(self, company_id: int) -> List[Dict]:
        """기업의 모든 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            company_id=company_id
        ).order_by(PersonCorporateContract.created_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_active_contracts_by_person(self, person_user_id: int) -> List[Dict]:
        """개인의 활성 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_active_contracts_by_company(self, company_id: int) -> List[Dict]:
        """기업의 활성 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_pending_contracts_by_person(self, person_user_id: int) -> List[Dict]:
        """개인에게 온 대기 중 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            status=PersonCorporateContract.STATUS_REQUESTED
        ).order_by(PersonCorporateContract.requested_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_pending_contracts_by_company(self, company_id: int) -> List[Dict]:
        """기업에서 보낸 대기 중 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_REQUESTED
        ).order_by(PersonCorporateContract.requested_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def get_contract_between(self, person_user_id: int, company_id: int) -> Optional[Dict]:
        """특정 개인과 기업 간 계약 조회"""
        contract = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            company_id=company_id
        ).filter(
            PersonCorporateContract.status.in_([
                PersonCorporateContract.STATUS_REQUESTED,
                PersonCorporateContract.STATUS_APPROVED
            ])
        ).first()
        return contract.to_dict(include_relations=True) if contract else None

    def get_by_status(self, status: str) -> List[Dict]:
        """상태별 계약 조회"""
        contracts = PersonCorporateContract.query.filter_by(
            status=status
        ).order_by(PersonCorporateContract.created_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def find_by_id(self, contract_id: int) -> Optional[PersonCorporateContract]:
        """ID로 모델 조회 (모델 반환)"""
        return PersonCorporateContract.query.get(contract_id)

    # ===== 생성 메서드 =====

    def create_contract_request(
        self,
        person_user_id: int,
        company_id: int,
        requested_by: str = 'company',
        contract_type: str = 'employment',
        position: str = None,
        department: str = None,
        notes: str = None
    ) -> Dict:
        """계약 요청 생성"""
        # 기존 활성/대기 중 계약 확인
        existing = self.get_contract_between(person_user_id, company_id)
        if existing:
            raise ValueError("이미 계약이 존재하거나 대기 중입니다.")

        contract = PersonCorporateContract(
            person_user_id=person_user_id,
            company_id=company_id,
            status=PersonCorporateContract.STATUS_REQUESTED,
            contract_type=contract_type,
            requested_by=requested_by,
            position=position,
            department=department,
            notes=notes,
        )

        db.session.add(contract)
        db.session.commit()

        return contract.to_dict(include_relations=True)

    # ===== 데이터 공유 설정 =====

    def get_sharing_settings(self, contract_id: int) -> Optional[Dict]:
        """데이터 공유 설정 조회"""
        contract = self.find_by_id(contract_id)
        if not contract or not contract.data_sharing_settings:
            return None
        return contract.data_sharing_settings.to_dict()

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> Dict:
        """데이터 공유 설정 업데이트"""
        contract = self.find_by_id(contract_id)
        if not contract:
            raise ValueError("계약을 찾을 수 없습니다.")

        if not contract.data_sharing_settings:
            # 새로 생성
            sharing = DataSharingSettings(contract_id=contract_id)
            db.session.add(sharing)
        else:
            sharing = contract.data_sharing_settings

        # 설정 업데이트
        for key, value in settings.items():
            if hasattr(sharing, key):
                setattr(sharing, key, value)

        db.session.commit()

        return sharing.to_dict()

    # ===== 동기화 로그 =====

    def get_sync_logs(self, contract_id: int, limit: int = 50) -> List[Dict]:
        """동기화 로그 조회"""
        logs = SyncLog.query.filter_by(
            contract_id=contract_id
        ).order_by(SyncLog.executed_at.desc()).limit(limit).all()
        return [log.to_dict() for log in logs]

    def create_sync_log(
        self,
        contract_id: int,
        sync_type: str,
        entity_type: str,
        field_name: str = None,
        old_value: Any = None,
        new_value: Any = None,
        direction: str = None,
        user_id: int = None
    ) -> Dict:
        """동기화 로그 생성"""
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type=entity_type,
            field_name=field_name,
            old_value=old_value,
            new_value=new_value,
            direction=direction,
            user_id=user_id
        )
        db.session.add(log)
        db.session.commit()

        return log.to_dict()

    # ===== 통계 =====

    def get_statistics_by_company(self, company_id: int) -> Dict:
        """기업별 계약 통계"""
        total = PersonCorporateContract.query.filter_by(company_id=company_id).count()
        active = PersonCorporateContract.query.filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).count()
        pending = PersonCorporateContract.query.filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_REQUESTED
        ).count()
        terminated = PersonCorporateContract.query.filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_TERMINATED
        ).count()

        return {
            'total': total,
            EmployeeStatus.ACTIVE: active,
            'pending': pending,
            'terminated': terminated,
        }

    def get_statistics_by_person(self, person_user_id: int) -> Dict:
        """개인별 계약 통계"""
        total = PersonCorporateContract.query.filter_by(person_user_id=person_user_id).count()
        active = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).count()
        pending = PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            status=PersonCorporateContract.STATUS_REQUESTED
        ).count()

        return {
            'total': total,
            EmployeeStatus.ACTIVE: active,
            'pending': pending,
        }

    # ===== 검색 =====

    def search_contracts(
        self,
        company_id: int = None,
        person_user_id: int = None,
        status: str = None,
        contract_type: str = None,
        search_term: str = None
    ) -> List[Dict]:
        """계약 검색"""
        query = PersonCorporateContract.query

        if company_id:
            query = query.filter_by(company_id=company_id)
        if person_user_id:
            query = query.filter_by(person_user_id=person_user_id)
        if status:
            query = query.filter_by(status=status)
        if contract_type:
            query = query.filter_by(contract_type=contract_type)
        if search_term:
            search = f"%{search_term}%"
            query = query.filter(
                db.or_(
                    PersonCorporateContract.position.ilike(search),
                    PersonCorporateContract.department.ilike(search),
                    PersonCorporateContract.employee_number.ilike(search),
                )
            )

        contracts = query.order_by(PersonCorporateContract.created_at.desc()).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    # ===== 벌크 조회 메서드 (N+1 방지) =====

    def get_contracts_by_user_ids_bulk(
        self,
        user_ids: List[int],
        company_id: int
    ) -> Dict[int, PersonCorporateContract]:
        """N+1 방지: user_id 목록으로 계약 벌크 조회

        Args:
            user_ids: User ID 목록
            company_id: 회사 ID

        Returns:
            Dict[user_id, PersonCorporateContract]
        """
        if not user_ids or not company_id:
            return {}

        contracts = PersonCorporateContract.query.filter(
            PersonCorporateContract.person_user_id.in_(user_ids),
            PersonCorporateContract.company_id == company_id
        ).all()

        return {c.person_user_id: c for c in contracts}

    def get_approved_by_employee_numbers_bulk(
        self,
        employee_numbers: List[str],
        company_id: int
    ) -> Dict[str, PersonCorporateContract]:
        """N+1 방지: employee_number 목록으로 approved 계약 벌크 조회

        Args:
            employee_numbers: 직원번호 목록
            company_id: 회사 ID

        Returns:
            Dict[employee_number, PersonCorporateContract]
        """
        if not employee_numbers or not company_id:
            return {}

        # None 값 필터링
        valid_numbers = [n for n in employee_numbers if n]
        if not valid_numbers:
            return {}

        from sqlalchemy.orm import joinedload

        contracts = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.employee_number.in_(valid_numbers),
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status == PersonCorporateContract.STATUS_APPROVED
        ).all()

        return {c.employee_number: c for c in contracts if c.employee_number}

    def get_contract_for_employee(self, employee_id: int) -> Optional[PersonCorporateContract]:
        """직원의 활성 계약 조회

        employee_id를 가진 User의 계약 또는 employee_number 매칭으로 조회

        Args:
            employee_id: Employee.id

        Returns:
            PersonCorporateContract 또는 None
        """
        # 1. User.employee_id로 User 찾기
        user = User.query.filter_by(employee_id=employee_id).first()
        if user:
            contract = PersonCorporateContract.query.filter_by(
                person_user_id=user.id,
                status=PersonCorporateContract.STATUS_APPROVED
            ).first()
            if contract:
                return contract

        # 2. Employee.employee_number로 계약 찾기
        employee = Employee.query.get(employee_id)
        if employee and employee.employee_number and employee.company_id:
            contract = PersonCorporateContract.query.filter_by(
                employee_number=employee.employee_number,
                company_id=employee.company_id,
                status=PersonCorporateContract.STATUS_APPROVED
            ).first()
            if contract:
                return contract

        return None

    def get_by_employee_ids_bulk(
        self,
        employee_ids: List[int]
    ) -> Dict[int, PersonCorporateContract]:
        """N+1 방지: employee_id 목록으로 계약 벌크 조회

        User.employee_id를 통해 계약 조회

        Args:
            employee_ids: Employee ID 목록

        Returns:
            Dict[employee_id, PersonCorporateContract]
        """
        if not employee_ids:
            return {}

        from sqlalchemy.orm import joinedload

        # employee_id를 가진 User 목록 조회
        users = User.query.filter(User.employee_id.in_(employee_ids)).all()
        user_emp_map = {u.employee_id: u.id for u in users if u.employee_id}

        if not user_emp_map:
            return {}

        # User의 계약 조회
        contracts = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.person_user_id.in_(user_emp_map.values()),
            PersonCorporateContract.status == PersonCorporateContract.STATUS_APPROVED
        ).all()

        # user_id -> contract 매핑
        user_contract_map = {c.person_user_id: c for c in contracts}

        # employee_id -> contract 변환
        result = {}
        for emp_id, user_id in user_emp_map.items():
            if user_id in user_contract_map:
                result[emp_id] = user_contract_map[user_id]

        return result

    def get_active_contract_by_person_and_company(
        self,
        user_id: int,
        company_id: int
    ) -> Optional[PersonCorporateContract]:
        """특정 User와 회사 간의 활성 계약 조회

        Args:
            user_id: User.id
            company_id: Company.id

        Returns:
            PersonCorporateContract 또는 None
        """
        return PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).first()

    def get_approved_contracts_with_users(
        self,
        company_id: int
    ) -> List[PersonCorporateContract]:
        """회사의 승인된 계약 목록 조회 (User 포함)

        Args:
            company_id: 회사 ID

        Returns:
            PersonCorporateContract 목록 (person_user 로드됨)
        """
        from sqlalchemy.orm import joinedload

        return PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter_by(
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()

    def find_approved_contract_by_employee_number(
        self,
        employee_number: str,
        company_id: int
    ) -> Optional[PersonCorporateContract]:
        """직원번호와 회사ID로 승인된 계약 조회

        Args:
            employee_number: 직원번호
            company_id: 회사 ID

        Returns:
            PersonCorporateContract 또는 None
        """
        return PersonCorporateContract.query.filter_by(
            employee_number=employee_number,
            company_id=company_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).first()

    # ========================================
    # Phase 30: 레이어 분리용 추가 메서드
    # ========================================

    def count_all(self) -> int:
        """전체 계약 수 조회

        Returns:
            전체 계약 수
        """
        return PersonCorporateContract.query.count()

    def count_by_status(self, status: str) -> int:
        """상태별 계약 수 조회

        Args:
            status: 계약 상태

        Returns:
            계약 수
        """
        return PersonCorporateContract.query.filter_by(status=status).count()

    def find_viewable_by_person_user_id(
        self,
        person_user_id: int,
        include_terminated: bool = True
    ) -> List[PersonCorporateContract]:
        """열람 가능한 계약 목록 조회 (approved + terminated)

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            person_user_id: 개인 사용자 ID
            include_terminated: 종료된 계약 포함 여부

        Returns:
            PersonCorporateContract 목록
        """
        from app.constants.status import ContractStatus

        viewable_statuses = [ContractStatus.APPROVED]
        if include_terminated:
            viewable_statuses.append(ContractStatus.TERMINATED)

        return PersonCorporateContract.query.filter(
            PersonCorporateContract.person_user_id == person_user_id,
            PersonCorporateContract.status.in_(viewable_statuses)
        ).all()

    def find_viewable_by_id_and_person_user(
        self,
        contract_id: int,
        person_user_id: int
    ) -> Optional[PersonCorporateContract]:
        """ID와 사용자ID로 열람 가능한 계약 조회

        Phase 30: Service Layer 레이어 분리용 메서드

        Args:
            contract_id: 계약 ID
            person_user_id: 개인 사용자 ID

        Returns:
            PersonCorporateContract 또는 None
        """
        from app.constants.status import ContractStatus

        return PersonCorporateContract.query.filter(
            PersonCorporateContract.id == contract_id,
            PersonCorporateContract.person_user_id == person_user_id,
            PersonCorporateContract.status.in_([ContractStatus.APPROVED, ContractStatus.TERMINATED])
        ).first()

    def find_by_person_user_id_and_status(
        self,
        person_user_id: int,
        status: str
    ) -> List[PersonCorporateContract]:
        """개인 사용자 ID와 상태로 계약 목록 조회

        Phase 30: sync_service 레이어 분리용 메서드

        Args:
            person_user_id: 개인 사용자 ID
            status: 계약 상태 (ContractStatus 상수)

        Returns:
            PersonCorporateContract 목록
        """
        return PersonCorporateContract.query.filter_by(
            person_user_id=person_user_id,
            status=status
        ).all()

    def find_with_history(
        self,
        employee_number: str,
        company_id: int,
        history_statuses: List[str]
    ) -> Optional[PersonCorporateContract]:
        """계약 이력 조회 - 수정불가 필터용

        Phase 30: contract_core_service 레이어 분리용 메서드

        Args:
            employee_number: 직원번호
            company_id: 회사 ID
            history_statuses: 이력 상태 목록 (approved, terminated 등)

        Returns:
            PersonCorporateContract 또는 None
        """
        if not employee_number or not company_id:
            return None

        return PersonCorporateContract.query.filter(
            PersonCorporateContract.employee_number == employee_number,
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_(history_statuses)
        ).first()


    def find_filtered_contracts(
        self,
        company_id: int = None,
        person_user_id: int = None,
        statuses: List[str] = None
    ) -> List[PersonCorporateContract]:
        """통합 계약 필터링 (contract_filter_service용)

        Phase 30: contract_filter_service 레이어 분리용 메서드

        Args:
            company_id: 법인 ID (선택)
            person_user_id: 개인 사용자 ID (선택)
            statuses: 조회할 상태 리스트

        Returns:
            필터링된 계약 리스트
        """
        from sqlalchemy.orm import joinedload

        if statuses is None:
            statuses = [ContractStatus.APPROVED]

        query = PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.status.in_(statuses)
        )

        if company_id:
            query = query.filter(PersonCorporateContract.company_id == company_id)
        if person_user_id:
            query = query.filter(PersonCorporateContract.person_user_id == person_user_id)

        return query.all()

    def find_by_employee_numbers_and_company(
        self,
        employee_numbers: List[str],
        company_id: int,
        statuses: List[str] = None
    ) -> List[PersonCorporateContract]:
        """employee_number 목록으로 계약 벌크 조회

        Phase 30: contract_filter_service 레이어 분리용 메서드

        Args:
            employee_numbers: 직원번호 목록
            company_id: 법인 ID
            statuses: 조회할 상태 리스트

        Returns:
            계약 리스트
        """
        from sqlalchemy.orm import joinedload

        if not employee_numbers or not company_id:
            return []

        valid_numbers = [n for n in employee_numbers if n]
        if not valid_numbers:
            return []

        if statuses is None:
            statuses = [ContractStatus.APPROVED]

        return PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.employee_number.in_(valid_numbers),
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_(statuses)
        ).all()

    def find_by_user_ids_and_company(
        self,
        user_ids: List[int],
        company_id: int,
        statuses: List[str] = None
    ) -> List[PersonCorporateContract]:
        """user_id 목록으로 계약 벌크 조회

        Phase 30: contract_filter_service 레이어 분리용 메서드

        Args:
            user_ids: User ID 목록
            company_id: 법인 ID
            statuses: 조회할 상태 리스트

        Returns:
            계약 리스트
        """
        from sqlalchemy.orm import joinedload

        if not user_ids or not company_id:
            return []

        if statuses is None:
            statuses = [ContractStatus.APPROVED]

        return PersonCorporateContract.query.options(
            joinedload(PersonCorporateContract.person_user)
        ).filter(
            PersonCorporateContract.person_user_id.in_(user_ids),
            PersonCorporateContract.company_id == company_id,
            PersonCorporateContract.status.in_(statuses)
        ).all()

    def find_active_by_user_and_company(
        self,
        user_id: int,
        company_id: int
    ) -> Optional[PersonCorporateContract]:
        """특정 User와 회사 간 활성 계약 조회

        Phase 30: contract_filter_service 레이어 분리용 메서드

        Args:
            user_id: User ID
            company_id: 법인 ID

        Returns:
            계약 또는 None
        """
        return PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            company_id=company_id,
            status=ContractStatus.APPROVED
        ).first()

    def find_terminated_contracts(
        self,
        company_id: int = None,
        person_user_id: int = None,
        limit: int = None
    ) -> List[PersonCorporateContract]:
        """종료된 계약 이력 조회

        Phase 30: termination_service 레이어 분리용 메서드

        Args:
            company_id: 법인 ID (선택)
            person_user_id: 개인 사용자 ID (선택)
            limit: 조회 제한

        Returns:
            종료된 계약 목록
        """
        query = PersonCorporateContract.query.filter(
            PersonCorporateContract.status == ContractStatus.TERMINATED
        )

        if company_id:
            query = query.filter_by(company_id=company_id)
        if person_user_id:
            query = query.filter_by(person_user_id=person_user_id)

        query = query.order_by(PersonCorporateContract.terminated_at.desc())

        if limit:
            query = query.limit(limit)

        return query.all()

    def find_archivable_contracts(
        self,
        cutoff_date
    ) -> List[PersonCorporateContract]:
        """아카이브 대상 계약 조회 (종료 후 일정 기간 경과)

        Phase 30: termination_service 레이어 분리용 메서드

        Args:
            cutoff_date: 기준일 (이 날짜 이전에 종료된 계약)

        Returns:
            아카이브 대상 계약 목록
        """
        return PersonCorporateContract.query.filter(
            PersonCorporateContract.status == ContractStatus.TERMINATED,
            PersonCorporateContract.terminated_at <= cutoff_date
        ).all()


# 싱글톤 인스턴스
person_contract_repository = PersonContractRepository()
