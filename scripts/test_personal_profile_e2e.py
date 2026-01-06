"""
개인계정 프로필 E2E 테스트 스크립트

개인계정(personal_junhyuk.kim)으로 로그인하여 프로필 관련 기능을 테스트합니다.
- 로그인/로그아웃
- 프로필 조회/수정
- 이력 데이터 CRUD (학력, 경력, 자격증, 어학, 병역)
- 첨부파일 (프로필 사진)
"""
import asyncio
import json
import sys
import os
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5200"
LOGIN_URL = f"{BASE_URL}/auth/login"
LOGOUT_URL = f"{BASE_URL}/auth/logout"

# 개인계정 테스트 정보
PERSONAL_ACCOUNT = {
    "username": "personal_junhyuk.kim",
    "password": "test1234",
    "expected_redirect": "/personal/dashboard"
}

# 테스트 결과 저장
test_results = {
    "timestamp": datetime.now().isoformat(),
    "total": 0,
    "passed": 0,
    "failed": 0,
    "bugs": [],
    "tests": []
}


def log_result(test_id, test_name, passed, message="", bug_id=None, details=None):
    """테스트 결과 로깅"""
    status = "PASS" if passed else "FAIL"
    print(f"  [{status}] {test_id}: {test_name}")
    if message:
        print(f"       -> {message}")

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
        "details": details
    })


async def login(page):
    """개인계정으로 로그인"""
    await page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
    await page.fill('input[name="username"]', PERSONAL_ACCOUNT["username"])
    await page.fill('input[name="password"]', PERSONAL_ACCOUNT["password"])
    await page.click('button[type="submit"]')
    await page.wait_for_load_state("networkidle", timeout=10000)
    return page.url


async def logout(page):
    """로그아웃"""
    try:
        await page.goto(LOGOUT_URL, wait_until="networkidle", timeout=5000)
    except:
        pass


async def test_tc_p_001_login(page):
    """TC-P-001: 개인계정 로그인 성공"""
    print("\n[TC-P-001] 개인계정 로그인 테스트")
    print("-" * 60)

    try:
        final_url = await login(page)

        # 1. 리다이렉트 확인
        if "/personal/dashboard" in final_url:
            log_result("TC-P-001-1", "대시보드 리다이렉트", True, final_url)
        else:
            log_result("TC-P-001-1", "대시보드 리다이렉트", False,
                      f"예상: /personal/dashboard, 실제: {final_url}")

        # 2. 환영 메시지 확인
        flash_messages = await page.locator('.alert, .flash-message, [class*="flash"]').all_text_contents()
        welcome_found = any("환영" in msg or "로그인" in msg for msg in flash_messages)
        log_result("TC-P-001-2", "환영 메시지 표시", welcome_found,
                  str(flash_messages) if flash_messages else "메시지 없음")

        # 3. 세션 쿠키 확인
        cookies = await page.context.cookies()
        session_cookie = any('session' in c['name'].lower() for c in cookies)
        log_result("TC-P-001-3", "세션 쿠키 설정", session_cookie)

        return True
    except Exception as e:
        log_result("TC-P-001", "로그인", False, str(e))
        return False


async def test_tc_p_002_profile_view(page):
    """TC-P-002: 프로필 조회 페이지 접근"""
    print("\n[TC-P-002] 프로필 조회 페이지 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/", wait_until="networkidle", timeout=30000)

        # 1. 페이지 로드 확인
        page_title = await page.title()
        content = await page.content()

        if "프로필" in page_title or "프로필" in content or "profile" in content.lower():
            log_result("TC-P-002-1", "프로필 페이지 로드", True)
        else:
            log_result("TC-P-002-1", "프로필 페이지 로드", False, f"URL: {page.url}")

        # 2. 기본 정보 섹션 확인
        basic_section = await page.locator('[data-section="basic"], .basic-info, .profile-basic, .card').first.is_visible()
        log_result("TC-P-002-2", "기본 정보 섹션 표시", basic_section)

        # 3. 이력 섹션 확인 (학력, 경력 등)
        education_visible = await page.locator('text=학력').first.is_visible() if await page.locator('text=학력').count() > 0 else False
        career_visible = await page.locator('text=경력').first.is_visible() if await page.locator('text=경력').count() > 0 else False

        log_result("TC-P-002-3", "이력 섹션 표시", education_visible or career_visible,
                  f"학력: {education_visible}, 경력: {career_visible}")

        return True
    except Exception as e:
        log_result("TC-P-002", "프로필 조회", False, str(e))
        return False


