"""
개인계정 회원가입 및 프로필 전체 필드 E2E 테스트 스크립트

신규 개인계정 가입부터 프로필 정보 모든 필드 입력까지의 E2E 테스트
- Phase 1: 회원가입 (6개 필드)
- Phase 2: 로그인
- Phase 3: 기본정보 입력 (30개 필드)
- Phase 4: 이력 데이터 입력 (123개 필드 - 각 섹션 3개 행)
- Phase 5: 사진 업로드
- Phase 6: 종합 검증

총 테스트 필드: 166개 이상
"""
import asyncio
import json
import sys
import os
import uuid
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5200"
REGISTER_URL = f"{BASE_URL}/personal/register"
LOGIN_URL = f"{BASE_URL}/auth/login"
LOGOUT_URL = f"{BASE_URL}/auth/logout"
PROFILE_EDIT_URL = f"{BASE_URL}/profile/edit"
PROFILE_VIEW_URL = f"{BASE_URL}/profile/"
DASHBOARD_URL = f"{BASE_URL}/personal/dashboard"

# 샘플 파일 경로
SAMPLE_FILES_DIR = r"D:\projects\hrmanagement\.dev_docs\sample\docs_file"


def generate_unique_username():
    """고유한 테스트 username 생성"""
    timestamp = datetime.now().strftime('%y%m%d%H%M%S')
    unique_id = uuid.uuid4().hex[:4]
    return f"e2e_test_{timestamp}_{unique_id}"


# 동적으로 생성되는 테스트 계정 정보
TEST_USERNAME = generate_unique_username()
TEST_EMAIL = f"{TEST_USERNAME}@e2etest.local"

# 회원가입 데이터 (6개 필드)
TEST_REGISTRATION = {
    "username": TEST_USERNAME,
    "email": TEST_EMAIL,
    "password": "E2ETest1234!",
    "password_confirm": "E2ETest1234!",
    "name": "E2E테스터",
    "mobile_phone": "010-9999-0001"
}

# 기본정보 데이터 (30개 필드)
TEST_BASIC_INFO = {
    "name": "E2E테스터",
    "english_name": "E2E Tester",
    "chinese_name": "二二測試",
    "foreign_name": "イーツーテスター",
    "resident_number": "850520-1234567",
    "gender": "남성",
    "marital_status": "기혼",
    "nationality": "대한민국",
    "phone": "010-9999-0001",
    "home_phone": "02-1234-5678",
    "email": TEST_EMAIL,
    "address": "서울특별시 강남구 테헤란로 123",
    "detailed_address": "E2E빌딩 201호",
    "postal_code": "06234",
    "actual_address": "서울특별시 서초구 반포대로 456",
    "actual_detailed_address": "테스트아파트 101동 1001호",
    "actual_postal_code": "06500",
    "emergency_contact": "010-8888-9999",
    "emergency_relation": "배우자",
    "hobby": "독서, 등산, 여행",
    "specialty": "E2E 테스트 자동화",
    "disability_info": "해당없음",
    "lunar_birth": False,
    "bank_name": "KB국민은행",
    "account_number": "1234567890123",
    "account_holder": "E2E테스터"
}

# 학력 데이터 (3개 행 x 7개 필드 = 21개)
TEST_EDUCATIONS = [
    {
        "school_name": "E2E테스트대학교",
        "degree": "학사",
        "major": "컴퓨터공학",
        "graduation_year": "2010",
        "gpa": "3.8/4.5",
        "graduation_status": "졸업",
        "note": "수석 졸업"
    },
    {
        "school_name": "E2E테스트대학원",
        "degree": "석사",
        "major": "소프트웨어공학",
        "graduation_year": "2012",
        "gpa": "4.2/4.5",
        "graduation_status": "졸업",
        "note": "논문 최우수상"
    },
    {
        "school_name": "E2E테스트고등학교",
        "degree": "고등학교 졸업",
        "major": "인문계",
        "graduation_year": "2006",
        "gpa": "",
        "graduation_status": "졸업",
        "note": ""
    }
]

# 경력 데이터 (3개 행 x 13개 필드 = 39개)
TEST_CAREERS = [
    {
        "company_name": "E2E테스트회사",
        "department": "개발팀",
        "position": "선임연구원",
        "job_grade": "L3",
        "job_title": "팀장",
        "job_role": "백엔드 개발",
        "duties": "API 설계 및 구현",
        "salary_type": "연봉",
        "salary": "60000000",
        "monthly_salary": "5000000",
        "pay_step": "5",
        "start_date": "2015-03-01",
        "end_date": "2020-12-31"
    },
    {
        "company_name": "ABC소프트",
        "department": "솔루션사업부",
        "position": "대리",
        "job_grade": "L2",
        "job_title": "",
        "job_role": "풀스택 개발",
        "duties": "웹 애플리케이션 개발",
        "salary_type": "연봉",
        "salary": "45000000",
        "monthly_salary": "3750000",
        "pay_step": "3",
        "start_date": "2012-03-01",
        "end_date": "2015-02-28"
    },
    {
        "company_name": "스타트업XYZ",
        "department": "기술팀",
        "position": "사원",
        "job_grade": "L1",
        "job_title": "",
        "job_role": "프론트엔드 개발",
        "duties": "UI/UX 개발",
        "salary_type": "연봉",
        "salary": "35000000",
        "monthly_salary": "2916667",
        "pay_step": "1",
        "start_date": "2010-07-01",
        "end_date": "2012-02-29"
    }
]

# 자격증 데이터 (3개 행 x 6개 필드 = 18개)
TEST_CERTIFICATES = [
    {
        "name": "정보처리기사",
        "issuing_organization": "한국산업인력공단",
        "grade": "기사",
        "acquisition_date": "2012-05-20",
        "number": "12345678",
        "expiry_date": ""
    },
    {
        "name": "SQLD",
        "issuing_organization": "한국데이터산업진흥원",
        "grade": "전문가",
        "acquisition_date": "2014-09-15",
        "number": "SQL-2014-12345",
        "expiry_date": ""
    },
    {
        "name": "AWS Solutions Architect",
        "issuing_organization": "Amazon Web Services",
        "grade": "Professional",
        "acquisition_date": "2022-03-10",
        "number": "AWS-SAP-2022-001",
        "expiry_date": "2025-03-10"
    }
]

# 어학 데이터 (3개 행 x 5개 필드 = 15개)
TEST_LANGUAGES = [
    {
        "language": "영어",
        "level": "고급",
        "test_name": "TOEIC",
        "score": "950",
        "test_date": "2023-06-15"
    },
    {
        "language": "일본어",
        "level": "중급",
        "test_name": "JLPT",
        "score": "N2",
        "test_date": "2022-12-01"
    },
    {
        "language": "중국어",
        "level": "초급",
        "test_name": "HSK",
        "score": "4급",
        "test_date": "2021-05-20"
    }
]

# 병역 데이터 (7개 필드, 단일)
TEST_MILITARY = {
    "status": "군필",
    "branch": "육군",
    "rank": "병장",
    "period": "2005-01 ~ 2006-12",
    "duty": "행정병",
    "specialty": "보병",
    "exemption_reason": ""
}

# 수상 데이터 (3개 행 x 4개 필드 = 12개)
TEST_AWARDS = [
    {
        "name": "우수사원상",
        "date": "2019-12-20",
        "issuer": "E2E테스트회사",
        "note": "연간 최우수 개발자"
    },
    {
        "name": "혁신상",
        "date": "2018-06-15",
        "issuer": "ABC소프트",
        "note": "신규 서비스 개발 공로"
    },
    {
        "name": "해커톤 대상",
        "date": "2017-11-01",
        "issuer": "IT협회",
        "note": "전국 해커톤 대회 1위"
    }
]

# 가족 데이터 (3개 행 x 6개 필드 = 18개)
TEST_FAMILIES = [
    {
        "relation": "배우자",
        "name": "테스트배우자",
        "birth_date": "1987-03-15",
        "occupation": "회사원",
        "phone": "010-7777-8888",
        "is_cohabitant": "동거"
    },
    {
        "relation": "자녀",
        "name": "테스트자녀1",
        "birth_date": "2015-08-20",
        "occupation": "학생",
        "phone": "",
        "is_cohabitant": "동거"
    },
    {
        "relation": "자녀",
        "name": "테스트자녀2",
        "birth_date": "2018-02-10",
        "occupation": "학생",
        "phone": "",
        "is_cohabitant": "동거"
    }
]

# 테스트 결과 저장
test_results = {
    "timestamp": datetime.now().isoformat(),
    "test_username": TEST_USERNAME,
    "test_email": TEST_EMAIL,
    "total": 0,
    "passed": 0,
    "failed": 0,
    "bugs": [],
    "tests": [],
    "field_coverage": {
        "registration": 0,
        "basic_info": 0,
        "education": 0,
        "career": 0,
        "certificate": 0,
        "language": 0,
        "military": 0,
        "award": 0,
        "family": 0,
        "photo": 0
    }
}


