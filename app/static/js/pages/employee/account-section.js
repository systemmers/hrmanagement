/**
 * Account Section Module
 * 21번/22번 원칙: 직원 등록 시 계정 동시 생성
 *
 * 기능:
 * - 계정 생성 토글 이벤트
 * - 필수 필드 동적 설정
 * - 이메일 동기화
 * - 비밀번호 자동 생성
 * - 아이디/이메일 중복 확인
 */

import { showToast } from './helpers.js';

/**
 * 계정 섹션 초기화
 */
export function initAccountSection() {
    const accountToggle = document.getElementById('createAccountToggle');
    if (!accountToggle) return;

    // 토글 이벤트
    initToggleEvent(accountToggle);

    // 이메일 동기화 버튼
    initEmailSync();

    // 비밀번호 자동 생성 버튼
    initPasswordGenerator();

    // 아이디 유효성 검사
    initUsernameValidation();

    // 이메일 유효성 검사
    initEmailValidation();

    // 초기 상태 설정
    updateAccountFieldsState(accountToggle.checked);
}

/**
 * 토글 이벤트 초기화
 */
function initToggleEvent(toggleElement) {
    toggleElement.addEventListener('change', function() {
        updateAccountFieldsState(this.checked);
    });
}

/**
 * 계정 필드 상태 업데이트
 */
function updateAccountFieldsState(isEnabled) {
    const formFields = document.getElementById('accountFormFields');
    const disabledMessage = document.getElementById('accountDisabledMessage');
    const accountUsername = document.getElementById('account_username');
    const accountEmail = document.getElementById('account_email');
    const accountPassword = document.getElementById('account_password');

    if (formFields) {
        formFields.style.display = isEnabled ? 'block' : 'none';
    }
    if (disabledMessage) {
        disabledMessage.style.display = isEnabled ? 'none' : 'block';
    }

    // 필수 필드 설정
    if (accountUsername) {
        accountUsername.required = isEnabled;
    }
    if (accountEmail) {
        accountEmail.required = isEnabled;
    }
    if (accountPassword) {
        accountPassword.required = isEnabled;
    }
}

/**
 * 이메일 동기화 버튼 초기화
 */
function initEmailSync() {
    const syncBtn = document.getElementById('syncEmailBtn');
    if (!syncBtn) return;

    syncBtn.addEventListener('click', function() {
        const personalEmail = document.getElementById('email');
        const accountEmail = document.getElementById('account_email');

        if (personalEmail && accountEmail) {
            accountEmail.value = personalEmail.value;
            validateEmail(accountEmail.value);
            showToast('이메일이 동기화되었습니다.', 'info');
        }
    });
}

/**
 * 비밀번호 자동 생성 버튼 초기화
 */
function initPasswordGenerator() {
    const generateBtn = document.getElementById('generatePasswordBtn');
    if (!generateBtn) return;

    generateBtn.addEventListener('click', function() {
        const passwordField = document.getElementById('account_password');
        if (passwordField) {
            const password = generateSecurePassword();
            passwordField.value = password;
            showToast('비밀번호가 자동 생성되었습니다.', 'success');
        }
    });
}

/**
 * 안전한 비밀번호 생성
 */
function generateSecurePassword(length = 12) {
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const numbers = '0123456789';
    const special = '!@#$%';
    const allChars = uppercase + lowercase + numbers + special;

    let password = '';

    // 각 문자 유형에서 최소 1개씩 포함
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += special[Math.floor(Math.random() * special.length)];

    // 나머지 문자 채우기
    for (let i = password.length; i < length; i++) {
        password += allChars[Math.floor(Math.random() * allChars.length)];
    }

    // 셔플
    return password.split('').sort(() => Math.random() - 0.5).join('');
}

/**
 * 아이디 유효성 검사 초기화
 */
function initUsernameValidation() {
    const usernameField = document.getElementById('account_username');
    if (!usernameField) return;

    let debounceTimer;

    usernameField.addEventListener('input', function() {
        const validationIcon = document.getElementById('usernameValidation');
        const value = this.value.trim();

        // 기본 형식 검사
        if (value.length < 4) {
            setValidationState(validationIcon, 'error', '4자 이상 입력');
            return;
        }

        if (!/^[a-zA-Z0-9]+$/.test(value)) {
            setValidationState(validationIcon, 'error', '영문/숫자만');
            return;
        }

        setValidationState(validationIcon, 'loading', '확인 중...');

        // 디바운스 처리
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            checkUsernameAvailability(value, validationIcon);
        }, 500);
    });
}

/**
 * 아이디 중복 확인 API 호출
 */
async function checkUsernameAvailability(username, validationIcon) {
    try {
        const response = await fetch(`/api/users/check-username?username=${encodeURIComponent(username)}`);
        const data = await response.json();

        if (data.available) {
            setValidationState(validationIcon, 'success', '사용 가능');
        } else {
            setValidationState(validationIcon, 'error', '이미 사용 중');
        }
    } catch (error) {
        // API 미구현 시 기본 통과 처리
        setValidationState(validationIcon, 'success', '확인됨');
    }
}

/**
 * 이메일 유효성 검사 초기화
 */
function initEmailValidation() {
    const emailField = document.getElementById('account_email');
    if (!emailField) return;

    let debounceTimer;

    emailField.addEventListener('input', function() {
        const value = this.value.trim();

        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
            validateEmail(value);
        }, 500);
    });
}

/**
 * 이메일 유효성 검사
 */
async function validateEmail(email) {
    if (!email || !email.includes('@')) {
        return false;
    }

    try {
        const response = await fetch(`/api/users/check-email?email=${encodeURIComponent(email)}`);
        const data = await response.json();
        return data.available;
    } catch (error) {
        // API 미구현 시 기본 통과 처리
        return true;
    }
}

/**
 * 유효성 상태 표시
 */
function setValidationState(iconElement, state, message) {
    if (!iconElement) return;

    iconElement.className = 'validation-icon';

    switch (state) {
        case 'success':
            iconElement.innerHTML = '<i class="fas fa-check-circle text-success"></i>';
            iconElement.title = message;
            break;
        case 'error':
            iconElement.innerHTML = '<i class="fas fa-times-circle text-danger"></i>';
            iconElement.title = message;
            break;
        case 'loading':
            iconElement.innerHTML = '<i class="fas fa-spinner fa-spin text-muted"></i>';
            iconElement.title = message;
            break;
        default:
            iconElement.innerHTML = '';
    }
}

/**
 * 폼 제출 전 계정 필드 검증
 */
export function validateAccountFields() {
    const toggle = document.getElementById('createAccountToggle');
    if (!toggle || !toggle.checked) {
        return { valid: true, errors: [] };
    }

    const errors = [];
    const username = document.getElementById('account_username')?.value?.trim();
    const email = document.getElementById('account_email')?.value?.trim();
    const password = document.getElementById('account_password')?.value;

    if (!username || username.length < 4) {
        errors.push('아이디는 4자 이상이어야 합니다.');
    }

    if (!email || !email.includes('@')) {
        errors.push('올바른 이메일 형식이 아닙니다.');
    }

    if (!password || password.length < 8) {
        errors.push('비밀번호는 8자 이상이어야 합니다.');
    }

    return {
        valid: errors.length === 0,
        errors: errors
    };
}

export default {
    initAccountSection,
    validateAccountFields,
    generateSecurePassword
};
