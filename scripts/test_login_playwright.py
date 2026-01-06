"""
Playwright 로그인 테스트 스크립트

각 계정 유형별 로그인을 테스트하고 버그를 확인합니다.
"""
import asyncio
import json
import sys
from datetime import datetime
from playwright.async_api import async_playwright, TimeoutError as PlaywrightTimeoutError

# Windows 콘솔 인코딩 설정
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

BASE_URL = "http://localhost:5200"
LOGIN_URL = f"{BASE_URL}/auth/login"

# 테스트 계정 정보
TEST_ACCOUNTS = {
    "platform": {
        "username": "superadmin",
        "password": "test1234",
        "expected_redirect": "/platform/",
        "account_type": "platform"
    },
    "corporate": {
        "username": "admin_testa",
        "password": "test1234",
        "expected_redirect": "/",
        "account_type": "corporate"
    },
    "employee_sub": {
        "username": "emp_0001",
        "password": "test1234",
        "expected_redirect": "/profile/",
        "account_type": "employee_sub"
    },
    "personal": {
        "username": "personal_junhyuk.kim",
        "password": "test1234",
        "expected_redirect": "/personal/dashboard",
        "account_type": "personal"
    },
    # 문제가 있는 계정들
    "employee_sub_null_employee_id_1": {
        "username": "testuser456@test.com",  # User#69
        "password": "test1234",
        "expected_redirect": None,  # 예상: 에러 또는 강제 로그아웃
        "account_type": "employee_sub",
        "issue": "employee_id = NULL"
    },
    "employee_sub_null_employee_id_2": {
        "username": "testprovision02@testcorp.co.kr",  # User#70
        "password": "test1234",
        "expected_redirect": None,
        "account_type": "employee_sub",
        "issue": "employee_id = NULL"
    },
    # pending_info + approved 조합 계정
    "employee_sub_pending_info_1": {
        "username": "test_provision_user2",  # User#66, Employee#52
        "password": "test1234",
        "expected_redirect": "/profile/complete",
        "account_type": "employee_sub",
        "issue": "pending_info + approved"
    },
    "employee_sub_pending_info_2": {
        "username": "testprovision02@testcorp.co.kr",  # User#70, Employee#57
        "password": "test1234",
        "expected_redirect": "/profile/complete",
        "account_type": "employee_sub",
        "issue": "pending_info + approved"
    },
    "employee_sub_pending_info_3": {
        "username": "jongsun@naver.com",  # User#68, Employee#58 (이종선)
        "password": "test1234",
        "expected_redirect": "/profile/complete",
        "account_type": "employee_sub",
        "issue": "pending_info + approved"
    },
    # resigned 상태 계정
    "employee_sub_resigned_1": {
        "username": "emp_0003",  # User#8, Employee#3 (서현우)
        "password": "test1234",
        "expected_redirect": None,  # 예상: 처리 방식 확인 필요
        "account_type": "employee_sub",
        "issue": "resigned + approved"
    }
}


