"""
데이터 동기화 서비스 (Facade)

개인(PersonalProfile) <-> 법인(Employee) 간 데이터 동기화를 처리합니다.
서브 서비스들을 조합하여 통합 인터페이스를 제공합니다.

Phase 4: 데이터 동기화 및 퇴사 처리
"""
from typing import Dict, List, Optional, Any
from datetime import datetime
import json

from app.database import db
from app.models.employee import Employee
from app.models.personal_profile import PersonalProfile
from app.models.profile import Profile
from app.models.person_contract import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog
)

# 서브 서비스 임포트
from app.services.sync_basic_service import SyncBasicService
from app.services.sync_relation_service import SyncRelationService


class SyncService:
    """
    개인-법인 데이터 동기화 서비스 (Facade)

    주요 기능:
    - 개인 -> 법인 동기화 (개인정보 변경 시)
    - 법인 -> 개인 동기화 (선택적, 법인 정보 수정 시)
    - 1회성 데이터 제공 (스냅샷)
    - 동기화 로그 기록
    """

    # 동기화 가능한 기본 필드 매핑 (PersonalProfile -> Employee)
    BASIC_FIELD_MAPPING = {
        'name': 'name',
        'english_name': 'english_name',
        'chinese_name': 'chinese_name',
        'photo': 'photo',
        'birth_date': 'birth_date',
        'lunar_birth': 'lunar_birth',
        'gender': 'gender',
    }

    # 연락처 필드 매핑
    CONTACT_FIELD_MAPPING = {
        'mobile_phone': 'mobile_phone',
        'home_phone': 'home_phone',
        'email': 'email',
        'postal_code': 'postal_code',
        'address': 'address',
        'detailed_address': 'detailed_address',
    }

    # 추가 개인정보 필드 매핑
    EXTRA_FIELD_MAPPING = {
        'nationality': 'nationality',
        'blood_type': 'blood_type',
        'religion': 'religion',
        'hobby': 'hobby',
        'specialty': 'specialty',
        'disability_info': 'disability_info',
        'resident_number': 'resident_number',
        'marital_status': 'marital_status',
        # 실제 거주 주소
        'actual_postal_code': 'actual_postal_code',
        'actual_address': 'actual_address',
        'actual_detailed_address': 'actual_detailed_address',
        # 비상연락처
        'emergency_contact': 'emergency_contact',
        'emergency_relation': 'emergency_relation',
    }

    # 데이터 공유 설정과 필드 그룹 매핑
    SHARING_FIELD_GROUPS = {
        'share_basic_info': BASIC_FIELD_MAPPING,
        'share_contact': CONTACT_FIELD_MAPPING,
    }

    def __init__(self):
        self._current_user_id = None
        self._basic_service = SyncBasicService()
        self._relation_service = SyncRelationService()

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정 (로그 기록용)"""
        self._current_user_id = user_id
        self._basic_service.set_current_user(user_id)
        self._relation_service.set_current_user(user_id)

    # ===== 필드 조회 메서드 =====

    def get_syncable_fields(self, contract_id: int) -> Dict[str, List[str]]:
        """
        계약의 데이터 공유 설정에 따른 동기화 가능 필드 목록 조회

        Returns:
            {
                'basic': ['name', 'photo', ...],
                'contact': ['mobile_phone', 'email', ...],
                'education': True/False,
                'career': True/False,
                ...
            }
        """
        settings = DataSharingSettings.query.filter_by(contract_id=contract_id).first()

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
            result['basic'] = list(self.BASIC_FIELD_MAPPING.keys())

        if settings.share_contact:
            result['contact'] = list(self.CONTACT_FIELD_MAPPING.keys())

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
            'basic': self.BASIC_FIELD_MAPPING,
            'contact': self.CONTACT_FIELD_MAPPING,
            'extra': self.EXTRA_FIELD_MAPPING,
        }

    # ===== 동기화 메서드 =====

    def sync_personal_to_employee(
        self,
        contract_id: int,
        fields: Optional[List[str]] = None,
        sync_type: str = SyncLog.SYNC_TYPE_AUTO
    ) -> Dict[str, Any]:
        """
        개인 프로필 -> 법인 직원 데이터 동기화

        Args:
            contract_id: 계약 ID
            fields: 동기화할 필드 목록 (None이면 설정에 따라 자동)
            sync_type: 동기화 유형 (auto, manual, initial)

        Returns:
            동기화 결과
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        personal_profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()
        if not personal_profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        # 관계 데이터용 Profile 조회 (educations, careers 등)
        profile = Profile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

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
        sync_type: str = SyncLog.SYNC_TYPE_MANUAL
    ) -> Dict[str, Any]:
        """
        법인 직원 -> 개인 프로필 데이터 동기화 (역방향, 선택적)
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()
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

        db.session.commit()

        return {
            'success': True,
            'synced_fields': result['synced_fields'],
            'changes': result['changes'],
            'logs': result['log_ids'],
        }

    # ===== 실시간 동기화 지원 =====

    def should_auto_sync(self, contract_id: int) -> bool:
        """실시간 자동 동기화 여부 확인"""
        settings = DataSharingSettings.query.filter_by(contract_id=contract_id).first()
        return settings.is_realtime_sync if settings else False

    def get_contracts_for_user(self, user_id: int) -> List[Dict]:
        """사용자의 활성 계약 목록 조회 (동기화 대상)"""
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()
        return [c.to_dict(include_relations=True) for c in contracts]

    def sync_all_contracts_for_user(
        self,
        user_id: int,
        sync_type: str = SyncLog.SYNC_TYPE_AUTO
    ) -> Dict[str, Any]:
        """사용자의 모든 활성 계약에 대해 동기화 실행"""
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()

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
        all_mappings = {
            **self.BASIC_FIELD_MAPPING,
            **self.CONTACT_FIELD_MAPPING,
            **self.EXTRA_FIELD_MAPPING,
        }
        return all_mappings.get(profile_field)

    def _find_or_create_employee(
        self,
        contract: PersonCorporateContract,
        profile: PersonalProfile,
        full_sync: bool = False,
        force_create: bool = False
    ) -> Optional[Employee]:
        """계약에 연결된 직원 찾기 또는 생성

        Args:
            contract: 계약 정보
            profile: 개인 프로필
            full_sync: True면 전체 프로필 데이터 동기화 (SSOT: FIELD_MAPPING 사용)
            force_create: True면 기존 Employee 무시하고 항상 새로 생성 (회사별 분리용)

        Returns:
            Employee 객체
        """
        from app.models.company import Company
        company = Company.query.get(contract.company_id)

        # force_create가 아닌 경우에만 기존 Employee 탐색
        if not force_create:
            if contract.employee_number:
                employee = Employee.query.filter_by(
                    employee_number=contract.employee_number
                ).first()
                if employee:
                    return employee

            if company:
                employee = Employee.query.filter_by(
                    name=profile.name,
                    organization_id=company.root_organization_id
                ).first()

                if employee:
                    if not contract.employee_number and employee.employee_number:
                        contract.employee_number = employee.employee_number
                    return employee

        # 새 Employee 생성
        employee = self._create_employee_from_profile(
            profile, contract, company, full_sync
        )
        db.session.add(employee)
        db.session.flush()

        employee.employee_number = f"EMP-{datetime.utcnow().year}-{employee.id:04d}"
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
            # SSOT: FIELD_MAPPING 활용하여 전체 필드 복사
            all_mappings = {
                **self.BASIC_FIELD_MAPPING,
                **self.CONTACT_FIELD_MAPPING,
                **self.EXTRA_FIELD_MAPPING,
            }
            for profile_field, employee_field in all_mappings.items():
                value = getattr(profile, profile_field, None)
                if value is not None:
                    employee_data[employee_field] = value

        return Employee(**employee_data)

    def _find_employee_by_contract(
        self,
        contract: PersonCorporateContract
    ) -> Optional[Employee]:
        """계약에 연결된 직원 조회"""
        if contract.employee_number:
            return Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()
        return None


# 싱글톤 인스턴스
sync_service = SyncService()
