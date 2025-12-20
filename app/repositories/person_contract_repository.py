"""
PersonCorporateContract Repository

개인-법인 계약 관리의 CRUD 및 비즈니스 로직을 처리합니다.
"""
from typing import List, Optional, Dict, Any
from datetime import datetime
from app.database import db
from app.models.person_contract import PersonCorporateContract, DataSharingSettings, SyncLog
from app.models.user import User
from app.models.employee import Employee
from .base_repository import BaseRepository


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

    def get_model_by_id(self, contract_id: int) -> Optional[PersonCorporateContract]:
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

    # ===== 승인/거절/종료 메서드 =====

    def approve_contract(self, contract_id: int, approved_by_user_id: int = None) -> Dict:
        """계약 승인

        21번 원칙: 계약 승인 시 Employee.status = 'active' 연동
        """
        contract = self.get_model_by_id(contract_id)
        if not contract:
            raise ValueError("계약을 찾을 수 없습니다.")

        contract.approve(approved_by_user_id)

        # Employee.status 연동: 계약 승인 시 active로 변경
        user = User.query.get(contract.person_user_id)
        if user and user.employee_id:
            employee = db.session.get(Employee, user.employee_id)
            if employee:
                employee.status = 'active'

        db.session.commit()

        return contract.to_dict(include_relations=True)

    def reject_contract(self, contract_id: int, rejected_by_user_id: int = None, reason: str = None) -> Dict:
        """계약 거절"""
        contract = self.get_model_by_id(contract_id)
        if not contract:
            raise ValueError("계약을 찾을 수 없습니다.")

        contract.reject(rejected_by_user_id, reason)
        db.session.commit()

        return contract.to_dict(include_relations=True)

    def terminate_contract(self, contract_id: int, terminated_by_user_id: int = None, reason: str = None) -> Dict:
        """계약 종료

        21번 원칙: 계약 종료 시 Employee.status = 'inactive' 연동
        """
        contract = self.get_model_by_id(contract_id)
        if not contract:
            raise ValueError("계약을 찾을 수 없습니다.")

        contract.terminate(terminated_by_user_id, reason)

        # Employee.status 연동: 계약 종료 시 inactive로 변경
        user = User.query.get(contract.person_user_id)
        if user and user.employee_id:
            employee = db.session.get(Employee, user.employee_id)
            if employee:
                employee.status = 'inactive'

        db.session.commit()

        return contract.to_dict(include_relations=True)

    # ===== 데이터 공유 설정 =====

    def get_sharing_settings(self, contract_id: int) -> Optional[Dict]:
        """데이터 공유 설정 조회"""
        contract = self.get_model_by_id(contract_id)
        if not contract or not contract.data_sharing_settings:
            return None
        return contract.data_sharing_settings.to_dict()

    def update_sharing_settings(self, contract_id: int, settings: Dict) -> Dict:
        """데이터 공유 설정 업데이트"""
        contract = self.get_model_by_id(contract_id)
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
            'active': active,
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
            'active': active,
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