async def test_login(page, account_name, account_info):
    """단일 계정 로그인 테스트"""
    result = {
        "account_name": account_name,
        "account_type": account_info.get("account_type"),
        "username": account_info["username"],
        "timestamp": datetime.now().isoformat(),
        "success": False,
        "errors": [],
        "warnings": [],
        "redirect_url": None,
        "final_url": None,
        "page_title": None,
        "flash_messages": [],
        "session_data": {}
    }
    
    try:
        # 로그인 페이지로 이동
        await page.goto(LOGIN_URL, wait_until="networkidle", timeout=30000)
        await page.wait_for_timeout(2000)
        
        # 페이지 스크린샷 저장 (디버깅용)
        await page.screenshot(path=f"debug_{account_name}_before.png")
        
        # 페이지 내용 확인
        page_content = await page.content()
        if "username" not in page_content.lower():
            result["errors"].append(f"로그인 페이지가 로드되지 않았습니다. URL: {page.url}")
            result["page_content_preview"] = page_content[:500]
            return result
        
        # 로그인 폼 입력 (명확한 셀렉터 사용)
        try:
            username_input = page.locator('input[name="username"]')
            await username_input.wait_for(state="visible", timeout=5000)
        except Exception as e:
            result["errors"].append(f"사용자명 입력 필드를 찾을 수 없습니다: {str(e)}")
            # 모든 input 요소 확인
            all_inputs = await page.locator('input').all()
            input_info = []
            for inp in all_inputs:
                name = await inp.get_attribute('name')
                input_type = await inp.get_attribute('type')
                input_id = await inp.get_attribute('id')
                input_info.append(f"name={name}, type={input_type}, id={input_id}")
            result["errors"].append(f"발견된 input 요소: {input_info}")
            return result
        
        try:
            password_input = page.locator('input[name="password"]')
            await password_input.wait_for(state="visible", timeout=5000)
        except Exception as e:
            result["errors"].append(f"비밀번호 입력 필드를 찾을 수 없습니다: {str(e)}")
            return result
        
        await username_input.fill(account_info["username"])
        await password_input.fill(account_info["password"])
        
        # 로그인 버튼 클릭
        try:
            login_button = page.locator('button[type="submit"]')
            await login_button.wait_for(state="visible", timeout=5000)
            await login_button.click()
        except Exception as e:
            result["errors"].append(f"로그인 버튼을 찾을 수 없습니다: {str(e)}")
            return result
        
        # 리다이렉트 대기
        await page.wait_for_load_state("networkidle", timeout=10000)
        await page.wait_for_timeout(2000)
        
        # 최종 URL 확인
        result["final_url"] = page.url
        result["page_title"] = await page.title()
        
        # Flash 메시지 수집
        flash_messages = await page.locator('.alert, .flash-message, [class*="flash"]').all()
        for flash in flash_messages:
            text = await flash.text_content()
            if text:
                result["flash_messages"].append(text.strip())
        
        # 세션 데이터 확인 (쿠키에서)
        cookies = await page.context.cookies()
        session_cookie = next((c for c in cookies if 'session' in c['name'].lower()), None)
        if session_cookie:
            result["session_data"]["has_session"] = True
        
        # 예상 리다이렉트 확인
        if account_info.get("expected_redirect"):
            if account_info["expected_redirect"] in result["final_url"]:
                result["success"] = True
                result["redirect_url"] = result["final_url"]
            else:
                result["errors"].append(
                    f"예상 리다이렉트: {account_info['expected_redirect']}, "
                    f"실제 URL: {result['final_url']}"
                )
        else:
            # 예상 리다이렉트가 없는 경우 (문제 계정)
            result["warnings"].append("예상 리다이렉트가 정의되지 않음")
            result["success"] = True  # 일단 성공으로 처리 (버그 확인용)
        
        # 페이지 내용 확인
        page_content = await page.content()
        
        # 에러 메시지 확인
        if "error" in page_content.lower() or "오류" in page_content:
            error_elements = await page.locator('.error, .alert-danger, [class*="error"]').all()
            for elem in error_elements:
                text = await elem.text_content()
                if text:
                    result["errors"].append(text.strip())
        
        # 특정 버그 패턴 확인
        if account_info.get("issue") == "employee_id = NULL":
            if "계정에 연결된 직원 정보가 없습니다" in page_content:
                result["errors"].append("BUG E-1: employee_id = NULL로 인한 강제 로그아웃")
            elif "/auth/logout" in result["final_url"]:
                result["errors"].append("BUG E-1: 강제 로그아웃 발생")
        
        if "pending_info" in page_content and "approved" in str(result.get("session_data", {})):
            result["warnings"].append("BUG E-2: pending_info + approved 조합 가능성")
        
    except PlaywrightTimeoutError as e:
        result["errors"].append(f"타임아웃: {str(e)}")
    except Exception as e:
        result["errors"].append(f"예외 발생: {str(e)}")
    
    return result


async def run_all_tests():
    """모든 계정 유형별 로그인 테스트 실행"""
    results = []
    
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=False)  # headless=False로 브라우저 확인 가능
        context = await browser.new_context()
        page = await context.new_page()
        
        print("=" * 80)
        print("Playwright 로그인 테스트 시작")
        print("=" * 80)
        
        for account_name, account_info in TEST_ACCOUNTS.items():
            print(f"\n[테스트] {account_name} ({account_info['username']})")
            print("-" * 80)
            
            result = await test_login(page, account_name, account_info)
            results.append(result)
            
            # 결과 출력
            if result["success"]:
                print(f"[OK] 성공: {result['final_url']}")
            else:
                print(f"[FAIL] 실패: {result['final_url']}")
            
            if result["errors"]:
                print("  에러:")
                for error in result["errors"]:
                    print(f"    - {error}")
            
            if result["warnings"]:
                print("  경고:")
                for warning in result["warnings"]:
                    print(f"    - {warning}")
            
            if result["flash_messages"]:
                print("  Flash 메시지:")
                for msg in result["flash_messages"]:
                    print(f"    - {msg}")
            
            # 다음 테스트 전 로그아웃
            try:
                await page.goto(f"{BASE_URL}/auth/logout", wait_until="networkidle", timeout=5000)
                await page.wait_for_timeout(1000)
            except:
                pass
        
        await browser.close()
    
    # 결과 요약
    print("\n" + "=" * 80)
    print("테스트 결과 요약")
    print("=" * 80)
    
    success_count = sum(1 for r in results if r["success"])
    error_count = sum(1 for r in results if r["errors"])
    
    print(f"\n총 테스트: {len(results)}개")
    print(f"성공: {success_count}개")
    print(f"에러 발생: {error_count}개")
    
    # 버그 목록
    bugs = []
    for result in results:
        for error in result["errors"]:
            if "BUG" in error:
                bugs.append({
                    "account": result["account_name"],
                    "username": result["username"],
                    "bug": error
                })
    
    if bugs:
        print("\n발견된 버그:")
        for bug in bugs:
            print(f"  - [{bug['account']}] {bug['username']}: {bug['bug']}")
    
    # 결과를 JSON 파일로 저장
    output_file = f"login_test_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    
    print(f"\n상세 결과가 {output_file}에 저장되었습니다.")
    
    return results


if __name__ == "__main__":
    asyncio.run(run_all_tests())

