/**
 * Corporate Register Page JavaScript
 * 법인 회원가입 페이지
 *
 * Used by:
 * - templates/corporate/register.html
 *
 * Dependencies:
 * - js/utils/formatting.js (HRFormatters)
 * - js/services/contract-service.js (HRContractAPI)
 */

document.addEventListener('DOMContentLoaded', function() {
    initBusinessNumberFormatting();
    initBusinessNumberCheck();
});

/**
 * Initialize business number auto-formatting
 * 사업자등록번호 입력 시 자동 포맷팅 (000-00-00000)
 */
function initBusinessNumberFormatting() {
    if (!window.HRFormatters) return;

    const businessInput = document.getElementById('businessNumber');
    if (!businessInput) return;

    businessInput.addEventListener('input', function(e) {
        e.target.value = window.HRFormatters.formatBusinessNumber(e.target.value);
    });
}

/**
 * Initialize business number duplicate check button
 * 사업자등록번호 중복 확인 버튼 이벤트 바인딩
 */
function initBusinessNumberCheck() {
    const checkBtn = document.querySelector('[data-action="check-business-number"]');
    if (!checkBtn) return;

    checkBtn.addEventListener('click', checkBusinessNumber);
}

/**
 * Check business number availability via API
 * 사업자등록번호 중복 확인 API 호출
 */
async function checkBusinessNumber() {
    const input = document.getElementById('businessNumber');
    const resultDiv = document.getElementById('businessNumberResult');

    if (!input || !resultDiv) return;

    if (!window.HRContractAPI) {
        resultDiv.textContent = 'API를 사용할 수 없습니다.';
        resultDiv.className = 'auth-form__check-result auth-form__check-result--error';
        return;
    }

    const result = await window.HRContractAPI.checkBusinessNumber(input.value.trim());
    resultDiv.textContent = result.message;
    resultDiv.className = 'auth-form__check-result auth-form__check-result--' +
                          (result.available ? 'success' : 'error');
}
