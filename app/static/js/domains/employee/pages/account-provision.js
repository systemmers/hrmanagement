/**
 * 직원 계정 발급 페이지 JavaScript
 *
 * 기능:
 * - 폼 유효성 검사
 * - 비밀번호 자동 생성
 * - 중복 제출 방지
 */

(function() {
    'use strict';

    // DOM Elements
    const form = document.getElementById('accountProvisionForm');
    const usernameInput = document.getElementById('username');
    const emailInput = document.getElementById('email');
    const passwordInput = document.getElementById('password');
    const generatePasswordBtn = document.getElementById('generatePasswordBtn');

    /**
     * 안전한 랜덤 비밀번호 생성
     * @param {number} length - 비밀번호 길이
     * @returns {string} 생성된 비밀번호
     */
    function generatePassword(length = 12) {
        const lowercase = 'abcdefghijklmnopqrstuvwxyz';
        const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
        const numbers = '0123456789';
        const special = '!@#$%';
        const allChars = lowercase + uppercase + numbers + special;

        let password = '';

        // 각 문자 유형 최소 1개씩 포함
        password += lowercase[Math.floor(Math.random() * lowercase.length)];
        password += uppercase[Math.floor(Math.random() * uppercase.length)];
        password += numbers[Math.floor(Math.random() * numbers.length)];
        password += special[Math.floor(Math.random() * special.length)];

        // 나머지 길이 채우기
        for (let i = password.length; i < length; i++) {
            password += allChars[Math.floor(Math.random() * allChars.length)];
        }

        // 셔플
        return password.split('').sort(() => Math.random() - 0.5).join('');
    }

    /**
     * 사용자명 유효성 검사
     * @param {string} username
     * @returns {object} { valid: boolean, message: string }
     */
    function validateUsername(username) {
        if (!username || username.length < 4) {
            return { valid: false, message: '사용자명은 4자 이상이어야 합니다.' };
        }
        if (!/^[a-zA-Z0-9_]+$/.test(username)) {
            return { valid: false, message: '사용자명은 영문, 숫자, 밑줄(_)만 사용할 수 있습니다.' };
        }
        return { valid: true, message: '' };
    }

    /**
     * 이메일 유효성 검사
     * @param {string} email
     * @returns {object} { valid: boolean, message: string }
     */
    function validateEmail(email) {
        if (!email || !email.includes('@')) {
            return { valid: false, message: '올바른 이메일 형식이 아닙니다.' };
        }
        return { valid: true, message: '' };
    }

    /**
     * 입력 필드 에러 표시
     * @param {HTMLElement} input
     * @param {string} message
     */
    function showError(input, message) {
        const formGroup = input.closest('.form__group');
        const existingError = formGroup.querySelector('.form__error');

        if (existingError) {
            existingError.textContent = message;
        } else {
            const errorEl = document.createElement('small');
            errorEl.className = 'form__error text-danger mt-1';
            errorEl.textContent = message;
            input.parentNode.insertBefore(errorEl, input.nextSibling);
        }
        input.classList.add('is-invalid');
    }

    /**
     * 입력 필드 에러 제거
     * @param {HTMLElement} input
     */
    function clearError(input) {
        const formGroup = input.closest('.form__group');
        const existingError = formGroup.querySelector('.form__error');
        if (existingError) {
            existingError.remove();
        }
        input.classList.remove('is-invalid');
    }

    // 비밀번호 자동 생성 버튼
    if (generatePasswordBtn) {
        generatePasswordBtn.addEventListener('click', function() {
            const password = generatePassword(12);
            passwordInput.value = password;
            passwordInput.type = 'text'; // 생성된 비밀번호 표시

            // 복사 안내 토스트 (toast 함수가 있는 경우)
            if (typeof showToast === 'function') {
                showToast('비밀번호가 생성되었습니다. 직원에게 전달해주세요.', 'success');
            }
        });
    }

    // 실시간 유효성 검사
    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            const result = validateUsername(this.value);
            if (!result.valid) {
                showError(this, result.message);
            } else {
                clearError(this);
            }
        });
    }

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const result = validateEmail(this.value);
            if (!result.valid) {
                showError(this, result.message);
            } else {
                clearError(this);
            }
        });
    }

    // 폼 제출 처리
    if (form) {
        form.addEventListener('submit', function(e) {
            let isValid = true;

            // 사용자명 검사
            const usernameResult = validateUsername(usernameInput.value);
            if (!usernameResult.valid) {
                showError(usernameInput, usernameResult.message);
                isValid = false;
            } else {
                clearError(usernameInput);
            }

            // 이메일 검사
            const emailResult = validateEmail(emailInput.value);
            if (!emailResult.valid) {
                showError(emailInput, emailResult.message);
                isValid = false;
            } else {
                clearError(emailInput);
            }

            if (!isValid) {
                e.preventDefault();
                return false;
            }

            // 중복 제출 방지
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>처리 중...</span>';
            }
        });
    }
})();
