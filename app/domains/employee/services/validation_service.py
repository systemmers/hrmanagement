"""
인라인 편집 유효성 검사 서비스

Phase 0.6: 섹션별 인라인 편집 데이터 유효성 검사
- 섹션별 필수 필드 검증
- 형식 검증 (전화번호, 이메일, 날짜)
- FieldOptions 기반 옵션 값 검증

사용법:
    from app.domains.employee.services import validation_service

    errors = validation_service.validate_section('personal', data)
    if errors:
        # {'field_name': 'error message'}
        return jsonify({'success': False, 'errors': errors}), 422
"""
import re
from typing import Dict, Optional, Any, List
from datetime import datetime

from app.shared.constants.field_options import FieldOptions


class SectionValidationService:
    """섹션별 유효성 검사 서비스"""

    # 전화번호 패턴 (한국 형식)
    PHONE_PATTERN = re.compile(r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$')

    # 이메일 패턴
    EMAIL_PATTERN = re.compile(r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$')

    # 날짜 패턴 (YYYY-MM-DD)
    DATE_PATTERN = re.compile(r'^\d{4}-\d{2}-\d{2}$')

    # 주민등록번호 패턴 (6-7 또는 13자리)
    RRN_PATTERN = re.compile(r'^(\d{6})-?(\d{7})$')

    # 섹션별 필수 필드 정의
    REQUIRED_FIELDS = {
        'personal': ['name'],
        'organization': [],
        'contract': [],
        'salary': [],
        'benefit': [],
        'military': [],
        'account': [],
        'basic': ['name'],
        # 신규 직원 등록용 (Phase 2)
        'registration': ['name', 'account_username', 'account_email'],
    }

    # 섹션별 필드 타입 정의
    FIELD_TYPES = {
        'personal': {
            'name': {'type': 'text', 'max_length': 50},
            'name_hanja': {'type': 'text', 'max_length': 50},
            'english_name': {'type': 'text', 'max_length': 100},
            'rrn': {'type': 'rrn'},
            'birth_date': {'type': 'date'},
            'gender': {'type': 'option', 'options': 'GENDER'},
            'nationality': {'type': 'option', 'options': 'NATIONALITY'},
            'phone': {'type': 'phone'},
            'emergency_phone': {'type': 'phone'},
            'email': {'type': 'email'},
            'personal_email': {'type': 'email'},
            'address': {'type': 'text', 'max_length': 200},
            'address_detail': {'type': 'text', 'max_length': 100},
        },
        'organization': {
            'organization_id': {'type': 'integer'},
            'department': {'type': 'text', 'max_length': 100},
            'position': {'type': 'option', 'options': 'POSITION'},
            'duty': {'type': 'option', 'options': 'DUTY'},
            'job_grade': {'type': 'option', 'options': 'JOB_GRADE'},
            'job_role': {'type': 'text', 'max_length': 100},
            'work_location': {'type': 'text', 'max_length': 100},
        },
        'contract': {
            'hire_date': {'type': 'date'},
            'contract_start_date': {'type': 'date'},
            'contract_end_date': {'type': 'date'},
            'employee_type': {'type': 'option', 'options': 'EMPLOYEE_TYPE'},
            'work_type': {'type': 'option', 'options': 'WORK_TYPE'},
            'contract_type': {'type': 'option', 'options': 'CONTRACT_TYPE'},
            'probation_end_date': {'type': 'date'},
        },
        'salary': {
            'annual_salary': {'type': 'currency'},
            'base_salary': {'type': 'currency'},
            'allowances': {'type': 'currency'},
            'bonus': {'type': 'currency'},
            'salary_account_bank': {'type': 'text', 'max_length': 50},
            'salary_account_number': {'type': 'text', 'max_length': 50},
            'salary_account_holder': {'type': 'text', 'max_length': 50},
        },
        'benefit': {
            'health_insurance': {'type': 'boolean'},
            'national_pension': {'type': 'boolean'},
            'employment_insurance': {'type': 'boolean'},
            'industrial_accident_insurance': {'type': 'boolean'},
            'retirement_pension_type': {'type': 'option', 'options': 'RETIREMENT_PENSION_TYPE'},
        },
        # Phase 0.7: 병역정보 기본정보로 통합, 단일 필드만 사용
        # military 섹션 삭제, military_status는 basic 섹션에서 처리
        'account': {
            'username': {'type': 'text', 'max_length': 50},
            'email': {'type': 'email'},
        },
        'basic': {
            'name': {'type': 'text', 'max_length': 50},
            'phone': {'type': 'phone'},
            'email': {'type': 'email'},
            'address': {'type': 'text', 'max_length': 200},
            'address_detail': {'type': 'text', 'max_length': 100},
            # Phase 0.7: 병역/비고 통합
            'military_status': {'type': 'option', 'options': 'MILITARY_STATUS'},
            'note': {'type': 'text', 'max_length': 2000},
        },
        # 신규 직원 등록용 (Phase 2)
        'registration': {
            'name': {'type': 'text', 'max_length': 50},
            'account_username': {'type': 'username', 'min_length': 4, 'max_length': 50},
            'account_email': {'type': 'email'},
            'english_name': {'type': 'text', 'max_length': 100},
            'birth_date': {'type': 'date'},
            'gender': {'type': 'option', 'options': 'GENDER'},
            'phone': {'type': 'phone'},
        },
    }

    def validate_section(
        self,
        section: str,
        data: Dict[str, Any],
        strict: bool = False
    ) -> Dict[str, str]:
        """섹션 데이터 유효성 검사

        Args:
            section: 섹션 이름
            data: 검증할 데이터
            strict: True면 필수 필드 검증, False면 입력된 필드만 검증

        Returns:
            에러 딕셔너리 {field: message}, 검증 통과 시 빈 딕셔너리
        """
        errors = {}

        # 섹션 유효성 확인
        if section not in self.FIELD_TYPES:
            return {'_section': f'알 수 없는 섹션입니다: {section}'}

        # 필수 필드 검증 (strict 모드)
        if strict:
            required = self.REQUIRED_FIELDS.get(section, [])
            for field in required:
                value = data.get(field)
                if not value or (isinstance(value, str) and not value.strip()):
                    errors[field] = self._get_field_label(field) + '은(는) 필수 입력 항목입니다.'

        # 필드별 타입 검증
        field_types = self.FIELD_TYPES.get(section, {})
        for field, value in data.items():
            if field not in field_types:
                continue

            # 빈 값은 스킵 (필수 검증은 위에서 처리)
            if not value and value != 0 and value is not False:
                continue

            field_config = field_types[field]
            error = self._validate_field(field, value, field_config)
            if error:
                errors[field] = error

        return errors

    def validate_field(
        self,
        field: str,
        value: Any,
        section: str = None
    ) -> Optional[str]:
        """단일 필드 유효성 검사

        Args:
            field: 필드 이름
            value: 필드 값
            section: 섹션 이름 (옵션, 필드 타입 조회용)

        Returns:
            에러 메시지 또는 None (검증 통과)
        """
        if section and section in self.FIELD_TYPES:
            field_config = self.FIELD_TYPES[section].get(field, {})
            return self._validate_field(field, value, field_config)
        return None

    def _validate_field(
        self,
        field: str,
        value: Any,
        config: Dict[str, Any]
    ) -> Optional[str]:
        """필드 타입별 검증"""
        field_type = config.get('type', 'text')
        label = self._get_field_label(field)

        if field_type == 'text':
            max_length = config.get('max_length', 255)
            if isinstance(value, str) and len(value) > max_length:
                return f'{label}은(는) {max_length}자를 초과할 수 없습니다.'

        elif field_type == 'phone':
            if not self._validate_phone(value):
                return f'{label} 형식이 올바르지 않습니다. (예: 010-1234-5678)'

        elif field_type == 'email':
            if not self._validate_email(value):
                return f'{label} 형식이 올바르지 않습니다.'

        elif field_type == 'date':
            if not self._validate_date(value):
                return f'{label} 형식이 올바르지 않습니다. (예: 2024-01-01)'

        elif field_type == 'rrn':
            if not self._validate_rrn(value):
                return '주민등록번호 형식이 올바르지 않습니다.'

        elif field_type == 'option':
            options_name = config.get('options')
            if options_name and not self._validate_option(value, options_name):
                return f'{label}의 값이 올바르지 않습니다.'

        elif field_type == 'integer':
            if not self._validate_integer(value):
                return f'{label}은(는) 숫자여야 합니다.'

        elif field_type == 'currency':
            if not self._validate_currency(value):
                return f'{label}은(는) 0 이상의 숫자여야 합니다.'

        elif field_type == 'boolean':
            if not self._validate_boolean(value):
                return f'{label} 값이 올바르지 않습니다.'

        elif field_type == 'username':
            min_length = config.get('min_length', 4)
            max_length = config.get('max_length', 50)
            error = self._validate_username(value, min_length, max_length)
            if error:
                return error

        return None

    # ========================================
    # Private: 타입별 검증 메서드
    # ========================================

    def _validate_phone(self, value: str) -> bool:
        """전화번호 형식 검증"""
        if not value:
            return True
        cleaned = re.sub(r'[^\d-]', '', str(value))
        return bool(self.PHONE_PATTERN.match(cleaned))

    def _validate_email(self, value: str) -> bool:
        """이메일 형식 검증"""
        if not value:
            return True
        return bool(self.EMAIL_PATTERN.match(str(value)))

    def _validate_date(self, value: str) -> bool:
        """날짜 형식 검증"""
        if not value:
            return True
        if not self.DATE_PATTERN.match(str(value)):
            return False
        try:
            datetime.strptime(str(value), '%Y-%m-%d')
            return True
        except ValueError:
            return False

    def _validate_rrn(self, value: str) -> bool:
        """주민등록번호 형식 검증 (기본)"""
        if not value:
            return True
        cleaned = re.sub(r'[^\d]', '', str(value))
        return len(cleaned) == 13

    def _validate_option(self, value: str, options_name: str) -> bool:
        """FieldOptions 기반 옵션 값 검증"""
        if not value:
            return True

        # FieldOptions에서 옵션 목록 조회
        options = getattr(FieldOptions, options_name, None)
        if not options:
            return True  # 옵션 정의 없으면 통과

        # 옵션 값 목록 추출
        valid_values = [opt.value for opt in options]
        return str(value) in valid_values

    def _validate_integer(self, value: Any) -> bool:
        """정수 검증"""
        if value is None or value == '':
            return True
        try:
            int(value)
            return True
        except (ValueError, TypeError):
            return False

    def _validate_currency(self, value: Any) -> bool:
        """금액 검증 (0 이상의 정수)"""
        if value is None or value == '':
            return True
        try:
            num = int(value)
            return num >= 0
        except (ValueError, TypeError):
            return False

    def _validate_boolean(self, value: Any) -> bool:
        """불리언 검증"""
        if value is None:
            return True
        if isinstance(value, bool):
            return True
        if isinstance(value, str):
            return value.lower() in ('true', 'false', '1', '0', '')
        return isinstance(value, (int, float)) and value in (0, 1)

    def _validate_username(self, value: str, min_length: int, max_length: int) -> Optional[str]:
        """계정 ID 검증 (영문, 숫자, _ 만 허용)"""
        if not value:
            return None

        value_str = str(value)

        # 길이 검증
        if len(value_str) < min_length:
            return f'계정 ID는 {min_length}자 이상이어야 합니다.'
        if len(value_str) > max_length:
            return f'계정 ID는 {max_length}자를 초과할 수 없습니다.'

        # 형식 검증 (영문, 숫자, _ 만 허용)
        if not re.match(r'^[a-zA-Z0-9_]+$', value_str):
            return '계정 ID는 영문, 숫자, 밑줄(_)만 사용 가능합니다.'

        return None

    def _get_field_label(self, field: str) -> str:
        """필드 라벨 조회"""
        # 필드명 → 한글 라벨 매핑
        labels = {
            'name': '이름',
            'name_hanja': '한자이름',
            'english_name': '영문이름',
            'rrn': '주민등록번호',
            'birth_date': '생년월일',
            'gender': '성별',
            'nationality': '국적',
            'phone': '전화번호',
            'emergency_phone': '비상연락처',
            'email': '이메일',
            'personal_email': '개인이메일',
            'address': '주소',
            'address_detail': '상세주소',
            'organization_id': '조직',
            'department': '부서',
            'position': '직위',
            'duty': '직책',
            'job_grade': '직급',
            'job_role': '직무',
            'work_location': '근무지',
            'hire_date': '입사일',
            'contract_start_date': '계약시작일',
            'contract_end_date': '계약종료일',
            'employee_type': '직원유형',
            'work_type': '근무형태',
            'contract_type': '계약유형',
            'probation_end_date': '수습종료일',
            'annual_salary': '연봉',
            'base_salary': '기본급',
            'allowances': '수당',
            'bonus': '상여금',
            'salary_account_bank': '급여계좌은행',
            'salary_account_number': '급여계좌번호',
            'salary_account_holder': '예금주',
            'health_insurance': '건강보험',
            'national_pension': '국민연금',
            'employment_insurance': '고용보험',
            'industrial_accident_insurance': '산재보험',
            'retirement_pension_type': '퇴직연금유형',
            'military_status': '병역상태',
            'military_branch': '군별',
            'military_rank': '계급',
            'military_start_date': '복무시작일',
            'military_end_date': '복무종료일',
            'military_exemption_reason': '면제사유',
            'username': '아이디',
            # 신규 직원 등록용 (Phase 2)
            'account_username': '계정 ID',
            'account_email': '계정 이메일',
        }
        return labels.get(field, field)


# 싱글톤 인스턴스
validation_service = SectionValidationService()


# 편의 함수
def validate_section(section: str, data: Dict, strict: bool = False) -> Dict[str, str]:
    """섹션 데이터 유효성 검사 (편의 함수)"""
    return validation_service.validate_section(section, data, strict)


__all__ = [
    'SectionValidationService',
    'validation_service',
    'validate_section',
]
