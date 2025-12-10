/**
 * formatters.js - 입력 포맷팅 유틸리티
 * 
 * 포함 기능:
 * - formatPhoneNumber: 전화번호 포맷팅 (010-1234-5678)
 * - formatBusinessNumber: 사업자등록번호 포맷팅 (123-45-67890)
 * - initPhoneInputs: 전화번호 입력 필드 자동 초기화
 * - initBusinessNumberInputs: 사업자등록번호 입력 필드 자동 초기화
 */

/**
 * 전화번호 포맷팅 (숫자만 추출 후 하이픈 추가)
 * @param {string} value - 입력값
 * @returns {string} 포맷팅된 전화번호 (예: 010-1234-5678)
 */
export function formatPhoneNumber(value) {
    let cleaned = value.replace(/[^0-9]/g, '');
    if (cleaned.length > 11) cleaned = cleaned.slice(0, 11);
    
    if (cleaned.length > 7) {
        return cleaned.slice(0, 3) + '-' + cleaned.slice(3, 7) + '-' + cleaned.slice(7);
    } else if (cleaned.length > 3) {
        return cleaned.slice(0, 3) + '-' + cleaned.slice(3);
    }
    return cleaned;
}

/**
 * 사업자등록번호 포맷팅 (숫자만 추출 후 하이픈 추가)
 * @param {string} value - 입력값
 * @returns {string} 포맷팅된 사업자등록번호 (예: 123-45-67890)
 */
export function formatBusinessNumber(value) {
    let cleaned = value.replace(/[^0-9]/g, '');
    if (cleaned.length > 10) cleaned = cleaned.slice(0, 10);
    
    if (cleaned.length > 5) {
        return cleaned.slice(0, 3) + '-' + cleaned.slice(3, 5) + '-' + cleaned.slice(5);
    } else if (cleaned.length > 3) {
        return cleaned.slice(0, 3) + '-' + cleaned.slice(3);
    }
    return cleaned;
}

/**
 * 전화번호 입력 필드에 자동 포맷팅 이벤트 바인딩
 * @param {string} selector - CSS 선택자 (기본값: 'input[type="tel"]')
 */
export function initPhoneInputs(selector = 'input[type="tel"]') {
    document.querySelectorAll(selector).forEach(function(input) {
        input.addEventListener('input', function(e) {
            e.target.value = formatPhoneNumber(e.target.value);
        });
    });
}

/**
 * 사업자등록번호 입력 필드에 자동 포맷팅 이벤트 바인딩
 * @param {string} selector - CSS 선택자
 */
export function initBusinessNumberInputs(selector = '.business-number-input') {
    document.querySelectorAll(selector).forEach(function(input) {
        input.addEventListener('input', function(e) {
            e.target.value = formatBusinessNumber(e.target.value);
        });
    });
}

/**
 * 날짜 포맷팅 (ISO 문자열 -> 한국어 로컬 표시)
 * @param {string} dateStr - ISO 날짜 문자열
 * @returns {string} 포맷팅된 날짜 문자열
 */
export function formatDate(dateStr) {
    if (\!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleString('ko-KR');
}

/**
 * 날짜만 포맷팅 (시간 제외)
 * @param {string} dateStr - ISO 날짜 문자열
 * @returns {string} 포맷팅된 날짜 문자열 (YYYY-MM-DD)
 */
export function formatDateOnly(dateStr) {
    if (\!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR');
}

/**
 * 금액 포맷팅 (천 단위 콤마)
 * @param {number|string} value - 금액
 * @returns {string} 포맷팅된 금액
 */
export function formatCurrency(value) {
    if (value === null || value === undefined) return '-';
    return Number(value).toLocaleString('ko-KR') + '원';
}

// 전역 함수로 노출 (비모듈 환경 호환)
if (typeof window \!== 'undefined') {
    window.HRFormatters = {
        formatPhoneNumber,
        formatBusinessNumber,
        initPhoneInputs,
        initBusinessNumberInputs,
        formatDate,
        formatDateOnly,
        formatCurrency
    };
}