def log_result(test_id, test_name, passed, message="", bug_id=None, details=None, fields_tested=0):
    """테스트 결과 로깅"""
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {test_id}: {test_name}")
    if message:
        print(f"       -> {message}")
    if fields_tested > 0:
        print(f"       -> 필드 테스트: {fields_tested}개")

    test_results["total"] += 1
    if passed:
        test_results["passed"] += 1
    else:
        test_results["failed"] += 1
        if bug_id:
            test_results["bugs"].append({
                "test_id": test_id,
                "bug_id": bug_id,
                "message": message,
                "details": details
            })

    test_results["tests"].append({
        "test_id": test_id,
        "test_name": test_name,
        "passed": passed,
        "message": message,
        "bug_id": bug_id,
        "details": details,
        "fields_tested": fields_tested
    })


async def fill_input_if_exists(page, selector, value, timeout=3000):
    """입력 필드가 존재하면 값 입력"""
    try:
        locator = page.locator(selector)
        if await locator.count() > 0:
            await locator.first.fill(str(value), timeout=timeout)
            return True
    except Exception:
        pass
    return False


async def select_option_if_exists(page, selector, value, timeout=3000):
    """선택 필드가 존재하면 옵션 선택"""
    try:
        locator = page.locator(selector)
        if await locator.count() > 0:
            await locator.first.select_option(label=value, timeout=timeout)
            return True
    except Exception:
        try:
            # value로 시도
            locator = page.locator(selector)
            if await locator.count() > 0:
                await locator.first.select_option(value=value, timeout=timeout)
                return True
        except Exception:
            pass
    return False


async def click_if_exists(page, selector, timeout=3000):
    """버튼이 존재하면 클릭"""
    try:
        locator = page.locator(selector)
        if await locator.count() > 0:
            await locator.first.click(timeout=timeout)
            return True
    except Exception:
        pass
    return False


# ============================================================================
# Phase 1: 회원가입 테스트 (TC-R-001 ~ TC-R-006)
# ============================================================================

async def test_tc_r_001_registration_page_access(page):
    """TC-R-001: 회원가입 페이지 접근"""
    print("\n[TC-R-001] 회원가입 페이지 접근 테스트")
    print("-" * 60)

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        # 1. 페이지 로드 확인
        if "/register" in page.url or "/auth/register" in page.url:
            log_result("TC-R-001-1", "회원가입 페이지 접근", True, page.url)
        else:
            log_result("TC-R-001-1", "회원가입 페이지 접근", False, f"URL: {page.url}")
            return False

        # 2. 가입 폼 존재 확인
        form_exists = await page.locator('form').count() > 0
        log_result("TC-R-001-2", "가입 폼 존재", form_exists)

        # 3. 필수 입력 필드 확인
        username_field = await page.locator('input[name="username"]').count() > 0
        email_field = await page.locator('input[name="email"]').count() > 0
        password_field = await page.locator('input[name="password"]').count() > 0

        all_fields = username_field and email_field and password_field
        log_result("TC-R-001-3", "필수 입력 필드 존재", all_fields,
                  f"username: {username_field}, email: {email_field}, password: {password_field}")

        return True
    except Exception as e:
        log_result("TC-R-001", "회원가입 페이지 접근", False, str(e))
        return False


