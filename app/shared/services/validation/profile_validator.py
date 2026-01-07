"""
Profile Basic Info Validator

Phase 9: app/shared/services/validation/으로 이동
Phase 28: 기본 정보 섹션 검증 서비스

기능:
- 필수 필드 검증
- 주민등록번호 형식/체크섬 검증
- 전화번호 형식 검증
- 이메일 형식 검증
- RRN-생년월일-성별 일관성 검증
"""
import re
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Any

from app.shared.base.service_result import ServiceResult
from app.shared.utils.rrn_parser import RRNParser, RRNParseResult


@dataclass
class ValidationError:
    """검증 오류 정보"""
    field: str
    message: str
    code: str


@dataclass
class ValidationResult:
    """검증 결과"""
    is_valid: bool
    errors: List[ValidationError] = field(default_factory=list)
    parsed_rrn: Optional[RRNParseResult] = None

    def add_error(self, field_name: str, message: str, code: str = "INVALID"):
        """오류 추가"""
        self.errors.append(ValidationError(field=field_name, message=message, code=code))
        self.is_valid = False

    def to_dict(self) -> Dict[str, Any]:
        """딕셔너리 변환"""
        return {
            'is_valid': self.is_valid,
            'errors': [
                {'field': e.field, 'message': e.message, 'code': e.code}
                for e in self.errors
            ],
            'parsed_rrn': {
                'birth_date': self.parsed_rrn.birth_date,
                'age': self.parsed_rrn.age,
                'gender': self.parsed_rrn.gender,
            } if self.parsed_rrn and self.parsed_rrn.is_valid else None
        }


