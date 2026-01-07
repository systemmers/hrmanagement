/**
 * 유효성 검증 유틸리티
 * Phase 7: 프론트엔드 리팩토링
 *
 * 폼 필드 및 데이터 유효성 검증 함수를 제공합니다.
 */

/**
 * 필수 값 검증
 * @param {*} value - 검증할 값
 * @returns {boolean} 유효 여부
 */
export function isRequired(value) {
    if (value === null || value === undefined) return false;
    if (typeof value === 'string') return value.trim().length > 0;
    if (Array.isArray(value)) return value.length > 0;
    return true;
}

/**
 * 이메일 형식 검증
 * @param {string} email - 이메일 주소
 * @returns {boolean} 유효 여부
 */
export function isEmail(email) {
    if (!email) return false;
    const pattern = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
    return pattern.test(email.trim());
}

/**
 * 전화번호 형식 검증
 * @param {string} phone - 전화번호
 * @returns {boolean} 유효 여부
 */
export function isPhone(phone) {
    if (!phone) return false;
    const cleaned = phone.replace(/\D/g, '');
    return cleaned.length >= 10 && cleaned.length <= 11;
}

/**
 * 숫자 검증
 * @param {*} value - 검증할 값
 * @returns {boolean} 유효 여부
 */
export function isNumber(value) {
    if (value === null || value === undefined || value === '') return false;
    return !isNaN(parseFloat(value)) && isFinite(value);
}

/**
 * 정수 검증
 * @param {*} value - 검증할 값
 * @returns {boolean} 유효 여부
 */
export function isInteger(value) {
    return isNumber(value) && Number.isInteger(parseFloat(value));
}

/**
 * 양수 검증
 * @param {*} value - 검증할 값
 * @returns {boolean} 유효 여부
 */
export function isPositive(value) {
    return isNumber(value) && parseFloat(value) > 0;
}

/**
 * 범위 검증
 * @param {number} value - 검증할 값
 * @param {number} min - 최소값
 * @param {number} max - 최대값
 * @returns {boolean} 유효 여부
 */
export function isInRange(value, min, max) {
    if (!isNumber(value)) return false;
    const num = parseFloat(value);
    return num >= min && num <= max;
}

/**
 * 문자열 길이 검증
 * @param {string} value - 검증할 문자열
 * @param {number} min - 최소 길이
 * @param {number} max - 최대 길이
 * @returns {boolean} 유효 여부
 */
export function isLength(value, min, max) {
    if (typeof value !== 'string') return false;
    const len = value.trim().length;
    return len >= min && len <= max;
}

/**
 * 날짜 형식 검증 (YYYY-MM-DD)
 * @param {string} date - 날짜 문자열
 * @returns {boolean} 유효 여부
 */
export function isDate(date) {
    if (!date) return false;
    const pattern = /^\d{4}-\d{2}-\d{2}$/;
    if (!pattern.test(date)) return false;
    const d = new Date(date);
    return !isNaN(d.getTime());
}

/**
 * 사업자등록번호 검증
 * @param {string} number - 사업자등록번호
 * @returns {boolean} 유효 여부
 */
export function isBusinessNumber(number) {
    if (!number) return false;
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length !== 10) return false;

    // 사업자등록번호 체크섬 검증
    const checkKeys = [1, 3, 7, 1, 3, 7, 1, 3, 5];
    let sum = 0;

    for (let i = 0; i < 9; i++) {
        sum += parseInt(cleaned[i]) * checkKeys[i];
    }
    sum += Math.floor((parseInt(cleaned[8]) * 5) / 10);

    const checkDigit = (10 - (sum % 10)) % 10;
    return checkDigit === parseInt(cleaned[9]);
}

/**
 * 주민등록번호 앞자리 검증 (생년월일)
 * @param {string} number - 주민등록번호 앞 6자리
 * @returns {boolean} 유효 여부
 */
export function isBirthDate(number) {
    if (!number) return false;
    const cleaned = number.replace(/\D/g, '');
    if (cleaned.length !== 6) return false;

    const year = parseInt(cleaned.substring(0, 2));
    const month = parseInt(cleaned.substring(2, 4));
    const day = parseInt(cleaned.substring(4, 6));

    if (month < 1 || month > 12) return false;
    if (day < 1 || day > 31) return false;

    return true;
}

