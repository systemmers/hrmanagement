/**
 * Form Validators Module
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 폼 유효성 검사 기능
 */

/**
 * 폼 유효성 검사 초기화
 */
export function initFormValidation() {
    const form = document.getElementById('employeeForm');

    if (!form) return;

    // 제출 시 유효성 검사
    form.addEventListener('submit', handleFormSubmit);

    // 입력 시 실시간 유효성 검사
    form.addEventListener('input', handleInputChange);
}

/**
 * 폼 제출 핸들러
 * @param {Event} e - 제출 이벤트
 */
function handleFormSubmit(e) {
    const form = e.target;
    const requiredFields = form.querySelectorAll('[required]');
    let isValid = true;
    let firstInvalidField = null;

    requiredFields.forEach(field => {
        if (!field.value.trim()) {
            isValid = false;
            field.classList.add('invalid');
            if (!firstInvalidField) {
                firstInvalidField = field;
            }
        } else {
            field.classList.remove('invalid');
        }
    });

    if (!isValid) {
        e.preventDefault();

        if (firstInvalidField) {
            firstInvalidField.focus();
            firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
        }

        alert('필수 입력 항목을 모두 입력해 주세요.');
    }
}

/**
 * 입력 변경 핸들러 (실시간 유효성 해제)
 * @param {Event} e - 입력 이벤트
 */
function handleInputChange(e) {
    if (e.target.classList.contains('invalid') && e.target.value.trim()) {
        e.target.classList.remove('invalid');
    }
}

/**
 * 특정 필드 유효성 검사
 * @param {HTMLElement} field - 검사할 필드
 * @returns {boolean} 유효 여부
 */
export function validateField(field) {
    const value = field.value.trim();
    const isRequired = field.hasAttribute('required');

    if (isRequired && !value) {
        field.classList.add('invalid');
        return false;
    }

    // 이메일 검사
    if (field.type === 'email' && value) {
        const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
        if (!emailRegex.test(value)) {
            field.classList.add('invalid');
            return false;
        }
    }

    // 전화번호 검사
    if (field.name && field.name.includes('phone') && value) {
        const phoneRegex = /^[\d\-\s]+$/;
        if (!phoneRegex.test(value)) {
            field.classList.add('invalid');
            return false;
        }
    }

    field.classList.remove('invalid');
    return true;
}

/**
 * 폼 전체 유효성 검사
 * @param {HTMLFormElement} form - 검사할 폼
 * @returns {boolean} 유효 여부
 */
export function validateForm(form) {
    const fields = form.querySelectorAll('input, select, textarea');
    let isValid = true;

    fields.forEach(field => {
        if (!validateField(field)) {
            isValid = false;
        }
    });

    return isValid;
}

export default {
    initFormValidation,
    validateField,
    validateForm
};