class ProfileBasicInfoValidator:
    """
    프로필 기본 정보 검증기

    Phase 28 필수 필드:
    - name: 이름
    - english_name: 영문이름
    - resident_number: 주민등록번호
    - mobile_phone: 휴대전화
    - email: 이메일
    - address: 주민등록상 주소
    - actual_address: 실제거주 주소
    """

    # 필수 필드 정의
    REQUIRED_FIELDS = {
        'name': '이름',
        'english_name': '영문이름',
        'resident_number': '주민등록번호',
        'mobile_phone': '휴대전화',
        'email': '이메일',
        'address': '주민등록상 주소',
        'actual_address': '실제거주 주소',
    }

    # 전화번호 패턴 (한국 형식)
    PHONE_PATTERN = re.compile(
        r'^(\d{2,3})-?(\d{3,4})-?(\d{4})$'
    )

    # 이메일 패턴
    EMAIL_PATTERN = re.compile(
        r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    )

    @classmethod
    def validate(cls, data: Dict[str, Any], strict: bool = False) -> ValidationResult:
        """
        기본 정보 검증 (메인 메서드)

        Args:
            data: 검증할 데이터 딕셔너리
            strict: True면 모든 필수 필드 검증, False면 입력된 필드만 검증

        Returns:
            ValidationResult: 검증 결과
        """
        result = ValidationResult(is_valid=True)

        # 1. 필수 필드 검증 (strict 모드일 때만)
        if strict:
            cls._validate_required_fields(data, result)

        # 2. 주민등록번호 검증 (입력된 경우)
        if data.get('resident_number'):
            cls._validate_resident_number(data, result)

        # 3. 전화번호 검증 (입력된 경우)
        if data.get('mobile_phone'):
            cls._validate_phone(data.get('mobile_phone'), 'mobile_phone', '휴대전화', result)
        if data.get('home_phone'):
            cls._validate_phone(data.get('home_phone'), 'home_phone', '자택전화', result)
        if data.get('emergency_contact'):
            cls._validate_phone(data.get('emergency_contact'), 'emergency_contact', '비상연락처', result)

        # 4. 이메일 검증 (입력된 경우)
        if data.get('email'):
            cls._validate_email(data.get('email'), result)

        # 5. 일관성 검증 (RRN 파싱 결과가 있고, birth_date/gender가 직접 입력된 경우)
        if result.parsed_rrn and result.parsed_rrn.is_valid:
            cls._validate_consistency(data, result)

        return result

    @classmethod
    def _validate_required_fields(cls, data: Dict[str, Any], result: ValidationResult):
        """필수 필드 검증"""
        for field_name, label in cls.REQUIRED_FIELDS.items():
            value = data.get(field_name)
            if not value or (isinstance(value, str) and not value.strip()):
                result.add_error(
                    field_name,
                    f'{label}은(는) 필수 입력 항목입니다.',
                    'REQUIRED'
                )

    @classmethod
    def _validate_resident_number(cls, data: Dict[str, Any], result: ValidationResult):
        """
        주민등록번호 검증

        검증 항목:
        - 형식 검증 (13자리)
        - 날짜 유효성 검증
        - 성별코드 검증
        - 체크섬 검증
        """
        rrn = data.get('resident_number', '')

        # RRNParser로 검증
        parse_result = RRNParser.parse(rrn)

        if not parse_result.is_valid:
            result.add_error(
                'resident_number',
                parse_result.error_message or '유효하지 않은 주민등록번호입니다.',
                'INVALID_RRN'
            )
        else:
            # 파싱 결과 저장 (자동 입력에 사용)
            result.parsed_rrn = parse_result

    @classmethod
    def _validate_phone(cls, phone: str, field_name: str, label: str, result: ValidationResult):
        """
        전화번호 형식 검증

        허용 형식:
        - 010-1234-5678
        - 01012345678
        - 02-123-4567
        - 031-1234-5678
        """
        if not phone:
            return

        # 숫자와 하이픈만 추출
        cleaned = re.sub(r'[^\d-]', '', phone)

        if not cls.PHONE_PATTERN.match(cleaned):
            result.add_error(
                field_name,
                f'{label} 형식이 올바르지 않습니다. (예: 010-1234-5678)',
                'INVALID_PHONE'
            )

    @classmethod
    def _validate_email(cls, email: str, result: ValidationResult):
        """이메일 형식 검증"""
        if not email:
            return

        if not cls.EMAIL_PATTERN.match(email):
            result.add_error(
                'email',
                '이메일 형식이 올바르지 않습니다.',
                'INVALID_EMAIL'
            )

    @classmethod
    def _validate_consistency(cls, data: Dict[str, Any], result: ValidationResult):
        """
        RRN-생년월일-성별 일관성 검증

        주민등록번호에서 파싱한 값과 직접 입력된 값이 불일치하면 경고
        """
        if not result.parsed_rrn or not result.parsed_rrn.is_valid:
            return

        # 생년월일 일관성 체크
        input_birth = data.get('birth_date')
        if input_birth and input_birth != result.parsed_rrn.birth_date:
            result.add_error(
                'birth_date',
                f'생년월일이 주민등록번호와 일치하지 않습니다. '
                f'(주민번호 기준: {result.parsed_rrn.birth_date})',
                'INCONSISTENT'
            )

        # 성별 일관성 체크
        input_gender = data.get('gender')
        if input_gender and input_gender != result.parsed_rrn.gender:
            result.add_error(
                'gender',
                f'성별이 주민등록번호와 일치하지 않습니다. '
                f'(주민번호 기준: {result.parsed_rrn.gender})',
                'INCONSISTENT'
            )

    @classmethod
    def extract_auto_fields(cls, rrn: str) -> Optional[Dict[str, Any]]:
        """
        주민등록번호에서 자동 입력 필드 추출

        Args:
            rrn: 주민등록번호

        Returns:
            Optional[Dict]: 자동 입력 필드 (birth_date, age, gender)
        """
        parse_result = RRNParser.parse(rrn)

        if not parse_result.is_valid:
            return None

        return {
            'birth_date': parse_result.birth_date,
            'age': parse_result.age,
            'gender': parse_result.gender,
        }


def validate_profile_basic_info(data: Dict[str, Any], strict: bool = False) -> ServiceResult:
    """
    프로필 기본 정보 검증 (편의 함수)

    Args:
        data: 검증할 데이터
        strict: 필수 필드 검증 여부

    Returns:
        ServiceResult: 성공 시 검증 결과, 실패 시 오류 정보
    """
    result = ProfileBasicInfoValidator.validate(data, strict=strict)

    if result.is_valid:
        return ServiceResult.ok(
            data=result.to_dict(),
            message="검증 통과"
        )
    else:
        return ServiceResult.fail(
            message="검증 실패",
            error_code="VALIDATION_ERROR",
            error_details=result.to_dict()
        )


__all__ = [
    'ProfileBasicInfoValidator',
    'ValidationResult',
    'ValidationError',
    'validate_profile_basic_info',
]