/**
 * 파일 확장자 검증
 * @param {string} filename - 파일명
 * @param {string[]} allowedExtensions - 허용 확장자 목록
 * @returns {boolean} 유효 여부
 */
export function isAllowedExtension(filename, allowedExtensions) {
    if (!filename || !allowedExtensions?.length) return false;
    const ext = filename.split('.').pop()?.toLowerCase();
    return allowedExtensions.includes(ext);
}

/**
 * 파일 크기 검증
 * @param {number} size - 파일 크기 (bytes)
 * @param {number} maxSizeMB - 최대 크기 (MB)
 * @returns {boolean} 유효 여부
 */
export function isAllowedFileSize(size, maxSizeMB) {
    const maxBytes = maxSizeMB * 1024 * 1024;
    return size <= maxBytes;
}

/**
 * URL 형식 검증
 * @param {string} url - URL 문자열
 * @returns {boolean} 유효 여부
 */
export function isUrl(url) {
    if (!url) return false;
    try {
        new URL(url);
        return true;
    } catch {
        return false;
    }
}

/**
 * 폼 유효성 검증 결과 객체
 */
export class ValidationResult {
    constructor() {
        this.errors = {};
        this.isValid = true;
    }

    /**
     * 에러 추가
     * @param {string} field - 필드명
     * @param {string} message - 에러 메시지
     */
    addError(field, message) {
        this.errors[field] = message;
        this.isValid = false;
    }

    /**
     * 특정 필드 에러 가져오기
     * @param {string} field - 필드명
     * @returns {string|null} 에러 메시지
     */
    getError(field) {
        return this.errors[field] || null;
    }

    /**
     * 모든 에러 메시지 가져오기
     * @returns {string[]} 에러 메시지 배열
     */
    getAllErrors() {
        return Object.values(this.errors);
    }

    /**
     * 첫 번째 에러 메시지 가져오기
     * @returns {string|null} 에러 메시지
     */
    getFirstError() {
        const errors = this.getAllErrors();
        return errors.length > 0 ? errors[0] : null;
    }
}

/**
 * 폼 필드 검증기
 * @param {Object} rules - 검증 규칙 ({ fieldName: [validators] })
 * @param {Object} data - 검증할 데이터
 * @returns {ValidationResult} 검증 결과
 */
export function validateForm(rules, data) {
    const result = new ValidationResult();

    Object.entries(rules).forEach(([field, validators]) => {
        const value = data[field];

        for (const validator of validators) {
            const { validate, message } = validator;
            if (!validate(value, data)) {
                result.addError(field, message);
                break; // 첫 번째 에러만 기록
            }
        }
    });

    return result;
}

/**
 * 공통 검증 규칙 생성 헬퍼
 */
export const validators = {
    required: (message = '필수 입력 항목입니다.') => ({
        validate: isRequired,
        message
    }),

    email: (message = '올바른 이메일 형식이 아닙니다.') => ({
        validate: isEmail,
        message
    }),

    phone: (message = '올바른 전화번호 형식이 아닙니다.') => ({
        validate: isPhone,
        message
    }),

    number: (message = '숫자만 입력 가능합니다.') => ({
        validate: isNumber,
        message
    }),

    minLength: (min, message) => ({
        validate: (value) => !value || value.length >= min,
        message: message || `최소 ${min}자 이상 입력해주세요.`
    }),

    maxLength: (max, message) => ({
        validate: (value) => !value || value.length <= max,
        message: message || `최대 ${max}자까지 입력 가능합니다.`
    }),

    min: (minValue, message) => ({
        validate: (value) => !isNumber(value) || parseFloat(value) >= minValue,
        message: message || `${minValue} 이상의 값을 입력해주세요.`
    }),

    max: (maxValue, message) => ({
        validate: (value) => !isNumber(value) || parseFloat(value) <= maxValue,
        message: message || `${maxValue} 이하의 값을 입력해주세요.`
    }),

    pattern: (regex, message = '올바른 형식이 아닙니다.') => ({
        validate: (value) => !value || regex.test(value),
        message
    }),

    match: (fieldName, message = '값이 일치하지 않습니다.') => ({
        validate: (value, data) => value === data[fieldName],
        message
    })
};
