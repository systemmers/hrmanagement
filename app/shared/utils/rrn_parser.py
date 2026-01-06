"""
RRN (Resident Registration Number) 파서 유틸리티

Phase 28: 주민등록번호 파싱 및 검증

기능:
- 형식 검증 (13자리)
- 날짜 유효성 검증
- 성별코드 검증 (1-8)
- 체크섬 검증 (Luhn 변형)
- 생년월일 추출
- 나이 계산 (만 나이)
- 성별 추출
- 마스킹 함수
"""
from dataclasses import dataclass
from datetime import datetime, date
from typing import Optional, Tuple
import re


@dataclass
class RRNParseResult:
    """RRN 파싱 결과"""
    is_valid: bool
    birth_date: Optional[str] = None  # YYYY-MM-DD 형식
    age: Optional[int] = None  # 만 나이
    gender: Optional[str] = None  # '남' 또는 '여'
    error_message: Optional[str] = None


class RRNParser:
    """주민등록번호 파서 클래스"""

    # 체크섬 가중치 (주민번호 각 자리에 곱할 값)
    CHECKSUM_WEIGHTS = [2, 3, 4, 5, 6, 7, 8, 9, 2, 3, 4, 5]

    # 성별코드 매핑
    GENDER_MAP = {
        '1': '남',  # 1900년대 남성
        '2': '여',  # 1900년대 여성
        '3': '남',  # 2000년대 남성
        '4': '여',  # 2000년대 여성
        '5': '남',  # 1900년대 외국인 남성
        '6': '여',  # 1900년대 외국인 여성
        '7': '남',  # 2000년대 외국인 남성
        '8': '여',  # 2000년대 외국인 여성
    }

    # 세기 코드 매핑 (성별코드 -> 세기)
    CENTURY_MAP = {
        '1': 1900, '2': 1900,
        '3': 2000, '4': 2000,
        '5': 1900, '6': 1900,
        '7': 2000, '8': 2000,
        '9': 1800, '0': 1800,  # 1800년대 (거의 사용 안함)
    }

    @classmethod
    def parse(cls, rrn: str) -> RRNParseResult:
        """
        주민등록번호 파싱 (메인 메서드)

        Args:
            rrn: 주민등록번호 (하이픈 포함/미포함)

        Returns:
            RRNParseResult: 파싱 결과
        """
        # 형식 검증
        format_result = cls.validate_format(rrn)
        if not format_result[0]:
            return RRNParseResult(is_valid=False, error_message=format_result[1])

        # 정규화 (숫자만)
        digits = cls._normalize(rrn)

        # 날짜 검증
        date_result = cls.validate_date(digits)
        if not date_result[0]:
            return RRNParseResult(is_valid=False, error_message=date_result[1])

        # 성별코드 검증
        gender_result = cls.validate_gender_code(digits)
        if not gender_result[0]:
            return RRNParseResult(is_valid=False, error_message=gender_result[1])

        # 체크섬 검증
        checksum_result = cls.validate_checksum(digits)
        if not checksum_result[0]:
            return RRNParseResult(is_valid=False, error_message=checksum_result[1])

        # 정보 추출
        birth_date = cls.extract_birth_date(digits)
        age = cls.calculate_age(birth_date)
        gender = cls.extract_gender(digits)

        return RRNParseResult(
            is_valid=True,
            birth_date=birth_date,
            age=age,
            gender=gender
        )

    @classmethod
    def _normalize(cls, rrn: str) -> str:
        """주민번호에서 숫자만 추출"""
        return re.sub(r'[^0-9]', '', rrn)

    @classmethod
    def validate_format(cls, rrn: str) -> Tuple[bool, Optional[str]]:
        """
        형식 검증 (13자리 숫자)

        Returns:
            Tuple[bool, Optional[str]]: (유효성, 에러메시지)
        """
        if not rrn:
            return False, "주민등록번호를 입력해주세요."

        digits = cls._normalize(rrn)

        if len(digits) != 13:
            return False, "주민등록번호는 13자리여야 합니다."

        if not digits.isdigit():
            return False, "주민등록번호는 숫자만 입력 가능합니다."

        return True, None

    @classmethod
    def validate_date(cls, digits: str) -> Tuple[bool, Optional[str]]:
        """
        날짜 유효성 검증 (앞 6자리)

        Args:
            digits: 정규화된 13자리 숫자

        Returns:
            Tuple[bool, Optional[str]]: (유효성, 에러메시지)
        """
        if len(digits) != 13:
            return False, "잘못된 주민등록번호 형식입니다."

        yy = digits[0:2]
        mm = digits[2:4]
        dd = digits[4:6]
        gender_code = digits[6]

        # 세기 결정
        century = cls.CENTURY_MAP.get(gender_code, 1900)
        year = century + int(yy)

        try:
            birth = datetime(year, int(mm), int(dd))

            # 미래 날짜 검증
            if birth.date() > date.today():
                return False, "생년월일이 미래 날짜입니다."

            # 너무 오래된 날짜 검증 (150세 이상)
            if (date.today().year - birth.year) > 150:
                return False, "유효하지 않은 생년월일입니다."

            return True, None

        except ValueError:
            return False, f"유효하지 않은 날짜입니다: {year}-{mm}-{dd}"

    @classmethod
    def validate_gender_code(cls, digits: str) -> Tuple[bool, Optional[str]]:
        """
        성별코드 검증 (7번째 자리: 1-8)

        Args:
            digits: 정규화된 13자리 숫자

        Returns:
            Tuple[bool, Optional[str]]: (유효성, 에러메시지)
        """
        if len(digits) != 13:
            return False, "잘못된 주민등록번호 형식입니다."

        gender_code = digits[6]

        if gender_code not in cls.GENDER_MAP:
            return False, f"유효하지 않은 성별 코드입니다: {gender_code}"

        return True, None

    @classmethod
    def validate_checksum(cls, digits: str) -> Tuple[bool, Optional[str]]:
        """
        체크섬 검증 (Luhn 변형 알고리즘)

        알고리즘:
        1. 앞 12자리에 가중치 [2,3,4,5,6,7,8,9,2,3,4,5] 곱함
        2. 합계를 11로 나눈 나머지 계산
        3. 11 - 나머지 = 체크디짓 (10 이상이면 10으로 나눈 나머지)
        4. 계산된 체크디짓과 마지막 자리 비교

        Args:
            digits: 정규화된 13자리 숫자

        Returns:
            Tuple[bool, Optional[str]]: (유효성, 에러메시지)
        """
        if len(digits) != 13:
            return False, "잘못된 주민등록번호 형식입니다."

        # 가중치 합계 계산
        total = sum(
            int(digits[i]) * cls.CHECKSUM_WEIGHTS[i]
            for i in range(12)
        )

        # 체크디짓 계산
        remainder = total % 11
        check_digit = (11 - remainder) % 10

        # 마지막 자리와 비교
        if check_digit != int(digits[12]):
            return False, "주민등록번호 체크섬이 일치하지 않습니다."

        return True, None

    @classmethod
    def extract_birth_date(cls, digits: str) -> Optional[str]:
        """
        생년월일 추출 (YYYY-MM-DD 형식)

        Args:
            digits: 정규화된 13자리 숫자

        Returns:
            Optional[str]: 생년월일 문자열 (YYYY-MM-DD)
        """
        if len(digits) != 13:
            return None

        yy = digits[0:2]
        mm = digits[2:4]
        dd = digits[4:6]
        gender_code = digits[6]

        century = cls.CENTURY_MAP.get(gender_code, 1900)
        year = century + int(yy)

        return f"{year:04d}-{mm}-{dd}"

    @classmethod
    def calculate_age(cls, birth_date: Optional[str], reference_date: Optional[date] = None) -> Optional[int]:
        """
        만 나이 계산

        Args:
            birth_date: 생년월일 (YYYY-MM-DD 형식)
            reference_date: 기준일 (기본: 오늘)

        Returns:
            Optional[int]: 만 나이
        """
        if not birth_date:
            return None

        try:
            birth = datetime.strptime(birth_date, '%Y-%m-%d').date()
            today = reference_date or date.today()

            age = today.year - birth.year

            # 생일이 지나지 않았으면 1살 감소
            if (today.month, today.day) < (birth.month, birth.day):
                age -= 1

            return age

        except ValueError:
            return None

    @classmethod
    def extract_gender(cls, digits: str) -> Optional[str]:
        """
        성별 추출

        Args:
            digits: 정규화된 13자리 숫자

        Returns:
            Optional[str]: '남' 또는 '여'
        """
        if len(digits) != 13:
            return None

        gender_code = digits[6]
        return cls.GENDER_MAP.get(gender_code)

    @classmethod
    def mask(cls, rrn: str, mask_char: str = '*') -> str:
        """
        주민등록번호 마스킹 (뒷자리 6자리)

        Args:
            rrn: 주민등록번호
            mask_char: 마스킹 문자 (기본: *)

        Returns:
            str: 마스킹된 주민등록번호 (예: 900101-1******)
        """
        if not rrn:
            return ''

        digits = cls._normalize(rrn)

        if len(digits) != 13:
            return rrn  # 잘못된 형식은 그대로 반환

        # 앞 6자리 + 성별코드 + 마스킹 6자리
        return f"{digits[:6]}-{digits[6]}{mask_char * 6}"

    @classmethod
    def format_with_hyphen(cls, rrn: str) -> str:
        """
        주민등록번호 하이픈 포맷팅

        Args:
            rrn: 주민등록번호 (13자리)

        Returns:
            str: 하이픈 포함 형식 (예: 900101-1234567)
        """
        digits = cls._normalize(rrn)

        if len(digits) != 13:
            return rrn

        return f"{digits[:6]}-{digits[6:]}"

    @classmethod
    def is_foreigner(cls, rrn: str) -> bool:
        """
        외국인 여부 확인

        Args:
            rrn: 주민등록번호

        Returns:
            bool: 외국인 여부
        """
        digits = cls._normalize(rrn)

        if len(digits) != 13:
            return False

        gender_code = digits[6]
        return gender_code in ('5', '6', '7', '8')


# 편의 함수 (모듈 레벨)
def parse_rrn(rrn: str) -> RRNParseResult:
    """주민등록번호 파싱 (편의 함수)"""
    return RRNParser.parse(rrn)


def validate_rrn(rrn: str) -> Tuple[bool, Optional[str]]:
    """주민등록번호 검증 (편의 함수)"""
    result = RRNParser.parse(rrn)
    return result.is_valid, result.error_message


def mask_rrn(rrn: str) -> str:
    """주민등록번호 마스킹 (편의 함수)"""
    return RRNParser.mask(rrn)


__all__ = [
    'RRNParser',
    'RRNParseResult',
    'parse_rrn',
    'validate_rrn',
    'mask_rrn',
]
