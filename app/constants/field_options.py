"""
Field Options - 폼 선택 옵션 상수 정의 (SSOT 원칙)

템플릿에서 하드코딩된 select 옵션을 중앙화하여 관리합니다.
Jinja2 템플릿에서 loop로 렌더링하여 일관성을 유지합니다.

SSOT 통합:
- 옵션 정의 (Option)
- 레거시 매핑 (LEGACY_MAP)
- 레이블 조회 (get_label, get_label_with_legacy)
"""
from collections import namedtuple

# 옵션 정의용 namedtuple (value: DB 저장값, label: UI 표시값)
Option = namedtuple('Option', ['value', 'label'])


class FieldOptions:
    """폼 필드 선택 옵션 중앙 관리"""

    # ========================================
    # 기본정보 옵션
    # ========================================

    # 성별 옵션
    GENDER = [
        Option('남', '남성'),
        Option('여', '여성'),
    ]

    # 결혼 여부 옵션
    MARITAL_STATUS = [
        Option('미혼', '미혼'),
        Option('기혼', '기혼'),
        Option('이혼', '이혼'),
        Option('사별', '사별'),
    ]

    # 국적 옵션
    NATIONALITY = [
        Option('대한민국', '대한민국'),
        Option('미국', '미국'),
        Option('중국', '중국'),
        Option('일본', '일본'),
        Option('베트남', '베트남'),
        Option('기타', '기타'),
    ]

    # 혈액형 옵션
    BLOOD_TYPE = [
        Option('A', 'A형'),
        Option('B', 'B형'),
        Option('O', 'O형'),
        Option('AB', 'AB형'),
    ]

    # ========================================
    # 계약/고용 옵션
    # ========================================

    # 재직 상태 옵션
    EMPLOYEE_STATUS = [
        Option('active', '정상'),
        Option('pending_info', '정보입력대기'),
        Option('pending_contract', '계약대기'),
        Option('warning', '대기'),
        Option('expired', '만료'),
        Option('resigned', '퇴사'),
    ]

    # 주간 근무시간 옵션
    WORKING_HOURS = [
        Option('40', '주 40시간'),
        Option('35', '주 35시간'),
        Option('30', '주 30시간'),
        Option('20', '주 20시간'),
        Option('15', '주 15시간'),
    ]

    # 휴게시간 옵션
    BREAK_TIME = [
        Option('60', '60분'),
        Option('30', '30분'),
        Option('0', '없음'),
    ]

    # 고용 형태 옵션
    EMPLOYMENT_TYPE = [
        Option('regular', '정규직'),
        Option('contract', '계약직'),
        Option('parttime', '파트타임'),
        Option('intern', '인턴'),
    ]

    # 계약 유형 옵션 (PersonContract용)
    CONTRACT_TYPE = [
        Option('employment', '정규직'),
        Option('contract', '계약직'),
        Option('freelance', '프리랜서'),
        Option('intern', '인턴'),
    ]

    # 계약 상태 옵션 (PersonCorporateContract.status용)
    CONTRACT_STATUS = [
        Option('requested', '계약진행중'),
        Option('approved', '계약완료'),
        Option('rejected', '거절됨'),
        Option('terminated', '종료됨'),
        Option('expired', '만료됨'),
    ]

    # ========================================
    # 학력정보 옵션
    # ========================================

    # 학위 옵션
    DEGREE = [
        Option('고졸', '고등학교 졸업'),
        Option('전문학사', '전문학사'),
        Option('학사', '학사'),
        Option('석사', '석사'),
        Option('박사', '박사'),
    ]

    # 졸업 상태 옵션
    GRADUATION_STATUS = [
        Option('졸업', '졸업'),
        Option('재학', '재학'),
        Option('휴학', '휴학'),
        Option('중퇴', '중퇴'),
    ]

    # ========================================
    # 경력정보 옵션
    # ========================================

    # 급여 유형 옵션
    SALARY_TYPE = [
        Option('연봉제', '연봉제'),
        Option('월급제', '월급제'),
        Option('시급제', '시급제'),
        Option('호봉제', '호봉제'),
    ]

    # ========================================
    # 가족사항 옵션
    # ========================================

    # 가족 관계 옵션
    FAMILY_RELATION = [
        Option('배우자', '배우자'),
        Option('자녀', '자녀'),
        Option('부', '부'),
        Option('모', '모'),
        Option('형제', '형제'),
        Option('자매', '자매'),
    ]

    # 동거여부 옵션
    COHABIT = [
        Option('동거', '동거'),
        Option('별거', '별거'),
    ]

    # ========================================
    # 언어능력 옵션
    # ========================================

    # 언어 목록 옵션
    LANGUAGE = [
        Option('영어', '영어'),
        Option('일본어', '일본어'),
        Option('중국어', '중국어'),
        Option('스페인어', '스페인어'),
        Option('프랑스어', '프랑스어'),
        Option('독일어', '독일어'),
        Option('러시아어', '러시아어'),
        Option('베트남어', '베트남어'),
        Option('태국어', '태국어'),
        Option('기타', '기타'),
    ]

    # 언어 수준 옵션
    LANGUAGE_LEVEL = [
        Option('원어민', '원어민'),
        Option('고급', '상'),
        Option('중급', '중'),
        Option('초급', '하'),
    ]

    # ========================================
    # 병역정보 옵션
    # ========================================

    # 병역 상태 옵션
    MILITARY_STATUS = [
        Option('군필', '군필'),
        Option('만기전역', '만기전역'),
        Option('의가사전역', '의가사전역'),
        Option('병역면제', '병역면제'),
        Option('면제', '면제'),
        Option('복무중', '복무중'),
        Option('미필', '미필'),
        Option('해당없음', '해당없음'),
    ]

    # 군별 옵션
    MILITARY_BRANCH = [
        Option('육군', '육군'),
        Option('해군', '해군'),
        Option('공군', '공군'),
        Option('해병대', '해병대'),
        Option('의무경찰', '의무경찰'),
        Option('사회복무요원', '사회복무요원'),
    ]

    # ========================================
    # 레거시 매핑 (하위 호환용)
    # ========================================
    # 영문코드 → DB 저장값(한글) 변환
    LEGACY_MAP = {
        # 성별
        'male': '남',
        'female': '여',
        'M': '남',
        'F': '여',

        # 결혼여부
        'single': '미혼',
        'married': '기혼',
        'divorced': '이혼',
        'widowed': '사별',

        # 국적
        'kr': '대한민국',
        'KR': '대한민국',
        'korea': '대한민국',
        'us': '미국',
        'US': '미국',
        'usa': '미국',
        'jp': '일본',
        'JP': '일본',
        'japan': '일본',
        'cn': '중국',
        'CN': '중국',
        'china': '중국',
        'vn': '베트남',
        'VN': '베트남',

        # 학위
        'high_school': '고졸',
        'associate': '전문학사',
        'bachelor': '학사',
        'master': '석사',
        'doctor': '박사',
        'phd': '박사',

        # 졸업상태
        'graduated': '졸업',
        'enrolled': '재학',
        'on_leave': '휴학',
        'dropped': '중퇴',

        # 급여유형 (JS templates.js 호환)
        'annual': '연봉제',
        'monthly': '월급제',
        'hourly': '시급제',
        'pay_step': '호봉제',

        # 가족관계
        'spouse': '배우자',
        'child': '자녀',
        'parent': '부',
        'father': '부',
        'mother': '모',
        'sibling': '형제',
        'brother': '형제',
        'sister': '자매',
        'grandparent': '기타',
        'other': '기타',

        # 동거여부 (JS boolean 문자열 호환)
        'true': '동거',
        'false': '별거',
        True: '동거',
        False: '별거',

        # 언어수준
        'native': '원어민',
        'advanced': '고급',
        'intermediate': '중급',
        'beginner': '초급',

        # 병역상태
        'completed': '군필',
        'exempted': '면제',
        'serving': '복무중',
        'not_applicable': '해당없음',

        # 재직상태 레거시 (한글 → 영문 표준값)
        '재직': 'active',
        '퇴사': 'resigned',

        # 군별
        'army': '육군',
        'navy': '해군',
        'airforce': '공군',
        'air_force': '공군',
        'marine': '해병대',
        'auxiliary': '사회복무요원',
    }

    @classmethod
    def get_all(cls):
        """모든 옵션을 딕셔너리로 반환 (context_processor용)"""
        return {
            # 기본정보
            'GENDER_OPTIONS': cls.GENDER,
            'MARITAL_STATUS_OPTIONS': cls.MARITAL_STATUS,
            'NATIONALITY_OPTIONS': cls.NATIONALITY,
            'BLOOD_TYPE_OPTIONS': cls.BLOOD_TYPE,
            # 계약정보
            'EMPLOYEE_STATUS_OPTIONS': cls.EMPLOYEE_STATUS,
            'EMPLOYMENT_TYPE_OPTIONS': cls.EMPLOYMENT_TYPE,
            'CONTRACT_TYPE_OPTIONS': cls.CONTRACT_TYPE,
            'CONTRACT_STATUS_OPTIONS': cls.CONTRACT_STATUS,
            'WORKING_HOURS_OPTIONS': cls.WORKING_HOURS,
            'BREAK_TIME_OPTIONS': cls.BREAK_TIME,
            # 학력정보
            'DEGREE_OPTIONS': cls.DEGREE,
            'GRADUATION_STATUS_OPTIONS': cls.GRADUATION_STATUS,
            # 경력정보
            'SALARY_TYPE_OPTIONS': cls.SALARY_TYPE,
            # 가족사항
            'FAMILY_RELATION_OPTIONS': cls.FAMILY_RELATION,
            'COHABIT_OPTIONS': cls.COHABIT,
            # 언어능력
            'LANGUAGE_OPTIONS': cls.LANGUAGE,
            'LANGUAGE_LEVEL_OPTIONS': cls.LANGUAGE_LEVEL,
            # 병역정보
            'MILITARY_STATUS_OPTIONS': cls.MILITARY_STATUS,
            'MILITARY_BRANCH_OPTIONS': cls.MILITARY_BRANCH,
        }

    @classmethod
    def get_label(cls, option_list, value):
        """값에 해당하는 레이블 반환"""
        for opt in option_list:
            if opt.value == value:
                return opt.label
        return value

    @classmethod
    def get_values(cls, option_list):
        """옵션 리스트에서 값만 추출"""
        return [opt.value for opt in option_list]

    @classmethod
    def get_label_with_legacy(cls, option_list, value):
        """
        레거시 매핑을 포함한 레이블 조회 (SSOT 통합)

        Args:
            option_list: 옵션 리스트 (예: FieldOptions.GENDER)
            value: 조회할 값 (DB값 또는 레거시 코드)

        Returns:
            레이블 문자열 또는 '정보 없음'

        엣지 케이스:
            - None → '정보 없음'
            - '' (빈 문자열) → '정보 없음'
            - 레거시 코드 → 변환 후 레이블 조회
            - 옵션에 없는 값 → 원본값 반환 (하위 호환)
        """
        # None 또는 빈 문자열 처리
        if value is None or value == '':
            return '정보 없음'

        # 레거시 코드 변환
        if value in cls.LEGACY_MAP:
            value = cls.LEGACY_MAP[value]

        # 옵션에서 레이블 조회
        for opt in option_list:
            if opt.value == value:
                return opt.label

        # 매칭 안되면 원본값 반환 (하위 호환)
        return value

    @classmethod
    def get_labels_dict(cls, option_list):
        """옵션 리스트를 {value: label} 딕셔너리로 반환"""
        return {opt.value: opt.label for opt in option_list}
