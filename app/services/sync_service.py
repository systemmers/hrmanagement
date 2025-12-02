"""
데이터 동기화 서비스

개인(PersonalProfile) <-> 법인(Employee) 간 데이터 동기화를 처리합니다.
Phase 4: 데이터 동기화 및 퇴사 처리
"""
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import json

from app.database import db
from app.models.employee import Employee
from app.models.personal_profile import (
    PersonalProfile,
    PersonalEducation,
    PersonalCareer,
    PersonalCertificate,
    PersonalLanguage,
    PersonalMilitaryService
)
from app.models.person_contract import (
    PersonCorporateContract,
    DataSharingSettings,
    SyncLog
)


class SyncService:
    """
    개인-법인 데이터 동기화 서비스

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
    }

    # 데이터 공유 설정과 필드 그룹 매핑
    SHARING_FIELD_GROUPS = {
        'share_basic_info': BASIC_FIELD_MAPPING,
        'share_contact': CONTACT_FIELD_MAPPING,
    }

    def __init__(self):
        self._current_user_id = None

    def set_current_user(self, user_id: int):
        """현재 작업 사용자 설정 (로그 기록용)"""
        self._current_user_id = user_id

    # ===== 필드 조회 메서드 =====

    def get_syncable_fields(self, contract_id: int) -> Dict[str, List[str]]:
        """
        계약의 데이터 공유 설정에 따른 동기화 가능 필드 목록 조회

        Args:
            contract_id: 계약 ID

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

        if not settings:
            # 기본값: 기본 정보만 공유
            return {
                'basic': list(self.BASIC_FIELD_MAPPING.keys()),
                'contact': [],
                'education': False,
                'career': False,
                'certificates': False,
                'languages': False,
                'military': False,
            }

        result = {
            'basic': [],
            'contact': [],
            'education': settings.share_education,
            'career': settings.share_career,
            'certificates': settings.share_certificates,
            'languages': settings.share_languages,
            'military': settings.share_military,
        }

        if settings.share_basic_info:
            result['basic'] = list(self.BASIC_FIELD_MAPPING.keys())

        if settings.share_contact:
            result['contact'] = list(self.CONTACT_FIELD_MAPPING.keys())

        return result

    def get_all_field_mappings(self) -> Dict[str, Dict[str, str]]:
        """모든 필드 매핑 정보 반환"""
        return {
            'basic': self.BASIC_FIELD_MAPPING.copy(),
            'contact': self.CONTACT_FIELD_MAPPING.copy(),
            'extra': self.EXTRA_FIELD_MAPPING.copy(),
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
            {
                'success': bool,
                'synced_fields': [...],
                'changes': [{field, old, new}, ...],
                'logs': [log_id, ...]
            }
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        # 개인 프로필 조회
        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

        if not profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        # 해당 계약의 법인 직원 조회 (employee_number로 매칭)
        employee = self._find_or_create_employee(contract, profile)

        if not employee:
            return {'success': False, 'error': '직원 데이터를 생성/조회할 수 없습니다.'}

        # 동기화 가능 필드 조회
        syncable = self.get_syncable_fields(contract_id)

        # 동기화할 필드 결정
        if fields:
            # 명시적으로 지정된 필드만 동기화
            target_fields = fields
        else:
            # 설정에 따른 전체 필드
            target_fields = syncable['basic'] + syncable['contact']

        # 필드 동기화 실행
        changes = []
        synced_fields = []
        log_ids = []

        for field in target_fields:
            # 필드 매핑 확인
            employee_field = self._get_employee_field(field)
            if not employee_field:
                continue

            # 값 비교 및 업데이트
            old_value = getattr(employee, employee_field, None)
            new_value = getattr(profile, field, None)

            if old_value != new_value:
                setattr(employee, employee_field, new_value)

                change = {
                    'field': field,
                    'old_value': self._serialize_value(old_value),
                    'new_value': self._serialize_value(new_value),
                }
                changes.append(change)
                synced_fields.append(field)

                # 동기화 로그 생성
                log = SyncLog.create_log(
                    contract_id=contract_id,
                    sync_type=sync_type,
                    entity_type='personal_profile',
                    field_name=field,
                    old_value=change['old_value'],
                    new_value=change['new_value'],
                    direction='personal_to_employee',
                    user_id=self._current_user_id
                )
                db.session.add(log)
                db.session.flush()
                log_ids.append(log.id)

        # 관계 데이터 동기화 (학력, 경력 등)
        relation_results = self._sync_relations(
            contract_id, profile, employee, syncable, sync_type
        )

        if relation_results['changes']:
            changes.extend(relation_results['changes'])
            log_ids.extend(relation_results['log_ids'])

        db.session.commit()

        return {
            'success': True,
            'synced_fields': synced_fields,
            'changes': changes,
            'logs': log_ids,
            'relations': relation_results.get('synced_relations', [])
        }

    def sync_employee_to_personal(
        self,
        contract_id: int,
        fields: Optional[List[str]] = None,
        sync_type: str = SyncLog.SYNC_TYPE_MANUAL
    ) -> Dict[str, Any]:
        """
        법인 직원 -> 개인 프로필 데이터 동기화 (역방향, 선택적)

        주의: 이 기능은 특별한 경우에만 사용됩니다.
        일반적으로 개인 -> 법인 방향으로만 동기화합니다.

        Args:
            contract_id: 계약 ID
            fields: 동기화할 필드 목록
            sync_type: 동기화 유형

        Returns:
            동기화 결과
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 동기화할 수 있습니다.'}

        # 개인 프로필 조회
        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

        if not profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        # 직원 조회
        employee = self._find_employee_by_contract(contract)
        if not employee:
            return {'success': False, 'error': '연결된 직원을 찾을 수 없습니다.'}

        # 동기화 가능 필드 조회
        syncable = self.get_syncable_fields(contract_id)

        # 동기화할 필드 결정
        if fields:
            target_fields = fields
        else:
            target_fields = syncable['basic'] + syncable['contact']

        # 필드 동기화 실행
        changes = []
        synced_fields = []
        log_ids = []

        for field in target_fields:
            employee_field = self._get_employee_field(field)
            if not employee_field:
                continue

            old_value = getattr(profile, field, None)
            new_value = getattr(employee, employee_field, None)

            if old_value != new_value:
                setattr(profile, field, new_value)

                change = {
                    'field': field,
                    'old_value': self._serialize_value(old_value),
                    'new_value': self._serialize_value(new_value),
                }
                changes.append(change)
                synced_fields.append(field)

                log = SyncLog.create_log(
                    contract_id=contract_id,
                    sync_type=sync_type,
                    entity_type='employee',
                    field_name=field,
                    old_value=change['old_value'],
                    new_value=change['new_value'],
                    direction='employee_to_personal',
                    user_id=self._current_user_id
                )
                db.session.add(log)
                db.session.flush()
                log_ids.append(log.id)

        db.session.commit()

        return {
            'success': True,
            'synced_fields': synced_fields,
            'changes': changes,
            'logs': log_ids,
        }

    # ===== 1회성 제공 메서드 =====

    def get_snapshot(
        self,
        contract_id: int,
        include_relations: bool = True
    ) -> Dict[str, Any]:
        """
        계약 기준 개인 프로필 스냅샷 생성 (1회성 제공용)

        데이터 공유 설정에 따라 허용된 데이터만 포함합니다.

        Args:
            contract_id: 계약 ID
            include_relations: 관계 데이터 포함 여부

        Returns:
            스냅샷 데이터
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        if contract.status != PersonCorporateContract.STATUS_APPROVED:
            return {'success': False, 'error': '승인된 계약만 조회할 수 있습니다.'}

        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

        if not profile:
            return {'success': False, 'error': '개인 프로필을 찾을 수 없습니다.'}

        syncable = self.get_syncable_fields(contract_id)

        # 기본 데이터 수집
        snapshot = {
            'snapshot_at': datetime.utcnow().isoformat(),
            'contract_id': contract_id,
            'data': {}
        }

        # 기본 정보
        if syncable['basic']:
            snapshot['data']['basic'] = {}
            for field in syncable['basic']:
                snapshot['data']['basic'][field] = getattr(profile, field, None)

        # 연락처 정보
        if syncable['contact']:
            snapshot['data']['contact'] = {}
            for field in syncable['contact']:
                snapshot['data']['contact'][field] = getattr(profile, field, None)

        # 관계 데이터
        if include_relations:
            if syncable['education']:
                snapshot['data']['educations'] = [
                    e.to_dict() for e in profile.educations.all()
                ]

            if syncable['career']:
                snapshot['data']['careers'] = [
                    c.to_dict() for c in profile.careers.all()
                ]

            if syncable['certificates']:
                snapshot['data']['certificates'] = [
                    c.to_dict() for c in profile.certificates.all()
                ]

            if syncable['languages']:
                snapshot['data']['languages'] = [
                    l.to_dict() for l in profile.languages.all()
                ]

            if syncable['military'] and profile.military_service:
                snapshot['data']['military_service'] = profile.military_service.to_dict()

        # 스냅샷 생성 로그
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=SyncLog.SYNC_TYPE_MANUAL,
            entity_type='snapshot',
            field_name=None,
            old_value=None,
            new_value=json.dumps(list(snapshot['data'].keys())),
            direction='personal_to_company',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        snapshot['success'] = True
        return snapshot

    def apply_snapshot_to_employee(
        self,
        contract_id: int,
        snapshot_data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        스냅샷 데이터를 직원 정보에 적용 (1회성 제공)

        Args:
            contract_id: 계약 ID
            snapshot_data: get_snapshot()으로 생성된 스냅샷

        Returns:
            적용 결과
        """
        contract = PersonCorporateContract.query.get(contract_id)
        if not contract:
            return {'success': False, 'error': '계약을 찾을 수 없습니다.'}

        profile = PersonalProfile.query.filter_by(
            user_id=contract.person_user_id
        ).first()

        employee = self._find_or_create_employee(contract, profile)
        if not employee:
            return {'success': False, 'error': '직원 데이터를 생성/조회할 수 없습니다.'}

        data = snapshot_data.get('data', {})
        changes = []

        # 기본 정보 적용
        basic_data = data.get('basic', {})
        for field, value in basic_data.items():
            emp_field = self._get_employee_field(field)
            if emp_field:
                old_value = getattr(employee, emp_field, None)
                if old_value != value:
                    setattr(employee, emp_field, value)
                    changes.append({
                        'field': field,
                        'old_value': self._serialize_value(old_value),
                        'new_value': self._serialize_value(value)
                    })

        # 연락처 정보 적용
        contact_data = data.get('contact', {})
        for field, value in contact_data.items():
            emp_field = self._get_employee_field(field)
            if emp_field:
                old_value = getattr(employee, emp_field, None)
                if old_value != value:
                    setattr(employee, emp_field, value)
                    changes.append({
                        'field': field,
                        'old_value': self._serialize_value(old_value),
                        'new_value': self._serialize_value(value)
                    })

        # 적용 로그
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=SyncLog.SYNC_TYPE_MANUAL,
            entity_type='snapshot_apply',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'changed_fields': len(changes)}),
            direction='snapshot_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.commit()

        return {
            'success': True,
            'changes': changes,
            'employee_id': employee.id
        }

    # ===== 실시간 동기화 지원 =====

    def should_auto_sync(self, contract_id: int) -> bool:
        """실시간 자동 동기화 여부 확인"""
        settings = DataSharingSettings.query.filter_by(contract_id=contract_id).first()
        return settings.is_realtime_sync if settings else False

    def get_contracts_for_user(self, user_id: int) -> List[Dict]:
        """
        사용자의 활성 계약 목록 조회 (동기화 대상)

        Args:
            user_id: 개인 사용자 ID

        Returns:
            활성 계약 목록
        """
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
        """
        사용자의 모든 활성 계약에 대해 동기화 실행

        Args:
            user_id: 개인 사용자 ID
            sync_type: 동기화 유형

        Returns:
            전체 동기화 결과
        """
        contracts = PersonCorporateContract.query.filter_by(
            person_user_id=user_id,
            status=PersonCorporateContract.STATUS_APPROVED
        ).all()

        results = []
        for contract in contracts:
            # 실시간 동기화가 활성화된 계약만 처리
            if self.should_auto_sync(contract.id):
                result = self.sync_personal_to_employee(
                    contract.id,
                    sync_type=sync_type
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

    def _serialize_value(self, value: Any) -> Optional[str]:
        """값을 JSON 직렬화 가능한 문자열로 변환"""
        if value is None:
            return None
        if isinstance(value, (str, int, float, bool)):
            return str(value)
        if isinstance(value, datetime):
            return value.isoformat()
        return json.dumps(value)

    def _find_or_create_employee(
        self,
        contract: PersonCorporateContract,
        profile: PersonalProfile
    ) -> Optional[Employee]:
        """
        계약에 연결된 직원 찾기 또는 생성

        Args:
            contract: 계약 정보
            profile: 개인 프로필

        Returns:
            Employee 모델 또는 None
        """
        # 계약의 employee_number로 직원 찾기
        if contract.employee_number:
            employee = Employee.query.filter_by(
                employee_number=contract.employee_number
            ).first()
            if employee:
                return employee

        # 동일 회사의 동일 이름 직원 찾기 (임시 로직)
        from app.models.company import Company
        company = Company.query.get(contract.company_id)

        if company:
            # organization_id를 통한 직원 검색
            employee = Employee.query.filter_by(
                name=profile.name,
                organization_id=company.organization_id
            ).first()

            if employee:
                # 계약에 employee_number 업데이트
                if not contract.employee_number and employee.employee_number:
                    contract.employee_number = employee.employee_number
                return employee

        # 직원이 없으면 새로 생성
        employee = Employee(
            name=profile.name,
            email=profile.email,
            phone=profile.mobile_phone,
            organization_id=company.organization_id if company else None,
            department=contract.department,
            position=contract.position,
            status='active',
            hire_date=datetime.utcnow().strftime('%Y-%m-%d'),
        )
        db.session.add(employee)
        db.session.flush()

        # employee_number 생성 및 계약 업데이트
        employee.employee_number = f"EMP-{datetime.utcnow().year}-{employee.id:04d}"
        contract.employee_number = employee.employee_number

        return employee

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

    def _sync_relations(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        syncable: Dict,
        sync_type: str
    ) -> Dict[str, Any]:
        """관계 데이터 동기화 (학력, 경력 등)"""
        changes = []
        log_ids = []
        synced_relations = []

        # 학력 동기화
        if syncable.get('education'):
            result = self._sync_education(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('education')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 경력 동기화
        if syncable.get('career'):
            result = self._sync_career(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('career')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 자격증 동기화
        if syncable.get('certificates'):
            result = self._sync_certificates(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('certificates')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 어학 동기화
        if syncable.get('languages'):
            result = self._sync_languages(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('languages')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        # 병역 동기화
        if syncable.get('military'):
            result = self._sync_military(contract_id, profile, employee, sync_type)
            if result['synced']:
                synced_relations.append('military')
                changes.extend(result.get('changes', []))
                log_ids.extend(result.get('log_ids', []))

        return {
            'synced_relations': synced_relations,
            'changes': changes,
            'log_ids': log_ids
        }

    def _sync_education(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """학력 정보 동기화"""
        from app.models.extended import Education

        personal_edus = list(profile.educations.all())
        if not personal_edus:
            return {'synced': False}

        # 기존 직원 학력 삭제 후 새로 추가 (전체 교체 방식)
        employee.educations.delete()

        for pe in personal_edus:
            edu = Education(
                employee_id=employee.id,
                school_type=pe.school_type,
                school_name=pe.school_name,
                major=pe.major,
                degree=pe.degree,
                admission_date=pe.admission_date,
                graduation_date=pe.graduation_date,
                status=pe.status,
            )
            db.session.add(edu)

        # 로그 생성
        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='education',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_edus)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'education', 'count': len(personal_edus)}],
            'log_ids': [log.id]
        }

    def _sync_career(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """경력 정보 동기화"""
        from app.models.extended import Career

        personal_careers = list(profile.careers.all())
        if not personal_careers:
            return {'synced': False}

        employee.careers.delete()

        for pc in personal_careers:
            career = Career(
                employee_id=employee.id,
                company_name=pc.company_name,
                department=pc.department,
                position=pc.position,
                job_title=pc.job_title,
                start_date=pc.start_date,
                end_date=pc.end_date,
                is_current=pc.is_current,
                responsibilities=pc.responsibilities,
            )
            db.session.add(career)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='career',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_careers)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'career', 'count': len(personal_careers)}],
            'log_ids': [log.id]
        }

    def _sync_certificates(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """자격증 정보 동기화"""
        from app.models.extended import Certificate

        personal_certs = list(profile.certificates.all())
        if not personal_certs:
            return {'synced': False}

        employee.certificates.delete()

        for pc in personal_certs:
            cert = Certificate(
                employee_id=employee.id,
                name=pc.name,
                issuing_organization=pc.issuing_organization,
                issue_date=pc.issue_date,
                expiry_date=pc.expiry_date,
                certificate_number=pc.certificate_number,
            )
            db.session.add(cert)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='certificate',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_certs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'certificate', 'count': len(personal_certs)}],
            'log_ids': [log.id]
        }

    def _sync_languages(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """어학 능력 동기화"""
        from app.models.extended import Language

        personal_langs = list(profile.languages.all())
        if not personal_langs:
            return {'synced': False}

        employee.languages.delete()

        for pl in personal_langs:
            lang = Language(
                employee_id=employee.id,
                language=pl.language,
                proficiency=pl.proficiency,
                test_name=pl.test_name,
                score=pl.score,
                test_date=pl.test_date,
            )
            db.session.add(lang)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='language',
            field_name=None,
            old_value=None,
            new_value=json.dumps({'count': len(personal_langs)}),
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'language', 'count': len(personal_langs)}],
            'log_ids': [log.id]
        }

    def _sync_military(
        self,
        contract_id: int,
        profile: PersonalProfile,
        employee: Employee,
        sync_type: str
    ) -> Dict[str, Any]:
        """병역 정보 동기화"""
        from app.models.extended import MilitaryService

        personal_military = profile.military_service
        if not personal_military:
            return {'synced': False}

        # 기존 병역 정보 삭제
        if employee.military_service:
            db.session.delete(employee.military_service)

        military = MilitaryService(
            employee_id=employee.id,
            service_type=personal_military.service_type,
            branch=personal_military.branch,
            rank=personal_military.rank,
            start_date=personal_military.start_date,
            end_date=personal_military.end_date,
            discharge_type=personal_military.discharge_type,
        )
        db.session.add(military)

        log = SyncLog.create_log(
            contract_id=contract_id,
            sync_type=sync_type,
            entity_type='military_service',
            field_name=None,
            old_value=None,
            new_value='synced',
            direction='personal_to_employee',
            user_id=self._current_user_id
        )
        db.session.add(log)
        db.session.flush()

        return {
            'synced': True,
            'changes': [{'entity': 'military_service', 'synced': True}],
            'log_ids': [log.id]
        }


# 싱글톤 인스턴스
sync_service = SyncService()
