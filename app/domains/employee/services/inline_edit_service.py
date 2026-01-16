"""
인라인 편집 서비스

Phase 0.5: 섹션별 인라인 편집 기능을 제공하는 서비스
- 정적 섹션 업데이트 (개인정보, 소속정보, 계약정보 등)
- ServiceResult 패턴 사용
- employee_core_service, employee_relation_service와 협력

사용법:
    from app.domains.employee.services import inline_edit_service

    result = inline_edit_service.update_section(
        employee_id=1,
        section='personal',
        data={'name': '홍길동', 'phone': '010-1234-5678'}
    )

    if result.success:
        updated_data = result.data
    else:
        error_message = result.message
"""
from typing import Dict, Optional, Any, Tuple

from app.shared.base.service_result import ServiceResult
from app.shared.utils.transaction import atomic_transaction


class InlineEditService:
    """인라인 편집 서비스

    정적 섹션(개인정보, 소속정보, 계약정보 등)의 인라인 편집을 처리합니다.
    동적 섹션(가족정보, 학력정보 등)은 employee_relation_service를 통해 처리합니다.
    """

    # 정적 섹션 설정 (section_api.py의 STATIC_SECTIONS와 동기화)
    # NOTE: 필드명은 Employee 모델 SSOT에 맞춤 (2026-01-16)
    STATIC_SECTIONS = {
        'personal': {
            'name': '개인 기본정보',
            'fields': [
                # 기본 정보
                'name', 'chinese_name', 'english_name', 'foreign_name',
                'birth_date', 'lunar_birth', 'gender', 'nationality',
                'resident_number', 'postal_code',
                # 연락처
                'phone', 'mobile_phone', 'home_phone',
                'email',
                # 비상연락처
                'emergency_contact', 'emergency_relation',
                # 주소
                'address', 'detailed_address',
                'actual_address', 'actual_detailed_address',
                'actual_postal_code',
                # 기타
                'marital_status', 'bank_name', 'account_number', 'account_holder',
                'hobby', 'specialty', 'disability_info', 'photo'
            ]
        },
        'organization': {
            'name': '소속정보',
            'fields': [
                'organization_id', 'department', 'team', 'position', 'job_title',
                'job_grade', 'job_role', 'work_location',
                'internal_phone', 'company_email'
            ]
        },
        'contract': {
            'name': '계약정보',
            'fields': [
                'hire_date', 'contract_start_date', 'contract_end_date',
                'employee_type', 'work_type', 'contract_type', 'probation_end_date'
            ],
            'readonly_fields': ['hire_date', 'contract_start_date', 'contract_end_date']
        },
        'salary': {
            'name': '급여정보',
            'model': 'Salary',  # relation 모델 사용
            'fields': [
                'salary_type', 'base_salary', 'position_allowance', 'meal_allowance',
                'transportation_allowance', 'total_salary', 'payment_day', 'payment_method',
                'annual_salary', 'monthly_salary', 'hourly_wage'
            ],
            'readonly_fields': ['total_salary']
        },
        'benefit': {
            'name': '연차 및 복리후생',
            'model': 'Benefit',  # relation 모델 사용
            'fields': [
                'year', 'annual_leave_granted', 'annual_leave_used',
                'annual_leave_remaining', 'severance_type', 'severance_method'
            ],
            'readonly_fields': ['annual_leave_remaining']
        },
        'military': {
            'name': '병역정보',
            'fields': [
                'military_status', 'military_branch', 'military_rank',
                'military_start_date', 'military_end_date', 'military_exemption_reason'
            ]
        },
        'account': {
            'name': '계정정보',
            'fields': ['username', 'email'],
            'readonly_fields': ['username']
        },
        'basic': {
            'name': '기본정보',
            'fields': ['name', 'phone', 'email', 'address', 'address_detail']
        }
    }

    def __init__(self):
        self._employee_repo = None
        self._core_service = None
        self._relation_service = None

    # ========================================
    # Lazy Repository/Service 초기화
    # ========================================

    @property
    def employee_repo(self):
        """EmployeeRepository lazy 로드"""
        if self._employee_repo is None:
            from app.domains.employee.repositories.employee_repository import employee_repository
            self._employee_repo = employee_repository
        return self._employee_repo

    @property
    def core_service(self):
        """EmployeeCoreService lazy 로드"""
        if self._core_service is None:
            from app.domains.employee.services.employee_core_service import employee_core_service
            self._core_service = employee_core_service
        return self._core_service

    @property
    def relation_service(self):
        """EmployeeRelationService lazy 로드"""
        if self._relation_service is None:
            from app.domains.employee.services.employee_relation_service import employee_relation_service
            self._relation_service = employee_relation_service
        return self._relation_service

    # ========================================
    # 메인 API: 섹션 업데이트
    # ========================================

    def update_section(
        self,
        employee_id: int,
        section: str,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """섹션 데이터 업데이트

        Args:
            employee_id: 직원 ID
            section: 섹션 이름 (personal, organization, contract 등)
            data: 업데이트할 데이터

        Returns:
            ServiceResult with updated data or error
        """
        # 섹션 유효성 검사
        if section not in self.STATIC_SECTIONS:
            return ServiceResult.fail(
                f'알 수 없는 섹션입니다: {section}',
                error_code='INVALID_SECTION'
            )

        # 권한 검사
        if not self.core_service.verify_access(employee_id):
            return ServiceResult.forbidden('접근 권한이 없습니다.')

        # 직원 조회
        employee = self.employee_repo.find_by_id(employee_id)
        if not employee:
            return ServiceResult.not_found('직원')

        # 섹션별 업데이트 메서드 라우팅
        update_method = getattr(self, f'_update_{section}', None)
        if update_method:
            return update_method(employee, data)
        else:
            # 기본 필드 업데이트
            return self._update_generic_fields(employee, section, data)

    def get_section_data(
        self,
        employee_id: int,
        section: str
    ) -> ServiceResult[Dict]:
        """섹션 데이터 조회

        Args:
            employee_id: 직원 ID
            section: 섹션 이름

        Returns:
            ServiceResult with section data
        """
        if section not in self.STATIC_SECTIONS:
            return ServiceResult.fail(
                f'알 수 없는 섹션입니다: {section}',
                error_code='INVALID_SECTION'
            )

        if not self.core_service.verify_access(employee_id):
            return ServiceResult.forbidden('접근 권한이 없습니다.')

        employee = self.employee_repo.find_by_id(employee_id)
        if not employee:
            return ServiceResult.not_found('직원')

        section_config = self.STATIC_SECTIONS[section]
        fields = section_config['fields']

        # relation 모델 사용 여부 확인
        model_name = section_config.get('model')

        if model_name == 'Salary':
            # Salary relation에서 데이터 조회
            salary = employee.salary
            return ServiceResult.ok(data=salary.to_dict() if salary else {})
        elif model_name == 'Benefit':
            # Benefit relation에서 데이터 조회
            benefit = employee.benefit
            return ServiceResult.ok(data=benefit.to_dict() if benefit else {})
        else:
            # Employee 모델에서 직접 조회
            section_data = {}
            employee_dict = employee.to_dict()
            for field in fields:
                if field in employee_dict:
                    section_data[field] = employee_dict[field]

            return ServiceResult.ok(data=section_data)

    # ========================================
    # 섹션별 업데이트 메서드
    # ========================================

    def _update_personal(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """개인 기본정보 업데이트

        Phase 28 호환: RRN 입력 시 birth_date, age, gender 자동 입력
        """
        try:
            with atomic_transaction():
                # RRN 자동입력 처리 (resident_number 필드 사용)
                if 'resident_number' in data and data['resident_number']:
                    data = self._apply_rrn_auto_fields(data)

                # 필드 업데이트
                fields = self.STATIC_SECTIONS['personal']['fields']
                self._update_employee_fields(employee, data, fields)

            # 업데이트된 데이터 반환
            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'personal'),
                message='개인 기본정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_organization(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """소속정보 업데이트"""
        try:
            with atomic_transaction():
                # organization_id 처리
                if 'organization_id' in data:
                    org_id = data['organization_id']
                    data['organization_id'] = int(org_id) if org_id else None

                fields = self.STATIC_SECTIONS['organization']['fields']
                self._update_employee_fields(employee, data, fields)

            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'organization'),
                message='소속정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_contract(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """계약정보 업데이트

        읽기전용 필드(hire_date 등)는 업데이트 제외
        """
        try:
            with atomic_transaction():
                section_config = self.STATIC_SECTIONS['contract']
                fields = section_config['fields']
                readonly_fields = section_config.get('readonly_fields', [])

                # 읽기전용 필드 제외
                writable_data = {
                    k: v for k, v in data.items()
                    if k not in readonly_fields
                }

                self._update_employee_fields(employee, writable_data, fields)

            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'contract'),
                message='계약정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_salary(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """급여정보 업데이트

        Salary relation 모델 직접 업데이트
        금액 필드 정수 변환 처리
        """
        try:
            with atomic_transaction():
                # Salary relation 조회 또는 생성
                salary = employee.salary
                if not salary:
                    from app.domains.employee.models import Salary
                    salary = Salary(employee_id=employee.id)
                    from app.database import db
                    db.session.add(salary)

                # 금액 필드 정수 변환
                currency_fields = [
                    'base_salary', 'position_allowance', 'meal_allowance',
                    'transportation_allowance', 'annual_salary', 'monthly_salary',
                    'hourly_wage', 'overtime_allowance', 'night_allowance',
                    'holiday_allowance'
                ]
                for field in currency_fields:
                    if field in data and data[field]:
                        try:
                            data[field] = int(str(data[field]).replace(',', ''))
                        except (ValueError, TypeError):
                            data[field] = None

                # 정수 필드 변환
                int_fields = ['payment_day', 'overtime_hours', 'night_hours', 'holiday_days', 'bonus_rate']
                for field in int_fields:
                    if field in data and data[field]:
                        try:
                            data[field] = int(data[field])
                        except (ValueError, TypeError):
                            data[field] = None

                # Salary 모델 필드 업데이트
                section_config = self.STATIC_SECTIONS['salary']
                fields = section_config['fields']
                readonly_fields = section_config.get('readonly_fields', [])

                for field in fields:
                    if field in data and field not in readonly_fields:
                        value = data[field]
                        if value == '':
                            value = None
                        if hasattr(salary, field):
                            setattr(salary, field, value)

            return ServiceResult.ok(
                data=salary.to_dict() if salary else {},
                message='급여정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_benefit(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """복리후생 업데이트

        Benefit relation 모델 직접 업데이트
        """
        try:
            with atomic_transaction():
                # Benefit relation 조회 또는 생성
                benefit = employee.benefit
                if not benefit:
                    from app.domains.employee.models import Benefit
                    benefit = Benefit(employee_id=employee.id)
                    from app.database import db
                    db.session.add(benefit)

                # 정수 필드 변환
                int_fields = ['year', 'annual_leave_granted', 'annual_leave_used']
                for field in int_fields:
                    if field in data and data[field]:
                        try:
                            data[field] = int(data[field])
                        except (ValueError, TypeError):
                            data[field] = None

                # Benefit 모델 필드 업데이트
                section_config = self.STATIC_SECTIONS['benefit']
                fields = section_config['fields']
                readonly_fields = section_config.get('readonly_fields', [])

                for field in fields:
                    if field in data and field not in readonly_fields:
                        value = data[field]
                        if value == '':
                            value = None
                        if hasattr(benefit, field):
                            setattr(benefit, field, value)

                # 잔여 연차 자동 계산
                if benefit.annual_leave_granted is not None and benefit.annual_leave_used is not None:
                    benefit.annual_leave_remaining = benefit.annual_leave_granted - benefit.annual_leave_used

            return ServiceResult.ok(
                data=benefit.to_dict() if benefit else {},
                message='복리후생 정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_military(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """병역정보 업데이트

        군필 상태에 따른 조건부 필드 처리
        """
        try:
            with atomic_transaction():
                # 비대상/면제 시 관련 필드 초기화
                status = data.get('military_status', employee.military_status)
                if status in ['비대상', '면제']:
                    data['military_branch'] = None
                    data['military_rank'] = None
                    data['military_start_date'] = None
                    data['military_end_date'] = None

                fields = self.STATIC_SECTIONS['military']['fields']
                self._update_employee_fields(employee, data, fields)

            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'military'),
                message='병역정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_account(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """계정정보 업데이트

        username은 읽기전용
        """
        try:
            with atomic_transaction():
                section_config = self.STATIC_SECTIONS['account']
                readonly_fields = section_config.get('readonly_fields', [])

                # 읽기전용 필드 제외
                writable_data = {
                    k: v for k, v in data.items()
                    if k not in readonly_fields
                }

                # email만 업데이트 (User 모델 통해)
                if 'email' in writable_data:
                    # User 모델 업데이트는 별도 처리 필요
                    pass

            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'account'),
                message='계정정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_basic(
        self,
        employee,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """기본정보 업데이트 (employee_sub용)"""
        try:
            with atomic_transaction():
                fields = self.STATIC_SECTIONS['basic']['fields']
                self._update_employee_fields(employee, data, fields)

            return ServiceResult.ok(
                data=self._get_section_dict(employee, 'basic'),
                message='기본정보가 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    def _update_generic_fields(
        self,
        employee,
        section: str,
        data: Dict[str, Any]
    ) -> ServiceResult[Dict]:
        """범용 필드 업데이트"""
        try:
            with atomic_transaction():
                section_config = self.STATIC_SECTIONS[section]
                fields = section_config['fields']
                readonly_fields = section_config.get('readonly_fields', [])

                # 읽기전용 필드 제외
                writable_data = {
                    k: v for k, v in data.items()
                    if k not in readonly_fields
                }

                self._update_employee_fields(employee, writable_data, fields)

            return ServiceResult.ok(
                data=self._get_section_dict(employee, section),
                message=f'{section_config["name"]}이(가) 저장되었습니다.'
            )

        except Exception as e:
            return ServiceResult.from_exception(e)

    # ========================================
    # Private 헬퍼 메서드
    # ========================================

    def _update_employee_fields(
        self,
        employee,
        data: Dict[str, Any],
        allowed_fields: list
    ) -> None:
        """Employee 모델 필드 업데이트

        Args:
            employee: Employee 모델 인스턴스
            data: 업데이트 데이터
            allowed_fields: 허용된 필드 목록
        """
        for field in allowed_fields:
            if field in data:
                value = data[field]
                # 빈 문자열을 None으로 변환
                if value == '':
                    value = None
                if hasattr(employee, field):
                    setattr(employee, field, value)

    def _get_section_dict(
        self,
        employee,
        section: str
    ) -> Dict[str, Any]:
        """섹션 필드만 포함하는 Dict 반환"""
        section_config = self.STATIC_SECTIONS.get(section, {})
        fields = section_config.get('fields', [])

        employee_dict = employee.to_dict()
        return {
            field: employee_dict.get(field)
            for field in fields
            if field in employee_dict
        }

    def _apply_rrn_auto_fields(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """주민번호에서 생년월일, 성별 자동 추출

        Phase 28 호환: rrn_parser 사용
        NOTE: 필드명 resident_number 사용 (모델 SSOT 기준, 2026-01-16)
        """
        from app.shared.utils.rrn_parser import RRNParser

        rrn = data.get('resident_number', '')
        if not rrn:
            return data

        result = RRNParser.parse(rrn)
        if result.is_valid:
            # 생년월일 자동 설정
            if not data.get('birth_date') and result.birth_date:
                data['birth_date'] = result.birth_date

            # 성별 자동 설정
            if not data.get('gender') and result.gender:
                data['gender'] = result.gender

        return data


# 싱글톤 인스턴스
inline_edit_service = InlineEditService()
