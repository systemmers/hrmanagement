/**
 * 숫자/날짜 포맷팅 유틸리티
 * Phase 7: 프론트엔드 리팩토링
 *
 * 숫자, 통화, 날짜 등의 포맷팅 함수를 제공합니다.
 */

/**
 * 숫자를 천 단위 콤마 포맷으로 변환
 * @param {number|string} num - 포맷팅할 숫자
 * @returns {string} 포맷된 문자열
 */
export function formatNumber(num) {
    if (num === null || num === undefined || num === '') {
        return '0';
    }
    const number = typeof num === 'string' ? parseFloat(num.replace(/,/g, '')) : num;
    if (isNaN(number)) {
        return '0';
    }
    return number.toLocaleString('ko-KR');
}

/**
 * 포맷된 문자열을 숫자로 파싱
 * @param {string} str - 파싱할 문자열
 * @returns {number} 파싱된 숫자
 */
export function parseNumber(str) {
    if (str === null || str === undefined || str === '') {
        return 0;
    }
    const cleaned = String(str).replace(/,/g, '').trim();
    const number = parseFloat(cleaned);
    return isNaN(number) ? 0 : number;
}

/**
 * 통화 형식으로 포맷팅 (원화)
 * @param {number|string} amount - 금액
 * @param {boolean} showSymbol - 통화 기호 표시 여부
 * @returns {string} 포맷된 금액
 */
export function formatCurrency(amount, showSymbol = true) {
    const formatted = formatNumber(amount);
    return showSymbol ? `${formatted}원` : formatted;
}

/**
 * 퍼센트 형식으로 포맷팅
 * @param {number} value - 값 (0-100 또는 0-1)
 * @param {boolean} isDecimal - 0-1 범위인지 여부
 * @param {number} decimals - 소수점 자릿수
 * @returns {string} 포맷된 퍼센트
 */
export function formatPercent(value, isDecimal = false, decimals = 1) {
    if (value === null || value === undefined) {
        return '0%';
    }
    const percent = isDecimal ? value * 100 : value;
    return `${percent.toFixed(decimals)}%`;
}

/**
 * 날짜를 YYYY-MM-DD 형식으로 포맷팅
 * @param {Date|string} date - 날짜 객체 또는 문자열
 * @returns {string} 포맷된 날짜
 */
export function formatDate(date) {
    if (!date) {
        return '';
    }
    const d = date instanceof Date ? date : new Date(date);
    if (isNaN(d.getTime())) {
        return '';
    }
    const year = d.getFullYear();
    const month = String(d.getMonth() + 1).padStart(2, '0');
    const day = String(d.getDate()).padStart(2, '0');
    return `${year}-${month}-${day}`;
}

/**
 * 날짜를 한국어 형식으로 포맷팅
 * @param {Date|string} date - 날짜 객체 또는 문자열
 * @returns {string} 포맷된 날짜 (예: 2024년 1월 15일)
 */
export function formatDateKorean(date) {
    if (!date) {
        return '';
    }
    const d = date instanceof Date ? date : new Date(date);
    if (isNaN(d.getTime())) {
        return '';
    }
    return `${d.getFullYear()}년 ${d.getMonth() + 1}월 ${d.getDate()}일`;
}

/**
 * 전화번호 포맷팅
 * @param {string} phone - 전화번호
 * @returns {string} 포맷된 전화번호
 */
export function formatPhone(phone) {
    if (!phone) {
        return '';
    }
    const cleaned = phone.replace(/\D/g, '');
    if (cleaned.length === 11) {
        return cleaned.replace(/(\d{3})(\d{4})(\d{4})/, '$1-$2-$3');
    } else if (cleaned.length === 10) {
        return cleaned.replace(/(\d{3})(\d{3})(\d{4})/, '$1-$2-$3');
    }
    return phone;
}

/**
 * 사업자등록번호 포맷팅
 * @param {string} number - 사업자등록번호
 * @returns {string} 포맷된 번호 (예: 123-45-67890)
 */
export function formatBusinessNumber(number) {
    if (!number) {
        return '';
    }
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length === 10) {
        return cleaned.replace(/(\d{3})(\d{2})(\d{5})/, '$1-$2-$3');
    }
    return number;
}

/**
 * 파일 크기 포맷팅
 * @param {number} bytes - 바이트 수
 * @returns {string} 포맷된 크기
 */
export function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return parseFloat((bytes / Math.pow(k, i)).toFixed(2)) + ' ' + sizes[i];
}

/**
 * 날짜만 포맷팅 (시간 제외)
 * @param {string} dateStr - ISO 날짜 문자열
 * @returns {string} 포맷된 날짜 문자열 (YYYY-MM-DD)
 */
export function formatDateOnly(dateStr) {
    if (!dateStr) return '-';
    const date = new Date(dateStr);
    return date.toLocaleDateString('ko-KR');
}

/**
 * 전화번호 입력 필드에 자동 포맷 이벤트 바인딩
 * @param {string} selector - CSS 선택자 (기본값: 'input[type="tel"]')
 */
export function initPhoneInputs(selector = 'input[type="tel"]') {
    document.querySelectorAll(selector).forEach(function(input) {
        input.addEventListener('input', function(e) {
            let cleaned = e.target.value.replace(/[^0-9]/g, '');
            if (cleaned.length > 11) cleaned = cleaned.slice(0, 11);

            if (cleaned.length > 7) {
                e.target.value = cleaned.slice(0, 3) + '-' + cleaned.slice(3, 7) + '-' + cleaned.slice(7);
            } else if (cleaned.length > 3) {
                e.target.value = cleaned.slice(0, 3) + '-' + cleaned.slice(3);
            } else {
                e.target.value = cleaned;
            }
        });
    });
}

/**
 * 사업자등록번호 입력 필드에 자동 포맷 이벤트 바인딩
 * @param {string} selector - CSS 선택자
 */
export function initBusinessNumberInputs(selector = '.business-number-input') {
    document.querySelectorAll(selector).forEach(function(input) {
        input.addEventListener('input', function(e) {
            let cleaned = e.target.value.replace(/[^0-9]/g, '');
            if (cleaned.length > 10) cleaned = cleaned.slice(0, 10);

            if (cleaned.length > 5) {
                e.target.value = cleaned.slice(0, 3) + '-' + cleaned.slice(3, 5) + '-' + cleaned.slice(5);
            } else if (cleaned.length > 3) {
                e.target.value = cleaned.slice(0, 3) + '-' + cleaned.slice(3);
            } else {
                e.target.value = cleaned;
            }
        });
    });
}

// 전역 함수로 노출 (레거시 환경 호환)
if (typeof window !== 'undefined') {
    window.HRFormatters = {
        formatNumber,
        parseNumber,
        formatCurrency,
        formatPercent,
        formatDate,
        formatDateKorean,
        formatDateOnly,
        formatPhone,
        formatBusinessNumber,
        formatFileSize,
        initPhoneInputs,
        initBusinessNumberInputs
    };
}