async def test_tc_p_003_profile_edit_page(page):
    """TC-P-003: 프로필 수정 페이지 접근"""
    print("\n[TC-P-003] 프로필 수정 페이지 접근 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 1. 수정 페이지 로드 확인
        page_url = page.url
        if "/profile/edit" in page_url or "/personal/profile/edit" in page_url:
            log_result("TC-P-003-1", "수정 페이지 접근", True, page_url)
        else:
            log_result("TC-P-003-1", "수정 페이지 접근", False,
                      f"리다이렉트됨: {page_url}", "BE-REDIRECT")

        # 2. 폼 존재 확인
        form_exists = await page.locator('form').count() > 0
        log_result("TC-P-003-2", "수정 폼 존재", form_exists)

        # 3. 이름 필드에 기존 데이터 채워짐 확인
        name_input = page.locator('input[name="name"]')
        if await name_input.count() > 0:
            name_value = await name_input.input_value()
            log_result("TC-P-003-3", "기존 데이터 로드", bool(name_value),
                      f"이름: {name_value}" if name_value else "이름 필드 비어있음")
        else:
            log_result("TC-P-003-3", "이름 필드 존재", False, "name 필드를 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-003", "프로필 수정 페이지", False, str(e))
        return False


async def test_tc_p_004_profile_edit_save(page):
    """TC-P-004: 기본 정보 수정 및 저장"""
    print("\n[TC-P-004] 기본 정보 수정 및 저장 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 1. 기존 값 저장
        name_input = page.locator('input[name="name"]')
        original_name = ""
        if await name_input.count() > 0:
            original_name = await name_input.input_value()

        # 2. 휴대폰 번호 수정 (다른 필드로 테스트)
        phone_input = page.locator('input[name="mobile_phone"], input[name="phone"]')
        if await phone_input.count() > 0:
            test_phone = "010-9999-8888"
            await phone_input.fill(test_phone)
            log_result("TC-P-004-1", "휴대폰 번호 입력", True, test_phone)
        else:
            log_result("TC-P-004-1", "휴대폰 필드 존재", False, "phone 필드를 찾을 수 없음")

        # 3. 저장 버튼 클릭
        submit_btn = page.locator('button[type="submit"], input[type="submit"], .btn-primary:has-text("저장"), .btn-primary:has-text("수정")')
        if await submit_btn.count() > 0:
            await submit_btn.first.click()
            await page.wait_for_load_state("networkidle", timeout=10000)

            # 4. 성공 메시지 확인
            flash_messages = await page.locator('.alert-success, .toast-success, [class*="success"]').all_text_contents()
            success_found = any("수정" in msg or "저장" in msg or "성공" in msg for msg in flash_messages)

            if success_found:
                log_result("TC-P-004-2", "저장 성공 메시지", True, str(flash_messages))
            else:
                # 에러 메시지 확인
                error_messages = await page.locator('.alert-danger, .alert-error, [class*="error"]').all_text_contents()
                log_result("TC-P-004-2", "저장 성공 메시지", False,
                          f"에러: {error_messages}" if error_messages else "메시지 없음")
        else:
            log_result("TC-P-004-2", "저장 버튼 존재", False, "submit 버튼을 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-004", "프로필 저장", False, str(e))
        return False


async def test_tc_p_005_education_add(page):
    """TC-P-005: 학력 정보 추가"""
    print("\n[TC-P-005] 학력 정보 추가 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 1. 학력 추가 버튼 찾기
        add_btn = page.locator('button:has-text("학력 추가"), .add-education-btn, [data-add="education"]')
        if await add_btn.count() > 0:
            # 기존 학력 수 확인
            education_rows_before = await page.locator('[data-education-row], .education-row, .education-item').count()

            await add_btn.first.click()
            await page.wait_for_timeout(500)

            # 새 행 추가 확인
            education_rows_after = await page.locator('[data-education-row], .education-row, .education-item').count()

            if education_rows_after > education_rows_before:
                log_result("TC-P-005-1", "학력 행 동적 추가", True,
                          f"{education_rows_before} -> {education_rows_after}")
            else:
                log_result("TC-P-005-1", "학력 행 동적 추가", False,
                          "행이 추가되지 않음", "FE-DYNAMIC-ROW")
        else:
            # 다른 방식으로 학력 추가 가능한지 확인
            log_result("TC-P-005-1", "학력 추가 버튼", False,
                      "학력 추가 버튼을 찾을 수 없음 - 다른 UI 패턴일 수 있음")

        # 2. 학력 입력 필드 확인
        school_input = page.locator('input[name*="school_name"], input[name*="education"][name*="school"]')
        if await school_input.count() > 0:
            await school_input.last.fill("E2E테스트대학교")
            log_result("TC-P-005-2", "학교명 입력", True, "E2E테스트대학교")
        else:
            log_result("TC-P-005-2", "학교명 필드", False, "school_name 필드를 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-005", "학력 추가", False, str(e))
        return False


async def test_tc_p_006_education_delete(page):
    """TC-P-006: 학력 정보 삭제"""
    print("\n[TC-P-006] 학력 정보 삭제 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 학력 삭제 버튼 찾기
        delete_btn = page.locator('[data-education-row] .btn-delete, .education-row .delete-btn, button:has-text("삭제"):near(:text("학력"))')

        if await delete_btn.count() > 0:
            education_rows_before = await page.locator('[data-education-row], .education-row').count()

            await delete_btn.first.click()
            await page.wait_for_timeout(500)

            education_rows_after = await page.locator('[data-education-row], .education-row').count()

            if education_rows_after < education_rows_before:
                log_result("TC-P-006-1", "학력 행 삭제", True,
                          f"{education_rows_before} -> {education_rows_after}")
            else:
                log_result("TC-P-006-1", "학력 행 삭제", False, "행이 삭제되지 않음")
        else:
            log_result("TC-P-006-1", "학력 삭제 버튼", False,
                      "삭제 버튼을 찾을 수 없음 (학력이 없거나 UI 다름)")

        return True
    except Exception as e:
        log_result("TC-P-006", "학력 삭제", False, str(e))
        return False


async def test_tc_p_007_career_add(page):
    """TC-P-007: 경력 정보 추가"""
    print("\n[TC-P-007] 경력 정보 추가 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 경력 추가 버튼 찾기
        add_btn = page.locator('button:has-text("경력 추가"), .add-career-btn, [data-add="career"]')

        if await add_btn.count() > 0:
            await add_btn.first.click()
            await page.wait_for_timeout(500)
            log_result("TC-P-007-1", "경력 추가 버튼 클릭", True)
        else:
            log_result("TC-P-007-1", "경력 추가 버튼", False, "버튼을 찾을 수 없음")

        # 경력 입력 필드 확인
        company_input = page.locator('input[name*="company_name"], input[name*="career"][name*="company"]')
        if await company_input.count() > 0:
            await company_input.last.fill("E2E테스트회사")
            log_result("TC-P-007-2", "회사명 입력", True, "E2E테스트회사")
        else:
            log_result("TC-P-007-2", "회사명 필드", False, "company_name 필드를 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-007", "경력 추가", False, str(e))
        return False


async def test_tc_p_008_certificate_crud(page):
    """TC-P-008: 자격증 CRUD"""
    print("\n[TC-P-008] 자격증 CRUD 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 자격증 섹션 확인
        cert_section = await page.locator('text=자격증').count() > 0
        log_result("TC-P-008-1", "자격증 섹션 존재", cert_section)

        # 자격증 추가 버튼
        add_btn = page.locator('button:has-text("자격증 추가"), .add-certificate-btn, [data-add="certificate"]')
        if await add_btn.count() > 0:
            await add_btn.first.click()
            await page.wait_for_timeout(500)
            log_result("TC-P-008-2", "자격증 추가 버튼", True)
        else:
            log_result("TC-P-008-2", "자격증 추가 버튼", False, "버튼을 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-008", "자격증 CRUD", False, str(e))
        return False


async def test_tc_p_009_language_crud(page):
    """TC-P-009: 어학 CRUD"""
    print("\n[TC-P-009] 어학 CRUD 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 어학 섹션 확인
        lang_section = await page.locator('text=어학').count() > 0
        log_result("TC-P-009-1", "어학 섹션 존재", lang_section)

        # 어학 추가 버튼
        add_btn = page.locator('button:has-text("어학 추가"), .add-language-btn, [data-add="language"]')
        if await add_btn.count() > 0:
            await add_btn.first.click()
            await page.wait_for_timeout(500)
            log_result("TC-P-009-2", "어학 추가 버튼", True)
        else:
            log_result("TC-P-009-2", "어학 추가 버튼", False, "버튼을 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-009", "어학 CRUD", False, str(e))
        return False


async def test_tc_p_010_military_save(page):
    """TC-P-010: 병역 정보 저장"""
    print("\n[TC-P-010] 병역 정보 저장 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 병역 섹션 확인
        military_section = await page.locator('text=병역').count() > 0
        log_result("TC-P-010-1", "병역 섹션 존재", military_section)

        # 병역 상태 선택
        military_select = page.locator('select[name*="military"], select[name*="service_type"]')
        if await military_select.count() > 0:
            options = await military_select.first.locator('option').all_text_contents()
            log_result("TC-P-010-2", "병역 선택 옵션", True, str(options))
        else:
            log_result("TC-P-010-2", "병역 선택 필드", False, "select 필드를 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-010", "병역 정보", False, str(e))
        return False


async def test_tc_p_011_photo_upload(page):
    """TC-P-011: 프로필 사진 업로드"""
    print("\n[TC-P-011] 프로필 사진 업로드 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 사진 업로드 input 찾기
        photo_input = page.locator('input[type="file"][name*="photo"], input[type="file"][accept*="image"]')

        if await photo_input.count() > 0:
            log_result("TC-P-011-1", "사진 업로드 필드 존재", True)

            # 미리보기 영역 확인
            preview = await page.locator('#photoPreview, #previewImage, .photo-preview, .profile-photo').count() > 0
            log_result("TC-P-011-2", "사진 미리보기 영역", preview)
        else:
            log_result("TC-P-011-1", "사진 업로드 필드", False, "file input을 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-011", "사진 업로드", False, str(e))
        return False


async def test_tc_p_012_photo_delete(page):
    """TC-P-012: 프로필 사진 삭제"""
    print("\n[TC-P-012] 프로필 사진 삭제 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 사진 삭제 버튼 찾기
        delete_btn = page.locator('#deletePhotoBtn, .photo-delete-btn, button:has-text("사진 삭제")')

        if await delete_btn.count() > 0:
            log_result("TC-P-012-1", "사진 삭제 버튼 존재", True)
        else:
            log_result("TC-P-012-1", "사진 삭제 버튼", False,
                      "삭제 버튼을 찾을 수 없음 (사진이 없거나 UI 다름)")

        return True
    except Exception as e:
        log_result("TC-P-012", "사진 삭제", False, str(e))
        return False


async def test_tc_p_015_required_field_validation(page):
    """TC-P-015: 필수 필드 누락 검증"""
    print("\n[TC-P-015] 필수 필드 누락 검증 테스트")
    print("-" * 60)

    try:
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 이름 필드를 비우고 저장 시도
        name_input = page.locator('input[name="name"]')
        if await name_input.count() > 0:
            await name_input.fill("")

            # 저장 버튼 클릭
            submit_btn = page.locator('button[type="submit"], input[type="submit"]')
            if await submit_btn.count() > 0:
                await submit_btn.first.click()
                await page.wait_for_timeout(1000)

                # HTML5 유효성 검사 또는 커스텀 에러 메시지 확인
                validation_message = await name_input.evaluate("el => el.validationMessage")
                error_visible = await page.locator('.form-error, .invalid-feedback, [data-error], .error-message').count() > 0

                if validation_message or error_visible:
                    log_result("TC-P-015-1", "필수 필드 검증", True,
                              validation_message or "에러 메시지 표시됨")
                else:
                    # 폼이 제출되었는지 확인 (URL 변경)
                    if "/profile/edit" in page.url:
                        log_result("TC-P-015-1", "필수 필드 검증", True,
                                  "폼 제출 방지됨 (같은 페이지)")
                    else:
                        log_result("TC-P-015-1", "필수 필드 검증", False,
                                  "빈 이름으로 제출됨", "FE-002")
        else:
            log_result("TC-P-015-1", "이름 필드", False, "name 필드를 찾을 수 없음")

        return True
    except Exception as e:
        log_result("TC-P-015", "필수 필드 검증", False, str(e))
        return False


async def test_tc_p_016_session_expiry(page):
    """TC-P-016: 세션 만료 처리"""
    print("\n[TC-P-016] 세션 만료 처리 테스트")
    print("-" * 60)

    try:
        # 로그인 후 세션 쿠키 삭제
        await login(page)

        # 쿠키 삭제
        await page.context.clear_cookies()

        # 프로필 페이지 접근 시도
        await page.goto(f"{BASE_URL}/profile/edit", wait_until="networkidle", timeout=30000)

        # 로그인 페이지로 리다이렉트 확인
        if "/auth/login" in page.url or "/login" in page.url:
            log_result("TC-P-016-1", "세션 만료 시 로그인 리다이렉트", True, page.url)
        else:
            log_result("TC-P-016-1", "세션 만료 시 로그인 리다이렉트", False,
                      f"리다이렉트 안됨: {page.url}", "BE-SESSION")

        return True
    except Exception as e:
        log_result("TC-P-016", "세션 만료", False, str(e))
        return False


async def test_tc_p_017_dashboard_stats(page):
    """TC-P-017: 대시보드 통계 확인"""
    print("\n[TC-P-017] 대시보드 통계 확인 테스트")
    print("-" * 60)

    try:
        await login(page)
        await page.goto(f"{BASE_URL}/personal/dashboard", wait_until="networkidle", timeout=30000)

        # 사용자 정보 표시 확인
        user_info = await page.locator('.user-info, .dashboard-header, .profile-name').count() > 0
        log_result("TC-P-017-1", "사용자 정보 표시", user_info)

        # 통계 카드 확인
        stats = await page.locator('.stat-card, .stats-card, [data-stat]').count()
        log_result("TC-P-017-2", "통계 카드 표시", stats > 0, f"카드 수: {stats}")

        return True
    except Exception as e:
        log_result("TC-P-017", "대시보드 통계", False, str(e))
        return False


async def test_tc_p_018_api_endpoints(page):
    """TC-P-018: API 엔드포인트 직접 테스트"""
    print("\n[TC-P-018] API 엔드포인트 테스트")
    print("-" * 60)

    try:
        await login(page)

        # 학력 API 테스트
        response = await page.request.get(f"{BASE_URL}/personal/education")
        if response.ok:
            data = await response.json()
            log_result("TC-P-018-1", "학력 API GET", True,
                      f"status: {response.status}")
        else:
            log_result("TC-P-018-1", "학력 API GET", False,
                      f"status: {response.status}")

        # 경력 API 테스트
        response = await page.request.get(f"{BASE_URL}/personal/career")
        if response.ok:
            log_result("TC-P-018-2", "경력 API GET", True)
        else:
            log_result("TC-P-018-2", "경력 API GET", False,
                      f"status: {response.status}")

        return True
    except Exception as e:
        log_result("TC-P-018", "API 테스트", False, str(e))
        return False


async def test_tc_p_020_unauthorized_access(page):
    """TC-P-020: 비인가 접근 차단 테스트"""
    print("\n[TC-P-020] 비인가 접근 차단 테스트")
    print("-" * 60)

    try:
        await login(page)

        # 법인 기능 접근 시도
        await page.goto(f"{BASE_URL}/employees/", wait_until="networkidle", timeout=30000)

        # 접근 차단 확인 (리다이렉트 또는 403)
        if "/employees/" not in page.url or "403" in await page.content():
            log_result("TC-P-020-1", "법인 기능 접근 차단", True,
                      f"리다이렉트: {page.url}")
        else:
            # 페이지 내용 확인 (에러 메시지)
            content = await page.content()
            if "권한" in content or "접근" in content or "error" in content.lower():
                log_result("TC-P-020-1", "법인 기능 접근 차단", True,
                          "에러 메시지 표시")
            else:
                log_result("TC-P-020-1", "법인 기능 접근 차단", False,
                          "개인계정으로 법인 기능 접근 가능", "BE-003")

        return True
    except Exception as e:
        log_result("TC-P-020", "비인가 접근", False, str(e))
        return False


async def run_all_tests():
    """모든 E2E 테스트 실행"""
    print("=" * 80)
    print("개인계정 프로필 E2E 테스트 시작")
    print(f"테스트 시작 시간: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"테스트 계정: {PERSONAL_ACCOUNT['username']}")
    print("=" * 80)

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context()
        page = await context.new_page()

        try:
            # Phase 1: 핵심 기능
            print("\n" + "=" * 80)
            print("Phase 1: 핵심 기능 테스트")
            print("=" * 80)

            await test_tc_p_001_login(page)
            await test_tc_p_002_profile_view(page)
            await test_tc_p_003_profile_edit_page(page)
            await test_tc_p_004_profile_edit_save(page)
            await test_tc_p_005_education_add(page)

            # Phase 2: 이력 CRUD
            print("\n" + "=" * 80)
            print("Phase 2: 이력 CRUD 테스트")
            print("=" * 80)

            await test_tc_p_006_education_delete(page)
            await test_tc_p_007_career_add(page)
            await test_tc_p_008_certificate_crud(page)
            await test_tc_p_009_language_crud(page)
            await test_tc_p_010_military_save(page)

            # Phase 3: 첨부파일
            print("\n" + "=" * 80)
            print("Phase 3: 첨부파일 테스트")
            print("=" * 80)

            await test_tc_p_011_photo_upload(page)
            await test_tc_p_012_photo_delete(page)

            # Phase 4: Edge Cases
            print("\n" + "=" * 80)
            print("Phase 4: Edge Cases 테스트")
            print("=" * 80)

            await test_tc_p_015_required_field_validation(page)
            await logout(page)
            await test_tc_p_016_session_expiry(page)
            await test_tc_p_017_dashboard_stats(page)
            await test_tc_p_018_api_endpoints(page)
            await test_tc_p_020_unauthorized_access(page)

        finally:
            await browser.close()

    # 결과 요약
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    print(f"\n총 테스트: {test_results['total']}개")
    print(f"통과: {test_results['passed']}개")
    print(f"실패: {test_results['failed']}개")
    print(f"통과율: {(test_results['passed'] / test_results['total'] * 100):.1f}%" if test_results['total'] > 0 else "N/A")

    if test_results['bugs']:
        print("\n" + "-" * 40)
        print("발견된 버그:")
        print("-" * 40)
        for bug in test_results['bugs']:
            print(f"  [{bug['test_id']}] {bug.get('bug_id', 'N/A')}: {bug['message']}")

    # 결과 저장
    output_file = f"personal_profile_e2e_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(test_results, f, ensure_ascii=False, indent=2)

    print(f"\n상세 결과가 {output_file}에 저장되었습니다.")

    return test_results


if __name__ == "__main__":
    asyncio.run(run_all_tests())
