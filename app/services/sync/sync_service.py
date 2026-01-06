"""
데이터 동기화 서비스 (Facade)

개인(PersonalProfile) <-> 법인(Employee) 간 데이터 동기화를 처리합니다.
서브 서비스들을 조합하여 통합 인터페이스를 제공합니다.

Phase 4: 데이터 동기화 및 퇴사 처리
Phase 5: 구조화 - sync/ 폴더로 이동
Phase 30: 레이어 분리 - Model.query 제거, Repository 패턴 적용
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.domains.employee.models import Employee
from app.models import SyncLog, PersonCorporateContract
from app.models import PersonalProfile
from app.shared.utils.transaction import atomic_transaction

# 서브 서비스 임포트 (같은 패키지 내)
from .sync_basic_service import SyncBasicService
from .sync_relation_service import SyncRelationService

# 필드 매핑 SSOT (Phase 4: 중앙화)
from app.shared.constants.sync_fields import SYNC_MAPPINGS
from app.shared.constants.status import ContractStatus


class SyncService:
    """
    개인-법인 데이터 동기화 서비스 (Facade)

    주요 기능:
    - 개인 -> 법인 동기화 (개인정보 변경 시)
    - 법인 -> 개인 동기화 (선택적, 법인 정보 수정 시)
    - 1회성 데이터 제공 (스냅샷)
    - 동기화 로그 기록

    필드 매핑은 constants/sync_fields.py에서 중앙 관리합니다.

    Phase 30: 레이어 분리 - Repository DI 패턴 적용
    """

    def __init__(self):
        self._current_user_id = None
        self._basic_service = SyncBasicService()
        self._relation_service = SyncRelationService()
        # Repository 지연 초기화용
        self._data_sharing_repo = None
        self._contract_repo = None
        self._profile_repo = None
        self._company_repo = None
        self._employee_repo = None

    # ========================================
    # Repository Properties (지연 초기화)
    # ========================================

    @property
    def data_sharing_repo(self):
        """지연 초기화된 DataSharingSettings Repository"""
        if self._data_sharing_repo is None:
            from app.repositories.data_sharing_settings_repository import data_sharing_settings_repository
            self._data_sharing_repo = data_sharing_settings_repository
        return self._data_sharing_repo

    @property
    def contract_repo(self):
        """지연 초기화된 계약 Repository"""
        if self._contract_repo is None:
            from app.repositories.contract.person_contract_repository import person_contract_repository
            self._contract_repo = person_contract_repository
        return self._contract_repo

    @property
    def profile_repo(self):
        """지연 초기화된 프로필 Repository"""
        if self._profile_repo is None:
            from app.domains.employee.repositories import profile_repository
            self._profile_repo = profile_repository
        return self._profile_repo

    @property
    def company_repo(self):
        """지연 초기화된 법인 Repository"""
        if self._company_repo is None:
            from app.repositories.company_repository import company_repository
            self._company_repo = company_repository
        return self._company_repo

    @property
    def employee_repo(self):
        """지연 초기화된 직원 Repository"""
        if self._employee_repo is None:
            from app.domains.employee.repositories import employee_repository
            self._employee_repo = employee_repository
        return self._employee_repo

    @property
    def personal_profile_repo(self):
        """지연 초기화된 PersonalProfile Repository"""
        if not hasattr(self, '_personal_profile_repo') or self._personal_profile_repo is None:
            from app.repositories.personal_profile_repository import personal_profile_repository
            self._personal_profile_repo = personal_profile_repository
        return self._personal_profile_repo

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정 (로그 기록용)"""
        self._current_user_id = user_id
        self._basic_service.set_current_user(user_id)
        self._relation_service.set_current_user(user_id)

    # ===== 필드 조회 메서드 =====

    def get_syncable_fields(self, contract_id: int) -> Dict[str, List[str]]:
        """
        계약의 데이터 공유 설정에 따른 동기화 가능 필드 목록 조회

        Phase 30: Repository 패턴 적용

        Returns:
            {
                'basic': ['name', 'photo', ...],
                'contact': ['mobile_phone', 'email', ...],
                'education': True/False,
                'career': True/False,
                ...
            }
        """
        settings = self.data_sharing_repo.find_by_contract_id(contract_id)

        result = {
            'basic': [],
            'contact': [],
            'education': False,
            'career': False,
            'certificates': False,
            'languages': False,
            'military': False,
            'family': False,
        }

        if not settings:
            return result

        if settings.share_basic_info:
            result['basic'] = SYNC_MAPPINGS.get_basic_field_names()

        if settings.share_contact:
            result['contact'] = SYNC_MAPPINGS.get_contact_field_names()

        if settings.share_education:
            result['education'] = True

        if settings.share_career:
            result['career'] = True

        if settings.share_certificates:
            result['certificates'] = True

        if settings.share_languages:
            result['languages'] = True

        if settings.share_military:
            result['military'] = True

        # family: share_contact가 True면 가족정보도 동기화 (비상연락처/부양가족)
        if settings.share_contact:
            result['family'] = True

        return result

    def get_all_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """모든 필드 매핑 정보 반환"""
        return {
            'basic': SYNC_MAPPINGS.basic,
            'contact': SYNC_MAPPINGS.contact,
            'extra': SYNC_MAPPINGS.extra,
        }

    # ===== 동기화 메서드 =====

    def sync_personal_to_employee(
        self,
        contract_id: int,
        fields: Optional[List[str]] = None,
        sync_type: str = SyncLog.SYNC_TYPE_AUTO,
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        개인 프로필 -> 법인 직원 데이터 동기화

        Phase 30: Repository 패턴 적용

        Args:
            contract_id: 계약 ID
            fields: 동기화할 필드 목록 (None이면 설정에 따라 자동)
            sync_type: 동기화 유형 (auto, manual, initial)
            commit: True면 commit 실행, False면 외부 트랜잭션에 위임 (Phase 30)

        Returns:
            동기화 결과
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != ContractStatus.APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        personal_profile = self.personal_profile_repo.find_by_user_id(
            contract.person_user_id
        )
        if not personal_profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        # 관계 데이터용 Profile 조회 (educations, careers 등)
        profile = self.profile_repo.get_by_user_id(contract.person_user_id)

        employee = self._find_or_create_employee(contract, personal_profile)
        if not employee:
            return {'success': False, 'error': '직원 데이터를 생성/조회할 수 없습니다.'}

        syncable = self.get_syncable_fields(contract_id)
        target_fields = fields if fields else syncable['basic'] + syncable['contact']

        # 기본 필드 동기화 (PersonalProfile에서)
        basic_result = self._basic_service.sync_personal_to_employee(
            contract_id, personal_profile, employee, target_fields,
            self._get_employee_field, sync_type
        )

        # 관계 데이터 동기화 (Profile에서, Profile이 있는 경우에만)
        if profile:
            relation_result = self._relation_service.sync_relations(
                contract_id, profile, employee, syncable, sync_type
            )
        else:
            relation_result = {'synced_relations': [], 'changes': [], 'log_ids': []}

        if commit:
            from app.database import db
            db.session.commit()

        return {
            'success': True,
            'synced_fields': basic_result['synced_fields'],
            'changes': basic_result['changes'] + relation_result['changes'],
            'logs': basic_result['log_ids'] + relation_result['log_ids'],
            'relations': relation_result['synced_relations']
        }

    def sync_employee_to_personal(
        self,
        contract_id: int,
        fields: Optional[List[str]] = None,
        sync_type: str = SyncLog.SYNC_TYPE_MANUAL,
        commit: bool = True
    ) -> Dict[str, Any]:
        """
        법인 직원 -> 개인 프로필 데이터 동기화 (역방향, 선택적)

        Phase 30: Repository 패턴 적용

        Args:
            contract_id: 계약 ID
            fields: 동기화할 필드 목록 (None이면 설정에 따라 자동)
            sync_type: 동기화 유형 (auto, manual, initial)
            commit: True면 commit 실행, False면 외부 트랜잭션에 위임 (Phase 30)
        """
        contract = self.contract_repo.find_by_id(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != ContractStatus.APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        profile = self.personal_profile_repo.find_by_user_id(
            contract.person_user_id
        )
        if not profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        employee = self._find_employee_by_contract(contract)
        if not employee:
            return {'success': False, 'error': '연결된 직원을 찾을 수 없습니다.'}

        syncable = self.get_syncable_fields(contract_id)
        target_fields = fields if fields else syncable['basic'] + syncable['contact']

        result = self._basic_service.sync_employee_to_personal(
            contract_id, profile, employee, target_fields,
            self._get_employee_field, sync_type
        )

        if commit:
            from app.database import db
            db.session.commit()

        return {
            'success': True,
            'synced_fields': result['synced_fields'],
            'changes': result['changes'],
            'logs': result['log_ids'],
        }

    # ===== 실시간 동기화 지원 =====

    def should_auto_sync(self, contract_id: int) -> bool:
        """실시간 자동 동기화 여부 확인

        Phase 30: Repository 패턴 적용
        """
        return self.data_sharing_repo.is_realtime_sync_enabled(contract_id)

    def get_contracts_for_user(self, user_id: int) -> List[Dict]:
        """사용자의 활성 계약 목록 조회 (동기화 대상)

        Phase 30: Repository 패턴 적용
        """
        contracts = self.contract_repo.find_by_person_user_id_and_status(
            user_id, ContractStatus.APPROVED
        )
        return [c.to_dict(include_relations=True) for c in contracts]

    def sync_all_contracts_for_user(
        self,
        user_id: int,
        sync_type: str = SyncLog.SYNC_TYPE_AUTO
    ) -> Dict[str, Any]:
        """사용자의 모든 활성 계약에 대해 동기화 실행

        Phase 30: Repository 패턴 적용
        """
        contracts = self.contract_repo.find_by_person_user_id_and_status(
            user_id, ContractStatus.APPROVED
        )

        results = []
        for contract in contracts:
            if self.should_auto_sync(contract.id):
                result = self.sync_personal_to_employee(
                    contract.id, sync_type=sync_type
                )
                results.append({
                    'contract_id': contract.id,
                    'company_name': contract.company.name if contract.company else None,
                    'result': result
                })

        return {
            'success': True,
            'total_contracts': len(contracts),
            'synced_contracts': len(results),
            'results': results
        }

    # ===== Private 헬퍼 메서드 =====

    def _get_employee_field(self, profile_field: str) -> Optional[str]:
        """프로필 필드에 대응하는 Employee 필드명 반환"""
        return SYNC_MAPPINGS.map_field(profile_field)

    def _find_or_create_employee(
        self,
        contract: PersonCorporateContract,
        profile: PersonalProfile,
        full_sync: bool = False,
        force_create: bool = False  # deprecated: 항상 새로 생성
    ) -> Optional[Employee]:
        """계약 승인 시 새 직원 레코드 생성

        재입사 정책:
        - 재입사는 새로운 Employee 레코드로 생성
        - 동일 사번 재사용 불가 (새 사번 발급)
        - 퇴사 처리된 Employee는 재사용 불가
        - 이유: 4대보험 등 종료로 데이터 연속성 없음

        Args:
            contract: 계약 정보
            profile: 개인 프로필
            full_sync: True면 전체 프로필 데이터 동기화
            force_create: deprecated (항상 새로 생성)

        Returns:
            새 Employee 객체

        Phase 30: Repository 패턴 적용
        """
        from app.shared.utils.employee_number import generate_employee_number

        company = self.company_repo.find_by_id(contract.company_id)

        # [재입사 정책] 기존 Employee 탐색 로직 제거
        # 비즈니스 규칙: 퇴사 후 재입사는 새 Employee 레코드로 생성
        # 이유: 4대보험 등 종료로 데이터 연속성 없음

        # 새 Employee 생성
        employee = self._create_employee_from_profile(
            profile, contract, company, full_sync
        )
        # Phase 30: Repository 패턴 적용 - db.session.add/flush -> employee_repo.create_from_model
        self.employee_repo.create_from_model(employee, flush=True)

        # 새로운 사번 생성 (시퀀스 기반 - SSOT: employee_number.py)
        employee.employee_number = generate_employee_number()
        contract.employee_number = employee.employee_number

        return employee

    def _create_employee_from_profile(
        self,
        profile: PersonalProfile,
        contract: PersonCorporateContract,
        company,
        full_sync: bool = False
    ) -> Employee:
        """PersonalProfile에서 Employee 생성 (SSOT: FIELD_MAPPING 활용)

        Args:
            profile: 개인 프로필
            contract: 계약 정보 (department, position)
            company: 회사 정보 (root_organization_id)
            full_sync: 전체 필드 동기화 여부

        Returns:
            새 Employee 객체
        """
        # 기본 필수 필드
        employee_data = {
            'name': profile.name,
            'email': profile.email,
            'phone': profile.mobile_phone,
            'company_id': contract.company_id,  # 명시적 설정 (손실 방지)
            'organization_id': company.root_organization_id if company else None,
            'department': contract.department,
            'position': contract.position,
            'status': 'active',
            'hire_date': datetime.utcnow().strftime('%Y-%m-%d'),
        }

        if full_sync:
            # SSOT: SYNC_MAPPINGS 활용하여 전체 필드 복사
            all_mappings = SYNC_MAPPINGS.get_all_basic_fields()
            for profile_field, employee_field in all_mappings.items():
                value = getattr(profile, profile_field, None)
                if value is not None:
                    employee_data[employee_field] = value

        return Employee(**employee_data)

    def _find_employee_by_contract(
        self,
        contract
    ) -> Optional[Employee]:
        """계약에 연결된 직원 조회

        Phase 30: Repository 패턴 적용
        """
        if contract.employee_number:
            return self.employee_repo.find_by_employee_number(
                contract.employee_number
            )
        return None


# 싱글톤 인스턴스
sync_service = SyncService()