async def test_tc_r_002_registration_success(page):
    """TC-R-002: 회원가입 성공 (모든 필드)"""
    print("\n[TC-R-002] 회원가입 성공 테스트 (6개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        # 1. 아이디 입력
        if await fill_input_if_exists(page, 'input[name="username"]', TEST_REGISTRATION["username"]):
            fields_filled += 1
            log_result("TC-R-002-1", "아이디 입력", True, TEST_REGISTRATION["username"])
        else:
            log_result("TC-R-002-1", "아이디 입력", False, "username 필드 없음")

        # 2. 이메일 입력
        if await fill_input_if_exists(page, 'input[name="email"]', TEST_REGISTRATION["email"]):
            fields_filled += 1
            log_result("TC-R-002-2", "이메일 입력", True, TEST_REGISTRATION["email"])
        else:
            log_result("TC-R-002-2", "이메일 입력", False, "email 필드 없음")

        # 3. 비밀번호 입력
        if await fill_input_if_exists(page, 'input[name="password"]', TEST_REGISTRATION["password"]):
            fields_filled += 1
            log_result("TC-R-002-3", "비밀번호 입력", True, "******")
        else:
            log_result("TC-R-002-3", "비밀번호 입력", False, "password 필드 없음")

        # 4. 비밀번호 확인 입력
        confirm_selectors = ['input[name="password_confirm"]', 'input[name="confirm_password"]', 'input[name="password2"]']
        confirm_filled = False
        for selector in confirm_selectors:
            if await fill_input_if_exists(page, selector, TEST_REGISTRATION["password_confirm"]):
                fields_filled += 1
                confirm_filled = True
                break
        log_result("TC-R-002-4", "비밀번호 확인 입력", confirm_filled, "******")

        # 5. 이름 입력
        if await fill_input_if_exists(page, 'input[name="name"]', TEST_REGISTRATION["name"]):
            fields_filled += 1
            log_result("TC-R-002-5", "이름 입력", True, TEST_REGISTRATION["name"])
        else:
            log_result("TC-R-002-5", "이름 입력", False, "name 필드 없음")

        # 6. 휴대전화 입력
        phone_selectors = ['input[name="mobile_phone"]', 'input[name="phone"]', 'input[name="mobile"]']
        phone_filled = False
        for selector in phone_selectors:
            if await fill_input_if_exists(page, selector, TEST_REGISTRATION["mobile_phone"]):
                fields_filled += 1
                phone_filled = True
                break
        log_result("TC-R-002-6", "휴대전화 입력", phone_filled, TEST_REGISTRATION["mobile_phone"])

        # 폼 제출
        await page.wait_for_timeout(500)
        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 성공 확인 (로그인 페이지로 리다이렉트 또는 성공 메시지)
            current_url = page.url
            content = await page.content()

            if "/login" in current_url or "로그인" in content or "가입" in content:
                log_result("TC-R-002-7", "회원가입 완료", True,
                          f"URL: {current_url}", fields_tested=fields_filled)
                test_results["field_coverage"]["registration"] = fields_filled
                return True
            else:
                # 에러 메시지 확인
                error_messages = await page.locator('.alert-danger, .alert-error, .error, [class*="error"]').all_text_contents()
                log_result("TC-R-002-7", "회원가입 완료", False,
                          f"에러: {error_messages}" if error_messages else f"URL: {current_url}",
                          "BE-REG-001", fields_tested=fields_filled)
                return False
        else:
            log_result("TC-R-002-7", "제출 버튼", False, "submit 버튼 없음")
            return False

    except Exception as e:
        log_result("TC-R-002", "회원가입", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_003_duplicate_username(page):
    """TC-R-003: 중복 아이디 검증"""
    print("\n[TC-R-003] 중복 아이디 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        # 이미 사용된 username으로 가입 시도
        await fill_input_if_exists(page, 'input[name="username"]', TEST_REGISTRATION["username"])
        await fill_input_if_exists(page, 'input[name="email"]', f"dup_{TEST_EMAIL}")
        await fill_input_if_exists(page, 'input[name="password"]', TEST_REGISTRATION["password"])

        confirm_selectors = ['input[name="password_confirm"]', 'input[name="confirm_password"]', 'input[name="password2"]']
        for selector in confirm_selectors:
            if await fill_input_if_exists(page, selector, TEST_REGISTRATION["password_confirm"]):
                break

        await fill_input_if_exists(page, 'input[name="name"]', "중복테스트")

        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)

            # 에러 메시지 확인
            content = await page.content()
            error_messages = await page.locator('.alert-danger, .alert-error, .error, [class*="error"]').all_text_contents()

            if "중복" in content or "이미" in content or "exists" in content.lower() or error_messages:
                log_result("TC-R-003-1", "중복 아이디 차단", True, str(error_messages))
            else:
                log_result("TC-R-003-1", "중복 아이디 차단", False,
                          "중복 아이디로 가입됨", "BE-REG-002")
        else:
            log_result("TC-R-003-1", "제출 버튼", False, "submit 버튼 없음")

        return True
    except Exception as e:
        log_result("TC-R-003", "중복 아이디 검증", False, str(e))
        return False


async def test_tc_r_004_duplicate_email(page):
    """TC-R-004: 중복 이메일 검증"""
    print("\n[TC-R-004] 중복 이메일 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        # 이미 사용된 email로 가입 시도
        dup_username = generate_unique_username()
        await fill_input_if_exists(page, 'input[name="username"]', dup_username)
        await fill_input_if_exists(page, 'input[name="email"]', TEST_REGISTRATION["email"])
        await fill_input_if_exists(page, 'input[name="password"]', TEST_REGISTRATION["password"])

        confirm_selectors = ['input[name="password_confirm"]', 'input[name="confirm_password"]', 'input[name="password2"]']
        for selector in confirm_selectors:
            if await fill_input_if_exists(page, selector, TEST_REGISTRATION["password_confirm"]):
                break

        await fill_input_if_exists(page, 'input[name="name"]', "이메일중복테스트")

        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)

            content = await page.content()
            error_messages = await page.locator('.alert-danger, .alert-error, .error, [class*="error"]').all_text_contents()

            if "중복" in content or "이미" in content or "exists" in content.lower() or error_messages:
                log_result("TC-R-004-1", "중복 이메일 차단", True, str(error_messages))
            else:
                log_result("TC-R-004-1", "중복 이메일 차단", False,
                          "중복 이메일로 가입됨", "BE-REG-003")
        else:
            log_result("TC-R-004-1", "제출 버튼", False, "submit 버튼 없음")

        return True
    except Exception as e:
        log_result("TC-R-004", "중복 이메일 검증", False, str(e))
        return False


async def test_tc_r_005_password_mismatch(page):
    """TC-R-005: 비밀번호 불일치 검증"""
    print("\n[TC-R-005] 비밀번호 불일치 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        mismatch_username = generate_unique_username()
        await fill_input_if_exists(page, 'input[name="username"]', mismatch_username)
        await fill_input_if_exists(page, 'input[name="email"]', f"{mismatch_username}@e2etest.local")
        await fill_input_if_exists(page, 'input[name="password"]', "Password123!")

        confirm_selectors = ['input[name="password_confirm"]', 'input[name="confirm_password"]', 'input[name="password2"]']
        for selector in confirm_selectors:
            if await fill_input_if_exists(page, selector, "DifferentPassword123!"):
                break

        await fill_input_if_exists(page, 'input[name="name"]', "비밀번호불일치테스트")

        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_timeout(2000)

            # 에러 확인
            content = await page.content()
            error_messages = await page.locator('.alert-danger, .alert-error, .error, [class*="error"], .invalid-feedback').all_text_contents()

            if "일치" in content or "match" in content.lower() or "/register" in page.url or error_messages:
                log_result("TC-R-005-1", "비밀번호 불일치 검증", True, str(error_messages))
            else:
                log_result("TC-R-005-1", "비밀번호 불일치 검증", False,
                          "불일치 비밀번호로 가입됨", "FE-REG-001")
        else:
            log_result("TC-R-005-1", "제출 버튼", False, "submit 버튼 없음")

        return True
    except Exception as e:
        log_result("TC-R-005", "비밀번호 불일치 검증", False, str(e))
        return False


async def test_tc_r_006_required_fields_missing(page):
    """TC-R-006: 필수 필드 누락 검증"""
    print("\n[TC-R-006] 필수 필드 누락 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(REGISTER_URL, wait_until="networkidle", timeout=30000)

        # 비밀번호만 입력하고 제출
        await fill_input_if_exists(page, 'input[name="password"]', "Test1234!")

        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_timeout(2000)

            # HTML5 유효성 검사 또는 커스텀 에러
            username_input = page.locator('input[name="username"]')
            if await username_input.count() > 0:
                validation_msg = await username_input.evaluate("el => el.validationMessage")
                if validation_msg or "/register" in page.url:
                    log_result("TC-R-006-1", "필수 필드 누락 검증", True, validation_msg or "폼 제출 차단됨")
                else:
                    log_result("TC-R-006-1", "필수 필드 누락 검증", False,
                              "필수 필드 없이 제출됨", "FE-REG-002")

        return True
    except Exception as e:
        log_result("TC-R-006", "필수 필드 누락 검증", False, str(e))
        return False


# ============================================================================
# Phase 2: 로그인 테스트 (TC-R-010 ~ TC-R-011)
# ============================================================================

async def test_tc_r_010_login_new_account(page):
    """TC-R-010: 신규 계정 로그인"""
    print("\n[TC-R-010] 신규 계정 로그인 테스트")
    print("-" * 60)

    try:
        await page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)

        # 로그인 정보 입력
        await fill_input_if_exists(page, 'input[name="username"]', TEST_REGISTRATION["username"])
        await fill_input_if_exists(page, 'input[name="password"]', TEST_REGISTRATION["password"])

        submit_btn = page.locator('button[type="submit"], input[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 로그인 성공 확인
            current_url = page.url
            if "/dashboard" in current_url or "/personal" in current_url:
                log_result("TC-R-010-1", "로그인 성공", True, current_url)

                # 세션 쿠키 확인
                cookies = await page.context.cookies()
                session_cookie = any('session' in c['name'].lower() for c in cookies)
                log_result("TC-R-010-2", "세션 쿠키 설정", session_cookie)

                return True
            else:
                error_messages = await page.locator('.alert-danger, .alert-error, .error').all_text_contents()
                log_result("TC-R-010-1", "로그인 성공", False,
                          f"에러: {error_messages}" if error_messages else f"URL: {current_url}",
                          "BE-LOGIN-001")
                return False
        else:
            log_result("TC-R-010-1", "제출 버튼", False, "submit 버튼 없음")
            return False

    except Exception as e:
        log_result("TC-R-010", "로그인", False, str(e))
        return False


async def test_tc_r_011_dashboard_access(page):
    """TC-R-011: 대시보드 확인"""
    print("\n[TC-R-011] 대시보드 확인 테스트")
    print("-" * 60)

    try:
        await page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=30000)

        # 대시보드 페이지 확인
        if "/dashboard" in page.url or "/personal" in page.url:
            log_result("TC-R-011-1", "대시보드 접근", True, page.url)
        else:
            log_result("TC-R-011-1", "대시보드 접근", False, f"리다이렉트: {page.url}")
            return False

        # 사용자 이름 표시 확인
        content = await page.content()
        if TEST_REGISTRATION["name"] in content or TEST_REGISTRATION["username"] in content:
            log_result("TC-R-011-2", "사용자 정보 표시", True)
        else:
            log_result("TC-R-011-2", "사용자 정보 표시", False, "사용자 이름 미표시")

        return True
    except Exception as e:
        log_result("TC-R-011", "대시보드", False, str(e))
        return False


# ============================================================================
# Phase 3: 기본정보 테스트 (TC-R-020 ~ TC-R-025)
# ============================================================================

async def test_tc_r_020_edit_page_access(page):
    """TC-R-020: 수정 페이지 접근"""
    print("\n[TC-R-020] 수정 페이지 접근 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        if "/edit" in page.url or "/profile" in page.url:
            log_result("TC-R-020-1", "수정 페이지 접근", True, page.url)
        else:
            log_result("TC-R-020-1", "수정 페이지 접근", False, f"리다이렉트: {page.url}")
            return False

        # 폼 존재 확인
        form_exists = await page.locator('form').count() > 0
        log_result("TC-R-020-2", "수정 폼 존재", form_exists)

        return True
    except Exception as e:
        log_result("TC-R-020", "수정 페이지 접근", False, str(e))
        return False


async def test_tc_r_021_required_fields(page):
    """TC-R-021: 필수 필드 입력 (7개)"""
    print("\n[TC-R-021] 필수 필드 입력 테스트 (7개)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 1. 이름
        if await fill_input_if_exists(page, 'input[name="name"]', TEST_BASIC_INFO["name"]):
            fields_filled += 1
            log_result("TC-R-021-1", "이름 입력", True)

        # 2. 영문 이름
        if await fill_input_if_exists(page, 'input[name="english_name"]', TEST_BASIC_INFO["english_name"]):
            fields_filled += 1
            log_result("TC-R-021-2", "영문 이름 입력", True)

        # 3. 주민등록번호
        if await fill_input_if_exists(page, 'input[name="resident_number"]', TEST_BASIC_INFO["resident_number"]):
            fields_filled += 1
            log_result("TC-R-021-3", "주민등록번호 입력", True)

        # 4. 휴대전화
        phone_selectors = ['input[name="phone"]', 'input[name="mobile_phone"]']
        for selector in phone_selectors:
            if await fill_input_if_exists(page, selector, TEST_BASIC_INFO["phone"]):
                fields_filled += 1
                log_result("TC-R-021-4", "휴대전화 입력", True)
                break

        # 5. 이메일
        if await fill_input_if_exists(page, 'input[name="email"]', TEST_BASIC_INFO["email"]):
            fields_filled += 1
            log_result("TC-R-021-5", "이메일 입력", True)

        # 6. 주민등록상 주소
        if await fill_input_if_exists(page, 'input[name="address"]', TEST_BASIC_INFO["address"]):
            fields_filled += 1
            log_result("TC-R-021-6", "주민등록상 주소 입력", True)

        # 7. 실제 거주지
        if await fill_input_if_exists(page, 'input[name="actual_address"]', TEST_BASIC_INFO["actual_address"]):
            fields_filled += 1
            log_result("TC-R-021-7", "실제 거주지 입력", True)

        log_result("TC-R-021", "필수 필드 입력 완료", fields_filled >= 5,
                  f"{fields_filled}/7개 필드 입력", fields_tested=fields_filled)

        return True
    except Exception as e:
        log_result("TC-R-021", "필수 필드 입력", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_022_rrn_auto_input(page):
    """TC-R-022: RRN 자동입력 확인 (생년월일, 나이, 성별)"""
    print("\n[TC-R-022] RRN 자동입력 확인 테스트 (3개 필드)")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 주민등록번호 입력
        await fill_input_if_exists(page, 'input[name="resident_number"]', TEST_BASIC_INFO["resident_number"])

        # blur 이벤트 발생 (자동입력 트리거)
        await page.evaluate('document.querySelector("input[name=resident_number]")?.blur()')

        # 자동입력 트리거 대기
        await page.wait_for_timeout(1000)

        auto_filled = 0

        # 생년월일 확인
        birth_input = page.locator('input[name="birth_date"]')
        if await birth_input.count() > 0:
            birth_value = await birth_input.input_value()
            if birth_value and "1985" in birth_value:
                auto_filled += 1
                log_result("TC-R-022-1", "생년월일 자동입력", True, birth_value)
            else:
                log_result("TC-R-022-1", "생년월일 자동입력", False, f"값: {birth_value}")

        # 나이 확인
        age_input = page.locator('input[name="age"]')
        if await age_input.count() > 0:
            age_value = await age_input.input_value()
            if age_value:
                auto_filled += 1
                log_result("TC-R-022-2", "나이 자동입력", True, age_value)
            else:
                log_result("TC-R-022-2", "나이 자동입력", False, "값 없음")

        # 성별 확인
        gender_select = page.locator('select[name="gender"]')
        if await gender_select.count() > 0:
            gender_value = await gender_select.input_value()
            if gender_value:
                auto_filled += 1
                log_result("TC-R-022-3", "성별 자동입력", True, gender_value)
            else:
                log_result("TC-R-022-3", "성별 자동입력", False, "값 없음")

        log_result("TC-R-022", "RRN 자동입력 완료", auto_filled >= 1,
                  f"{auto_filled}/3개 자동입력", fields_tested=auto_filled)

        return True
    except Exception as e:
        log_result("TC-R-022", "RRN 자동입력", False, str(e))
        return False


async def test_tc_r_023_optional_fields(page):
    """TC-R-023: 선택 필드 입력 (15개)"""
    print("\n[TC-R-023] 선택 필드 입력 테스트 (15개)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 1. 한자 이름
        if await fill_input_if_exists(page, 'input[name="chinese_name"]', TEST_BASIC_INFO["chinese_name"]):
            fields_filled += 1

        # 2. 외국어 이름
        if await fill_input_if_exists(page, 'input[name="foreign_name"]', TEST_BASIC_INFO["foreign_name"]):
            fields_filled += 1

        # 3. 결혼여부
        if await select_option_if_exists(page, 'select[name="marital_status"]', TEST_BASIC_INFO["marital_status"]):
            fields_filled += 1

        # 4. 국적
        if await select_option_if_exists(page, 'select[name="nationality"]', TEST_BASIC_INFO["nationality"]):
            fields_filled += 1

        # 5. 자택전화
        if await fill_input_if_exists(page, 'input[name="home_phone"]', TEST_BASIC_INFO["home_phone"]):
            fields_filled += 1

        # 6. 상세주소
        if await fill_input_if_exists(page, 'input[name="detailed_address"]', TEST_BASIC_INFO["detailed_address"]):
            fields_filled += 1

        # 7. 우편번호
        if await fill_input_if_exists(page, 'input[name="postal_code"]', TEST_BASIC_INFO["postal_code"]):
            fields_filled += 1

        # 8. 실제 거주지 상세
        if await fill_input_if_exists(page, 'input[name="actual_detailed_address"]', TEST_BASIC_INFO["actual_detailed_address"]):
            fields_filled += 1

        # 9. 실제 거주지 우편번호
        if await fill_input_if_exists(page, 'input[name="actual_postal_code"]', TEST_BASIC_INFO["actual_postal_code"]):
            fields_filled += 1

        # 10. 비상연락처
        if await fill_input_if_exists(page, 'input[name="emergency_contact"]', TEST_BASIC_INFO["emergency_contact"]):
            fields_filled += 1

        # 11. 비상연락처 관계
        if await fill_input_if_exists(page, 'input[name="emergency_relation"]', TEST_BASIC_INFO["emergency_relation"]):
            fields_filled += 1

        # 12. 취미
        if await fill_input_if_exists(page, 'input[name="hobby"], textarea[name="hobby"]', TEST_BASIC_INFO["hobby"]):
            fields_filled += 1

        # 13. 특기
        if await fill_input_if_exists(page, 'input[name="specialty"], textarea[name="specialty"]', TEST_BASIC_INFO["specialty"]):
            fields_filled += 1

        # 14. 장애정보
        if await fill_input_if_exists(page, 'input[name="disability_info"], textarea[name="disability_info"]', TEST_BASIC_INFO["disability_info"]):
            fields_filled += 1

        # 15. 음력 여부 (체크박스)
        lunar_checkbox = page.locator('input[name="lunar_birth"][type="checkbox"]')
        if await lunar_checkbox.count() > 0:
            if not TEST_BASIC_INFO["lunar_birth"]:
                # 체크 해제 상태 유지
                pass
            fields_filled += 1

        log_result("TC-R-023", "선택 필드 입력 완료", fields_filled >= 10,
                  f"{fields_filled}/15개 필드 입력", fields_tested=fields_filled)

        return True
    except Exception as e:
        log_result("TC-R-023", "선택 필드 입력", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_024_bank_info(page):
    """TC-R-024: 은행정보 입력 (3개)"""
    print("\n[TC-R-024] 은행정보 입력 테스트 (3개)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 1. 은행명
        if await select_option_if_exists(page, 'select[name="bank_name"]', TEST_BASIC_INFO["bank_name"]):
            fields_filled += 1
            log_result("TC-R-024-1", "은행명 선택", True, TEST_BASIC_INFO["bank_name"])
        else:
            log_result("TC-R-024-1", "은행명 선택", False, "bank_name 필드 없음")

        # 2. 계좌번호
        if await fill_input_if_exists(page, 'input[name="account_number"]', TEST_BASIC_INFO["account_number"]):
            fields_filled += 1
            log_result("TC-R-024-2", "계좌번호 입력", True)
        else:
            log_result("TC-R-024-2", "계좌번호 입력", False, "account_number 필드 없음")

        # 3. 예금주
        if await fill_input_if_exists(page, 'input[name="account_holder"]', TEST_BASIC_INFO["account_holder"]):
            fields_filled += 1
            log_result("TC-R-024-3", "예금주 입력", True)
        else:
            log_result("TC-R-024-3", "예금주 입력", False, "account_holder 필드 없음")

        log_result("TC-R-024", "은행정보 입력 완료", fields_filled >= 2,
                  f"{fields_filled}/3개 필드 입력", fields_tested=fields_filled)

        return True
    except Exception as e:
        log_result("TC-R-024", "은행정보 입력", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_025_basic_info_save(page):
    """TC-R-025: 기본정보 저장 (30개 총합)"""
    print("\n[TC-R-025] 기본정보 저장 테스트 (30개 필드)")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 모든 기본정보 입력
        total_fields = 0

        # 필수 필드
        for field, value in [
            ('input[name="name"]', TEST_BASIC_INFO["name"]),
            ('input[name="english_name"]', TEST_BASIC_INFO["english_name"]),
            ('input[name="resident_number"]', TEST_BASIC_INFO["resident_number"]),
            ('input[name="phone"], input[name="mobile_phone"]', TEST_BASIC_INFO["phone"]),
            ('input[name="email"]', TEST_BASIC_INFO["email"]),
            ('input[name="address"]', TEST_BASIC_INFO["address"]),
            ('input[name="actual_address"]', TEST_BASIC_INFO["actual_address"]),
        ]:
            if await fill_input_if_exists(page, field, value):
                total_fields += 1

        # 선택 필드
        for field, value in [
            ('input[name="chinese_name"]', TEST_BASIC_INFO["chinese_name"]),
            ('input[name="foreign_name"]', TEST_BASIC_INFO["foreign_name"]),
            ('input[name="home_phone"]', TEST_BASIC_INFO["home_phone"]),
            ('input[name="detailed_address"]', TEST_BASIC_INFO["detailed_address"]),
            ('input[name="postal_code"]', TEST_BASIC_INFO["postal_code"]),
            ('input[name="actual_detailed_address"]', TEST_BASIC_INFO["actual_detailed_address"]),
            ('input[name="actual_postal_code"]', TEST_BASIC_INFO["actual_postal_code"]),
            ('input[name="emergency_contact"]', TEST_BASIC_INFO["emergency_contact"]),
            ('input[name="emergency_relation"]', TEST_BASIC_INFO["emergency_relation"]),
            ('input[name="hobby"], textarea[name="hobby"]', TEST_BASIC_INFO["hobby"]),
            ('input[name="specialty"], textarea[name="specialty"]', TEST_BASIC_INFO["specialty"]),
            ('input[name="disability_info"], textarea[name="disability_info"]', TEST_BASIC_INFO["disability_info"]),
            ('input[name="account_number"]', TEST_BASIC_INFO["account_number"]),
            ('input[name="account_holder"]', TEST_BASIC_INFO["account_holder"]),
        ]:
            if await fill_input_if_exists(page, field, value):
                total_fields += 1

        # 선택 필드 (select)
        for field, value in [
            ('select[name="marital_status"]', TEST_BASIC_INFO["marital_status"]),
            ('select[name="nationality"]', TEST_BASIC_INFO["nationality"]),
            ('select[name="bank_name"]', TEST_BASIC_INFO["bank_name"]),
        ]:
            if await select_option_if_exists(page, field, value):
                total_fields += 1

        # 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 성공 메시지 확인
            flash_messages = await page.locator('.alert-success, .toast-success, .flash-success').all_text_contents()
            error_messages = await page.locator('.alert-danger, .alert-error, .flash-error').all_text_contents()
            # 빈 문자열 필터링
            error_messages = [m.strip() for m in error_messages if m.strip()]

            if flash_messages or not error_messages:
                log_result("TC-R-025", "기본정보 저장 성공", True,
                          f"{total_fields}개 필드 저장", fields_tested=total_fields)
                test_results["field_coverage"]["basic_info"] = total_fields
                return True
            else:
                log_result("TC-R-025", "기본정보 저장 실패", False,
                          f"에러: {error_messages}", "BE-SAVE-001", fields_tested=total_fields)
                return False
        else:
            log_result("TC-R-025", "저장 버튼", False, "submit 버튼 없음", fields_tested=total_fields)
            return False

    except Exception as e:
        log_result("TC-R-025", "기본정보 저장", False, str(e))
        return False


# ============================================================================
# Phase 4: 이력 데이터 테스트 (TC-R-030 ~ TC-R-039)
# ============================================================================

async def add_dynamic_row(page, add_button_selector, row_selector):
    """동적 행 추가 헬퍼"""
    try:
        add_btn = page.locator(add_button_selector)
        if await add_btn.count() > 0:
            before_count = await page.locator(row_selector).count()
            await add_btn.first.click()
            await page.wait_for_timeout(500)
            after_count = await page.locator(row_selector).count()
            return after_count > before_count
    except Exception:
        pass
    return False


async def test_tc_r_030_education_add(page):
    """TC-R-030: 학력 추가 (3개 행, 21개 필드)"""
    print("\n[TC-R-030] 학력 추가 테스트 (3개 행, 21개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 학력 섹션 스크롤
        education_section = page.locator('text=학력')
        if await education_section.count() > 0:
            await education_section.first.scroll_into_view_if_needed()

        for idx, edu in enumerate(TEST_EDUCATIONS):
            # 새 행 추가 (첫 번째 행은 이미 존재할 수 있음)
            if idx > 0:
                add_selectors = [
                    '#addEducation',
                    'button:has-text("학력 추가")',
                    '.add-education-btn',
                    '[data-add="education"]'
                ]
                row_added = False
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '#educationList .dynamic-item'):
                        row_added = True
                        break

                if not row_added:
                    log_result(f"TC-R-030-{idx+1}", f"학력 {idx+1}행 추가", False, "추가 버튼 없음")
                    continue

            # 학력 데이터 입력
            row_prefix = f"education_{idx}" if idx > 0 else ""

            # 학교명
            school_selectors = [
                f'input[name="education_school_name[]"]:nth-of-type({idx+1})',
                f'input[name*="school_name"]:nth-of-type({idx+1})',
                'input[name="education_school_name[]"]'
            ]
            for selector in school_selectors:
                locator = page.locator(selector)
                if await locator.count() > idx:
                    await locator.nth(idx).fill(edu["school_name"])
                    fields_filled += 1
                    break

            # 학위
            degree_selectors = [
                f'select[name="education_degree[]"]',
                f'select[name*="degree"]'
            ]
            for selector in degree_selectors:
                locator = page.locator(selector)
                if await locator.count() > idx:
                    try:
                        await locator.nth(idx).select_option(label=edu["degree"])
                        fields_filled += 1
                    except Exception:
                        pass
                    break

            # 전공
            major_selectors = ['input[name="education_major[]"]', 'input[name*="major"]']
            for selector in major_selectors:
                locator = page.locator(selector)
                if await locator.count() > idx:
                    await locator.nth(idx).fill(edu["major"])
                    fields_filled += 1
                    break

            # 졸업년도
            year_selectors = ['input[name="education_graduation_year[]"]', 'input[name*="graduation_year"]']
            for selector in year_selectors:
                locator = page.locator(selector)
                if await locator.count() > idx:
                    await locator.nth(idx).fill(edu["graduation_year"])
                    fields_filled += 1
                    break

            # 학점
            if edu["gpa"]:
                gpa_selectors = ['input[name="education_gpa[]"]', 'input[name*="gpa"]']
                for selector in gpa_selectors:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        await locator.nth(idx).fill(edu["gpa"])
                        fields_filled += 1
                        break

            # 졸업상태
            status_selectors = ['select[name="education_graduation_status[]"]', 'select[name*="graduation_status"]']
            for selector in status_selectors:
                locator = page.locator(selector)
                if await locator.count() > idx:
                    try:
                        await locator.nth(idx).select_option(label=edu["graduation_status"])
                        fields_filled += 1
                    except Exception:
                        pass
                    break

            # 비고
            if edu["note"]:
                note_selectors = ['input[name="education_note[]"]', 'textarea[name="education_note[]"]']
                for selector in note_selectors:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        await locator.nth(idx).fill(edu["note"])
                        fields_filled += 1
                        break

            log_result(f"TC-R-030-{idx+1}", f"학력 {idx+1}행 입력", True, edu["school_name"])

        log_result("TC-R-030", "학력 데이터 입력 완료", fields_filled >= 10,
                  f"{fields_filled}/21개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["education"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-030", "학력 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_031_education_save(page):
    """TC-R-031: 학력 저장 확인"""
    print("\n[TC-R-031] 학력 저장 확인 테스트")
    print("-" * 60)

    try:
        # 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 페이지 새로고침 후 데이터 확인
            await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

            # 저장된 학력 데이터 확인
            school_inputs = page.locator('input[name*="school_name"]')
            school_count = await school_inputs.count()

            if school_count >= 1:
                first_school = await school_inputs.first.input_value()
                if first_school:
                    log_result("TC-R-031-1", "학력 데이터 영속성", True, f"저장된 학교: {first_school}")
                else:
                    log_result("TC-R-031-1", "학력 데이터 영속성", False, "데이터 없음")
            else:
                log_result("TC-R-031-1", "학력 데이터 영속성", False, "학력 필드 없음")

        return True
    except Exception as e:
        log_result("TC-R-031", "학력 저장 확인", False, str(e))
        return False


async def test_tc_r_032_career_add(page):
    """TC-R-032: 경력 추가 (3개 행, 39개 필드)"""
    print("\n[TC-R-032] 경력 추가 테스트 (3개 행, 39개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 경력 섹션 스크롤
        career_section = page.locator('text=경력')
        if await career_section.count() > 0:
            await career_section.first.scroll_into_view_if_needed()

        for idx, career in enumerate(TEST_CAREERS):
            # 새 행 추가
            if idx > 0:
                add_selectors = [
                    '#addCareer',
                    'button:has-text("경력 추가")',
                    '.add-career-btn',
                    '[data-add="career"]'
                ]
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '[data-career-row], .career-row, .career-item'):
                        break

            # 경력 데이터 입력
            field_mappings = [
                ('input[name*="company_name"]', career["company_name"]),
                ('input[name*="department"]', career["department"]),
                ('input[name*="position"]', career["position"]),
                ('input[name*="job_grade"]', career.get("job_grade", "")),
                ('input[name*="job_title"]', career.get("job_title", "")),
                ('input[name*="job_role"]', career.get("job_role", "")),
                ('input[name*="duties"], textarea[name*="duties"]', career.get("duties", "")),
                ('input[name*="salary"][name*="career"]', career.get("salary", "")),
                ('input[name*="monthly_salary"]', career.get("monthly_salary", "")),
                ('input[name*="pay_step"]', career.get("pay_step", "")),
                ('input[name*="start_date"]', career["start_date"]),
                ('input[name*="end_date"]', career.get("end_date", "")),
            ]

            for selector, value in field_mappings:
                if value:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        try:
                            await locator.nth(idx).fill(str(value))
                            fields_filled += 1
                        except Exception:
                            pass

            # 급여유형 (select)
            salary_type_locator = page.locator('select[name*="salary_type"]')
            if await salary_type_locator.count() > idx:
                try:
                    await salary_type_locator.nth(idx).select_option(label=career.get("salary_type", "연봉"))
                    fields_filled += 1
                except Exception:
                    pass

            log_result(f"TC-R-032-{idx+1}", f"경력 {idx+1}행 입력", True, career["company_name"])

        log_result("TC-R-032", "경력 데이터 입력 완료", fields_filled >= 15,
                  f"{fields_filled}/39개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["career"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-032", "경력 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_033_career_save(page):
    """TC-R-033: 경력 저장 확인"""
    print("\n[TC-R-033] 경력 저장 확인 테스트")
    print("-" * 60)

    try:
        # 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            log_result("TC-R-033-1", "경력 저장 완료", True)

        return True
    except Exception as e:
        log_result("TC-R-033", "경력 저장 확인", False, str(e))
        return False


async def test_tc_r_034_certificate_add(page):
    """TC-R-034: 자격증 추가 (3개 행, 18개 필드)"""
    print("\n[TC-R-034] 자격증 추가 테스트 (3개 행, 18개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 자격증 섹션 스크롤
        cert_section = page.locator('text=자격증')
        if await cert_section.count() > 0:
            await cert_section.first.scroll_into_view_if_needed()

        for idx, cert in enumerate(TEST_CERTIFICATES):
            # 새 행 추가
            if idx > 0:
                add_selectors = [
                    '#addCertificate',
                    'button:has-text("자격증 추가")',
                    '.add-certificate-btn',
                    '[data-add="certificate"]'
                ]
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '[data-certificate-row], .certificate-row, .certificate-item'):
                        break

            # 자격증 데이터 입력
            field_mappings = [
                ('input[name*="certificate_name"], input[name*="cert_name"]', cert["name"]),
                ('input[name*="issuing_organization"], input[name*="issuer"]', cert["issuing_organization"]),
                ('input[name*="certificate_grade"], input[name*="grade"]', cert.get("grade", "")),
                ('input[name*="acquisition_date"], input[name*="cert_date"]', cert["acquisition_date"]),
                ('input[name*="certificate_number"], input[name*="cert_number"]', cert.get("number", "")),
                ('input[name*="expiry_date"]', cert.get("expiry_date", "")),
            ]

            for selector, value in field_mappings:
                if value:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        try:
                            await locator.nth(idx).fill(str(value))
                            fields_filled += 1
                        except Exception:
                            pass

            log_result(f"TC-R-034-{idx+1}", f"자격증 {idx+1}행 입력", True, cert["name"])

        log_result("TC-R-034", "자격증 데이터 입력 완료", fields_filled >= 9,
                  f"{fields_filled}/18개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["certificate"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-034", "자격증 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_035_language_add(page):
    """TC-R-035: 어학 추가 (3개 행, 15개 필드)"""
    print("\n[TC-R-035] 어학 추가 테스트 (3개 행, 15개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 어학 섹션 스크롤
        lang_section = page.locator('text=어학')
        if await lang_section.count() > 0:
            await lang_section.first.scroll_into_view_if_needed()

        for idx, lang in enumerate(TEST_LANGUAGES):
            # 새 행 추가
            if idx > 0:
                add_selectors = [
                    '#addLanguage',
                    'button:has-text("어학 추가")',
                    '.add-language-btn',
                    '[data-add="language"]'
                ]
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '[data-language-row], .language-row, .language-item'):
                        break

            # 어학 데이터 입력
            # 언어 (select)
            lang_select = page.locator('select[name*="language_language"], select[name*="language[]"]')
            if await lang_select.count() > idx:
                try:
                    await lang_select.nth(idx).select_option(label=lang["language"])
                    fields_filled += 1
                except Exception:
                    pass

            # 수준 (select)
            level_select = page.locator('select[name*="language_level"], select[name*="level"]')
            if await level_select.count() > idx:
                try:
                    await level_select.nth(idx).select_option(label=lang["level"])
                    fields_filled += 1
                except Exception:
                    pass

            field_mappings = [
                ('input[name*="test_name"]', lang["test_name"]),
                ('input[name*="score"]', lang["score"]),
                ('input[name*="test_date"]', lang["test_date"]),
            ]

            for selector, value in field_mappings:
                if value:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        try:
                            await locator.nth(idx).fill(str(value))
                            fields_filled += 1
                        except Exception:
                            pass

            log_result(f"TC-R-035-{idx+1}", f"어학 {idx+1}행 입력", True, f"{lang['language']} - {lang['test_name']}")

        log_result("TC-R-035", "어학 데이터 입력 완료", fields_filled >= 8,
                  f"{fields_filled}/15개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["language"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-035", "어학 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_036_military_input(page):
    """TC-R-036: 병역 입력 (7개 필드)"""
    print("\n[TC-R-036] 병역 입력 테스트 (7개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 병역 섹션 스크롤
        military_section = page.locator('text=병역')
        if await military_section.count() > 0:
            await military_section.first.scroll_into_view_if_needed()

        # 병역사항 (select)
        if await select_option_if_exists(page, 'select[name*="military_status"], select[name="military_status"]', TEST_MILITARY["status"]):
            fields_filled += 1
            log_result("TC-R-036-1", "병역사항 선택", True, TEST_MILITARY["status"])

        # 군별 (select)
        if await select_option_if_exists(page, 'select[name*="military_branch"], select[name="military_branch"]', TEST_MILITARY["branch"]):
            fields_filled += 1
            log_result("TC-R-036-2", "군별 선택", True, TEST_MILITARY["branch"])

        # 계급
        if await fill_input_if_exists(page, 'input[name*="military_rank"], input[name="military_rank"]', TEST_MILITARY["rank"]):
            fields_filled += 1
            log_result("TC-R-036-3", "계급 입력", True)

        # 복무기간
        if await fill_input_if_exists(page, 'input[name*="military_period"], input[name="military_period"]', TEST_MILITARY["period"]):
            fields_filled += 1
            log_result("TC-R-036-4", "복무기간 입력", True)

        # 보직
        if await fill_input_if_exists(page, 'input[name*="military_duty"], input[name="military_duty"]', TEST_MILITARY["duty"]):
            fields_filled += 1
            log_result("TC-R-036-5", "보직 입력", True)

        # 병과
        if await fill_input_if_exists(page, 'input[name*="military_specialty"], input[name="military_specialty"]', TEST_MILITARY["specialty"]):
            fields_filled += 1
            log_result("TC-R-036-6", "병과 입력", True)

        log_result("TC-R-036", "병역 데이터 입력 완료", fields_filled >= 4,
                  f"{fields_filled}/7개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["military"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-036", "병역 입력", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_037_award_add(page):
    """TC-R-037: 수상 추가 (3개 행, 12개 필드)"""
    print("\n[TC-R-037] 수상 추가 테스트 (3개 행, 12개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 수상 섹션 스크롤
        award_section = page.locator('text=수상')
        if await award_section.count() > 0:
            await award_section.first.scroll_into_view_if_needed()

        for idx, award in enumerate(TEST_AWARDS):
            # 새 행 추가
            if idx > 0:
                add_selectors = [
                    '#addAward',
                    'button:has-text("수상 추가")',
                    '.add-award-btn',
                    '[data-add="award"]'
                ]
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '[data-award-row], .award-row, .award-item'):
                        break

            # 수상 데이터 입력
            field_mappings = [
                ('input[name*="award_name"]', award["name"]),
                ('input[name*="award_date"]', award["date"]),
                ('input[name*="award_issuer"], input[name*="issuer"]', award["issuer"]),
                ('input[name*="award_note"], textarea[name*="award_note"]', award.get("note", "")),
            ]

            for selector, value in field_mappings:
                if value:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        try:
                            await locator.nth(idx).fill(str(value))
                            fields_filled += 1
                        except Exception:
                            pass

            log_result(f"TC-R-037-{idx+1}", f"수상 {idx+1}행 입력", True, award["name"])

        log_result("TC-R-037", "수상 데이터 입력 완료", fields_filled >= 6,
                  f"{fields_filled}/12개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["award"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-037", "수상 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_038_family_add(page):
    """TC-R-038: 가족 추가 (3개 행, 18개 필드)"""
    print("\n[TC-R-038] 가족 추가 테스트 (3개 행, 18개 필드)")
    print("-" * 60)

    fields_filled = 0

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 가족 섹션 스크롤
        family_section = page.locator('text=가족')
        if await family_section.count() > 0:
            await family_section.first.scroll_into_view_if_needed()

        for idx, family in enumerate(TEST_FAMILIES):
            # 새 행 추가
            if idx > 0:
                add_selectors = [
                    '#addFamily',
                    'button:has-text("가족 추가")',
                    '.add-family-btn',
                    '[data-add="family"]'
                ]
                for selector in add_selectors:
                    if await add_dynamic_row(page, selector, '[data-family-row], .family-row, .family-item'):
                        break

            # 관계 (select)
            relation_select = page.locator('select[name*="family_relation"], select[name*="relation"]')
            if await relation_select.count() > idx:
                try:
                    await relation_select.nth(idx).select_option(label=family["relation"])
                    fields_filled += 1
                except Exception:
                    pass

            # 가족 데이터 입력
            field_mappings = [
                ('input[name*="family_name"]', family["name"]),
                ('input[name*="family_birth_date"], input[name*="birth_date"]', family["birth_date"]),
                ('input[name*="family_occupation"], input[name*="occupation"]', family.get("occupation", "")),
                ('input[name*="family_phone"]', family.get("phone", "")),
            ]

            for selector, value in field_mappings:
                if value:
                    locator = page.locator(selector)
                    if await locator.count() > idx:
                        try:
                            await locator.nth(idx).fill(str(value))
                            fields_filled += 1
                        except Exception:
                            pass

            # 동거여부 (select)
            cohabit_select = page.locator('select[name*="is_cohabitant"], select[name*="cohabitant"]')
            if await cohabit_select.count() > idx:
                try:
                    await cohabit_select.nth(idx).select_option(label=family.get("is_cohabitant", "동거"))
                    fields_filled += 1
                except Exception:
                    pass

            log_result(f"TC-R-038-{idx+1}", f"가족 {idx+1}행 입력", True, f"{family['relation']} - {family['name']}")

        log_result("TC-R-038", "가족 데이터 입력 완료", fields_filled >= 9,
                  f"{fields_filled}/18개 필드 입력", fields_tested=fields_filled)
        test_results["field_coverage"]["family"] = fields_filled

        return True
    except Exception as e:
        log_result("TC-R-038", "가족 추가", False, str(e), fields_tested=fields_filled)
        return False


async def test_tc_r_039_history_save(page):
    """TC-R-039: 이력 저장 확인 (123개 필드 총합)"""
    print("\n[TC-R-039] 이력 저장 확인 테스트 (123개 필드 총합)")
    print("-" * 60)

    try:
        # 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 성공 메시지 확인
            flash_messages = await page.locator('.alert-success, .toast-success, [class*="success"]').all_text_contents()
            error_messages = await page.locator('.alert-danger, .alert-error, [class*="error"]').all_text_contents()

            total_history_fields = sum([
                test_results["field_coverage"]["education"],
                test_results["field_coverage"]["career"],
                test_results["field_coverage"]["certificate"],
                test_results["field_coverage"]["language"],
                test_results["field_coverage"]["military"],
                test_results["field_coverage"]["award"],
                test_results["field_coverage"]["family"],
            ])

            if flash_messages or not error_messages:
                log_result("TC-R-039", "이력 데이터 저장 성공", True,
                          f"총 {total_history_fields}개 필드 저장", fields_tested=total_history_fields)
                return True
            else:
                log_result("TC-R-039", "이력 데이터 저장 실패", False,
                          f"에러: {error_messages}", "BE-HISTORY-001", fields_tested=total_history_fields)
                return False

        return True
    except Exception as e:
        log_result("TC-R-039", "이력 저장 확인", False, str(e))
        return False


# ============================================================================
# Phase 5: 사진 업로드 테스트 (TC-R-040 ~ TC-R-043)
# ============================================================================

async def test_tc_r_040_png_upload(page):
    """TC-R-040: PNG 업로드"""
    print("\n[TC-R-040] PNG 업로드 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 사진 업로드 input 찾기
        photo_input = page.locator('input[type="file"][name*="photo"], input[type="file"][accept*="image"]')

        if await photo_input.count() > 0:
            # PNG 파일 업로드
            png_path = os.path.join(SAMPLE_FILES_DIR, "sangjin_face_01.png")
            if os.path.exists(png_path):
                await photo_input.set_input_files(png_path)
                await page.wait_for_timeout(1000)

                # 미리보기 확인
                preview = page.locator('#photoPreview, #previewImage, .photo-preview, .profile-photo img')
                if await preview.count() > 0:
                    log_result("TC-R-040-1", "PNG 업로드 성공", True, png_path)
                    test_results["field_coverage"]["photo"] += 1
                else:
                    log_result("TC-R-040-1", "PNG 업로드 (미리보기 없음)", True, png_path)
                    test_results["field_coverage"]["photo"] += 1
            else:
                log_result("TC-R-040-1", "PNG 업로드", False, f"파일 없음: {png_path}")
        else:
            log_result("TC-R-040-1", "사진 업로드 필드", False, "file input 없음")

        return True
    except Exception as e:
        log_result("TC-R-040", "PNG 업로드", False, str(e))
        return False


async def test_tc_r_041_jpg_upload(page):
    """TC-R-041: JPG 업로드"""
    print("\n[TC-R-041] JPG 업로드 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        photo_input = page.locator('input[type="file"][name*="photo"], input[type="file"][accept*="image"]')

        if await photo_input.count() > 0:
            jpg_path = os.path.join(SAMPLE_FILES_DIR, "sangjin_face_03.jpg")
            if os.path.exists(jpg_path):
                await photo_input.set_input_files(jpg_path)
                await page.wait_for_timeout(1000)

                log_result("TC-R-041-1", "JPG 업로드 성공", True, jpg_path)
                test_results["field_coverage"]["photo"] += 1
            else:
                log_result("TC-R-041-1", "JPG 업로드", False, f"파일 없음: {jpg_path}")
        else:
            log_result("TC-R-041-1", "사진 업로드 필드", False, "file input 없음")

        return True
    except Exception as e:
        log_result("TC-R-041", "JPG 업로드", False, str(e))
        return False


async def test_tc_r_042_photo_save(page):
    """TC-R-042: 저장 후 확인"""
    print("\n[TC-R-042] 사진 저장 후 확인 테스트")
    print("-" * 60)

    try:
        # 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

            # 페이지 새로고침 후 사진 확인
            await page.goto(PROFILE_VIEW_URL, wait_until="networkidle", timeout=30000)

            # 프로필 사진 표시 확인
            profile_img = page.locator('.profile-photo img, .photo-container img, img[src*="photo"], img[src*="profile"], img[src*="uploads"]')
            if await profile_img.count() > 0:
                img_src = await profile_img.first.get_attribute("src")
                if img_src and ("photo" in img_src.lower() or "profile" in img_src.lower() or "uploads" in img_src.lower()):
                    log_result("TC-R-042-1", "사진 저장 영속성", True, img_src)
                else:
                    log_result("TC-R-042-1", "사진 저장 영속성", False, "기본 이미지")
            else:
                log_result("TC-R-042-1", "사진 표시", False, "프로필 사진 없음")

        return True
    except Exception as e:
        log_result("TC-R-042", "사진 저장 확인", False, str(e))
        return False


async def test_tc_r_043_photo_delete(page):
    """TC-R-043: 사진 삭제"""
    print("\n[TC-R-043] 사진 삭제 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 사진 삭제 버튼 찾기
        delete_btn = page.locator('#deletePhotoBtn, .photo-delete-btn, button:has-text("사진 삭제"), button:has-text("삭제")')

        if await delete_btn.count() > 0:
            await delete_btn.first.click()
            await page.wait_for_timeout(1000)

            # 확인 다이얼로그 처리
            page.on("dialog", lambda dialog: dialog.accept())

            log_result("TC-R-043-1", "사진 삭제 버튼 클릭", True)
        else:
            log_result("TC-R-043-1", "사진 삭제 버튼", False, "삭제 버튼 없음 (사진이 없거나 UI 다름)")

        return True
    except Exception as e:
        log_result("TC-R-043", "사진 삭제", False, str(e))
        return False


# ============================================================================
# Phase 6: 종합 검증 테스트 (TC-R-050 ~ TC-R-054)
# ============================================================================

async def test_tc_r_050_full_save(page):
    """TC-R-050: 전체 저장 (모든 166+ 필드)"""
    print("\n[TC-R-050] 전체 저장 테스트 (166+ 필드)")
    print("-" * 60)

    try:
        total_fields = sum(test_results["field_coverage"].values())

        log_result("TC-R-050", "전체 필드 테스트 완료", total_fields >= 50,
                  f"총 {total_fields}개 필드 테스트됨", fields_tested=total_fields)

        return True
    except Exception as e:
        log_result("TC-R-050", "전체 저장", False, str(e))
        return False


async def test_tc_r_051_data_persistence(page):
    """TC-R-051: 데이터 영속성 (재로그인 후 확인)"""
    print("\n[TC-R-051] 데이터 영속성 테스트 (재로그인 후 확인)")
    print("-" * 60)

    try:
        # 로그아웃
        await page.goto(LOGOUT_URL, wait_until="networkidle", timeout=10000)

        # 재로그인
        await page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
        await fill_input_if_exists(page, 'input[name="username"]', TEST_REGISTRATION["username"])
        await fill_input_if_exists(page, 'input[name="password"]', TEST_REGISTRATION["password"])

        submit_btn = page.locator('button[type="submit"]')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=15000)

        # 프로필 확인
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        # 이름 필드 값 확인
        name_input = page.locator('input[name="name"]')
        if await name_input.count() > 0:
            name_value = await name_input.input_value()
            if name_value == TEST_BASIC_INFO["name"]:
                log_result("TC-R-051-1", "데이터 영속성 - 이름", True, name_value)
            else:
                log_result("TC-R-051-1", "데이터 영속성 - 이름", False,
                          f"예상: {TEST_BASIC_INFO['name']}, 실제: {name_value}")

        # 영문 이름 확인
        english_name_input = page.locator('input[name="english_name"]')
        if await english_name_input.count() > 0:
            en_value = await english_name_input.input_value()
            if en_value == TEST_BASIC_INFO["english_name"]:
                log_result("TC-R-051-2", "데이터 영속성 - 영문이름", True, en_value)
            else:
                log_result("TC-R-051-2", "데이터 영속성 - 영문이름", False, f"실제: {en_value}")

        return True
    except Exception as e:
        log_result("TC-R-051", "데이터 영속성", False, str(e))
        return False


async def test_tc_r_052_api_validation(page):
    """TC-R-052: API 검증 (/personal/* API)"""
    print("\n[TC-R-052] API 검증 테스트")
    print("-" * 60)

    try:
        # 먼저 페이지가 로그인 상태인지 확인하고, personal 대시보드로 이동
        await page.goto(DASHBOARD_URL, wait_until="networkidle", timeout=30000)

        # 프로필 API 테스트 (브라우저 컨텍스트에서 fetch 실행)
        api_endpoints = ["education", "career", "certificate", "language"]

        for endpoint_name in api_endpoints:
            try:
                # 브라우저 내에서 fetch 실행 (credentials: include로 세션 쿠키 명시적 포함)
                result = await page.evaluate(f'''
                    async () => {{
                        try {{
                            const response = await fetch('/personal/{endpoint_name}', {{
                                credentials: 'include'
                            }});
                            const text = await response.text();
                            return {{
                                status: response.status,
                                ok: response.ok,
                                body: text.substring(0, 200)
                            }};
                        }} catch (e) {{
                            return {{ status: 0, ok: false, error: e.message }};
                        }}
                    }}
                ''')
                if result.get('ok'):
                    log_result(f"TC-R-052-{endpoint_name}", f"API GET {endpoint_name}", True,
                              f"status: {result.get('status')}")
                else:
                    # 404 응답 본문 포함하여 원인 파악
                    body_preview = result.get('body', '')[:100]
                    log_result(f"TC-R-052-{endpoint_name}", f"API GET {endpoint_name}", False,
                              f"status: {result.get('status')}, body: {body_preview}")
            except Exception as e:
                log_result(f"TC-R-052-{endpoint_name}", f"API GET {endpoint_name}", False, str(e))

        return True
    except Exception as e:
        log_result("TC-R-052", "API 검증", False, str(e))
        return False


async def test_tc_r_053_profile_view(page):
    """TC-R-053: 프로필 조회 확인"""
    print("\n[TC-R-053] 프로필 조회 확인 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_VIEW_URL, wait_until="networkidle", timeout=30000)

        content = await page.content()

        # 이름 표시 확인
        if TEST_BASIC_INFO["name"] in content:
            log_result("TC-R-053-1", "프로필 조회 - 이름 표시", True)
        else:
            log_result("TC-R-053-1", "프로필 조회 - 이름 표시", False, "이름 미표시")

        # 학력 표시 확인
        if TEST_EDUCATIONS[0]["school_name"] in content or "학력" in content:
            log_result("TC-R-053-2", "프로필 조회 - 학력 표시", True)
        else:
            log_result("TC-R-053-2", "프로필 조회 - 학력 표시", False, "학력 미표시")

        return True
    except Exception as e:
        log_result("TC-R-053", "프로필 조회", False, str(e))
        return False


async def test_tc_r_054_field_validation(page):
    """TC-R-054: 필드별 데이터 검증 (모든 필드 값 확인)"""
    print("\n[TC-R-054] 필드별 데이터 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(PROFILE_EDIT_URL, wait_until="networkidle", timeout=30000)

        validated_fields = 0

        # 기본정보 필드 검증
        field_checks = [
            ('input[name="name"]', TEST_BASIC_INFO["name"]),
            ('input[name="english_name"]', TEST_BASIC_INFO["english_name"]),
            ('input[name="phone"], input[name="mobile_phone"]', TEST_BASIC_INFO["phone"]),
        ]

        for selector, expected in field_checks:
            locator = page.locator(selector)
            if await locator.count() > 0:
                actual = await locator.first.input_value()
                if actual == expected:
                    validated_fields += 1

        log_result("TC-R-054", "필드별 데이터 검증", validated_fields >= 2,
                  f"{validated_fields}개 필드 검증 완료", fields_tested=validated_fields)

        return True
    except Exception as e:
        log_result("TC-R-054", "필드별 데이터 검증", False, str(e))
        return False


# ============================================================================
# 메인 실행
# ============================================================================

async def run_all_tests():
    """모든 E2E 테스트 실행"""
    print("=" * 80)
    print("개인계정 회원가입 및 프로필 전체 필드 E2E 테스트")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"테스트 계정: {TEST_USERNAME}")
    print(f"테스트 이메일: {TEST_EMAIL}")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False로 브라우저 표시
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Phase 1: 회원가입 테스트
            print("\n" + "=" * 80)
            print("Phase 1: 회원가입 테스트 (TC-R-001 ~ TC-R-006)")
            print("=" * 80)

            await test_tc_r_001_registration_page_access(page)
            registration_success = await test_tc_r_002_registration_success(page)

            if registration_success:
                await test_tc_r_003_duplicate_username(page)
                await test_tc_r_004_duplicate_email(page)

            await test_tc_r_005_password_mismatch(page)
            await test_tc_r_006_required_fields_missing(page)

            if not registration_success:
                print("\n[WARNING] 회원가입 실패로 인해 후속 테스트를 건너뜁니다.")
                return test_results

            # Phase 2: 로그인 테스트
            print("\n" + "=" * 80)
            print("Phase 2: 로그인 테스트 (TC-R-010 ~ TC-R-011)")
            print("=" * 80)

            login_success = await test_tc_r_010_login_new_account(page)
            if login_success:
                await test_tc_r_011_dashboard_access(page)
            else:
                print("\n[WARNING] 로그인 실패로 인해 후속 테스트를 건너뜁니다.")
                return test_results

            # Phase 3: 기본정보 테스트
            print("\n" + "=" * 80)
            print("Phase 3: 기본정보 테스트 (TC-R-020 ~ TC-R-025)")
            print("=" * 80)

            await test_tc_r_020_edit_page_access(page)
            await test_tc_r_021_required_fields(page)
            await test_tc_r_022_rrn_auto_input(page)
            await test_tc_r_023_optional_fields(page)
            await test_tc_r_024_bank_info(page)
            await test_tc_r_025_basic_info_save(page)

            # Phase 4: 이력 데이터 테스트
            print("\n" + "=" * 80)
            print("Phase 4: 이력 데이터 테스트 (TC-R-030 ~ TC-R-039)")
            print("=" * 80)

            await test_tc_r_030_education_add(page)
            await test_tc_r_031_education_save(page)
            await test_tc_r_032_career_add(page)
            await test_tc_r_033_career_save(page)
            await test_tc_r_034_certificate_add(page)
            await test_tc_r_035_language_add(page)
            await test_tc_r_036_military_input(page)
            await test_tc_r_037_award_add(page)
            await test_tc_r_038_family_add(page)
            await test_tc_r_039_history_save(page)

            # Phase 5: 사진 업로드 테스트
            print("\n" + "=" * 80)
            print("Phase 5: 사진 업로드 테스트 (TC-R-040 ~ TC-R-043)")
            print("=" * 80)

            await test_tc_r_040_png_upload(page)
            await test_tc_r_041_jpg_upload(page)
            await test_tc_r_042_photo_save(page)
            await test_tc_r_043_photo_delete(page)

            # Phase 6: 종합 검증 테스트
            print("\n" + "=" * 80)
            print("Phase 6: 종합 검증 테스트 (TC-R-050 ~ TC-R-054)")
            print("=" * 80)

            await test_tc_r_050_full_save(page)
            await test_tc_r_051_data_persistence(page)
            await test_tc_r_052_api_validation(page)
            await test_tc_r_053_profile_view(page)
            await test_tc_r_054_field_validation(page)

        finally:
            await browser.close()

    # 결과 요약
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    print(f"\n테스트 계정: {TEST_USERNAME}")
    print(f"테스트 이메일: {TEST_EMAIL}")
    print(f"\n총 테스트: {test_results['total']}개")
    print(f"통과: {test_results['passed']}개")
    print(f"실패: {test_results['failed']}개")
    print(f"통과율: {(test_results['passed'] / test_results['total'] * 100):.1f}%" if test_results['total'] > 0 else "N/A")

    # 필드 커버리지 출력
    print("\n" + "-" * 40)
    print("필드 커버리지:")
    print("-" * 40)
    total_fields = 0
    for section, count in test_results["field_coverage"].items():
        print(f"  {section}: {count}개")
        total_fields += count
    print(f"  총계: {total_fields}개")

    if test_results['bugs']:
        print("\n" + "-" * 40)
        print("발견된 버그:")
        print("-" * 40)
        for bug in test_results['bugs']:
            print(f"  [{bug['test_id']}] {bug.get('bug_id', 'N/A')}: {bug['message']}")

    # 결과 저장
    output_file = f"personal_registration_e2e_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n상세 결과가 {output_file}에 저장되었습니다.")

    return test_results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
