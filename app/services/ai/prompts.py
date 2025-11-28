"""
AI 프롬프트 템플릿

문서 분석을 위한 프롬프트들을 정의합니다.
"""

# 문서 유형 감지 프롬프트
DOCUMENT_TYPE_DETECTION_PROMPT = """
당신은 한국 HR 시스템의 문서 분석 전문가입니다.
이 이미지/문서를 분석하여 문서 유형을 판별해주세요.

가능한 문서 유형:
- resume: 이력서, 자기소개서
- career_certificate: 경력증명서, 재직증명서
- education_certificate: 졸업증명서, 학위증명서, 성적증명서
- id_card: 주민등록증, 운전면허증, 여권
- bank_statement: 통장사본, 급여명세서
- photo: 증명사진
- other: 기타 문서

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "문서유형",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "reasoning": "판단 근거"
}
"""

# 이력서 분석 프롬프트
RESUME_EXTRACTION_PROMPT = """
당신은 한국 HR 시스템의 이력서 분석 전문가입니다.
이 이력서에서 다음 정보를 추출해주세요.

추출할 필드:
- name: 이름 (한글)
- name_en: 영문 이름 (있는 경우)
- birth_date: 생년월일 (YYYY-MM-DD 형식)
- gender: 성별 (male/female)
- phone: 전화번호
- email: 이메일
- address: 주소
- education: 학력 목록 [{
    "school_name": "학교명",
    "major": "전공",
    "degree": "학위(고졸/전문학사/학사/석사/박사)",
    "graduation_date": "졸업일",
    "status": "졸업/재학/중퇴/휴학"
}]
- careers: 경력 목록 [{
    "company_name": "회사명",
    "department": "부서",
    "position": "직위",
    "start_date": "입사일",
    "end_date": "퇴사일",
    "description": "업무내용"
}]
- certificates: 자격증 목록 [{
    "name": "자격증명",
    "issuer": "발급기관",
    "issue_date": "취득일",
    "number": "자격증번호"
}]
- skills: 기술/역량 목록

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "resume",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "extracted_fields": {
        // 위 필드들
    }
}
"""

# 경력증명서 분석 프롬프트
CAREER_CERTIFICATE_PROMPT = """
당신은 한국 HR 시스템의 문서 분석 전문가입니다.
이 경력증명서/재직증명서에서 다음 정보를 추출해주세요.

추출할 필드:
- employee_name: 직원 이름
- company_name: 회사명
- department: 부서
- position: 직위/직급
- start_date: 입사일 (YYYY-MM-DD)
- end_date: 퇴사일 (YYYY-MM-DD, 재직중이면 null)
- employment_type: 고용형태 (정규직/계약직/인턴 등)
- issue_date: 발급일
- issuer: 발급자/발급기관
- certificate_number: 증명서 번호 (있는 경우)

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "career_certificate",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "extracted_fields": {
        // 위 필드들
    }
}
"""

# 학력증명서 분석 프롬프트
EDUCATION_CERTIFICATE_PROMPT = """
당신은 한국 HR 시스템의 문서 분석 전문가입니다.
이 졸업증명서/학위증명서에서 다음 정보를 추출해주세요.

추출할 필드:
- student_name: 학생 이름
- birth_date: 생년월일 (YYYY-MM-DD)
- school_name: 학교명
- major: 전공/학과
- degree: 학위 (고졸/전문학사/학사/석사/박사)
- admission_date: 입학일 (YYYY-MM-DD)
- graduation_date: 졸업일 (YYYY-MM-DD)
- status: 상태 (졸업/수료/재학/휴학)
- certificate_number: 증명서 번호
- issue_date: 발급일

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "education_certificate",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "extracted_fields": {
        // 위 필드들
    }
}
"""

# 신분증 분석 프롬프트
ID_CARD_PROMPT = """
당신은 한국 HR 시스템의 문서 분석 전문가입니다.
이 신분증(주민등록증/운전면허증/여권)에서 다음 정보를 추출해주세요.

추출할 필드:
- id_type: 신분증 유형 (resident_card/driver_license/passport)
- name: 이름
- name_en: 영문 이름 (여권인 경우)
- birth_date: 생년월일 (YYYY-MM-DD)
- gender: 성별 (male/female)
- address: 주소 (주민등록증인 경우)
- issue_date: 발급일
- expiry_date: 만료일 (해당되는 경우)
- id_number_masked: 주민등록번호 앞 6자리 (개인정보 보호를 위해 뒷자리는 마스킹)

주의: 개인정보 보호를 위해 주민등록번호 뒷자리, 여권번호 전체는 추출하지 마세요.

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "id_card",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "extracted_fields": {
        // 위 필드들
    }
}
"""

# 통장사본 분석 프롬프트
BANK_STATEMENT_PROMPT = """
당신은 한국 HR 시스템의 문서 분석 전문가입니다.
이 통장사본/급여명세서에서 다음 정보를 추출해주세요.

추출할 필드:
- account_holder: 예금주
- bank_name: 은행명
- account_number_masked: 계좌번호 (중간 자리 마스킹)

주의: 개인정보 보호를 위해 전체 계좌번호는 추출하지 마세요.

다음 JSON 형식으로 응답해주세요:
{
    "document_type": "bank_statement",
    "confidence": 0.0~1.0 사이의 신뢰도,
    "extracted_fields": {
        // 위 필드들
    }
}
"""

# 프롬프트 매핑
PROMPTS = {
    "auto_detect": DOCUMENT_TYPE_DETECTION_PROMPT,
    "resume": RESUME_EXTRACTION_PROMPT,
    "career_certificate": CAREER_CERTIFICATE_PROMPT,
    "education_certificate": EDUCATION_CERTIFICATE_PROMPT,
    "id_card": ID_CARD_PROMPT,
    "bank_statement": BANK_STATEMENT_PROMPT,
}


def get_prompt(document_type: str) -> str:
    """문서 유형에 맞는 프롬프트 반환"""
    return PROMPTS.get(document_type, DOCUMENT_TYPE_DETECTION_PROMPT)
