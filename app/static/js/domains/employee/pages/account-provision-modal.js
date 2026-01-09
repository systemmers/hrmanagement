/**
 * Account Provision Modal JavaScript
 * 계정 발급 모달 스크립트
 *
 * 2-Step Modal:
 * - Step 1: 계정 정보 입력
 * - Step 2: 확인 및 제출
 */

import { post } from '../../../shared/utils/api.js';
import { showToast } from '../../../shared/components/toast.js';

// State
let currentStep = 1;

// DOM Elements
let modal, form;

document.addEventListener('DOMContentLoaded', function() {
    initAccountProvisionModal();
});

/**
 * Initialize account provision modal
 */
function initAccountProvisionModal() {
    modal = document.getElementById('accountProvisionModal');
    form = document.getElementById('accountProvisionForm');

    if (!modal || !form) return;

    // Open modal buttons (multiple triggers possible)
    const openBtn = document.getElementById('openAccountProvisionModal');
    if (openBtn) {
        openBtn.addEventListener('click', openModal);
    }

    // Alternative open button (e.g., empty state button)
    const openBtnEmpty = document.getElementById('openAccountProvisionModalEmpty');
    if (openBtnEmpty) {
        openBtnEmpty.addEventListener('click', openModal);
    }

    // Close modal buttons
    modal.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    // Backdrop click
    const backdrop = modal.querySelector('.modal__backdrop');
    if (backdrop) {
        backdrop.addEventListener('click', closeModal);
    }

    // Step navigation
    initStepNavigation();

    // Password generation
    initPasswordGeneration();

    // Real-time validation
    initValidation();

    // Form submission
    form.addEventListener('submit', handleFormSubmit);
}

/**
 * Open modal
 */
function openModal() {
    modal.classList.add('show');
    modal.setAttribute('aria-hidden', 'false');
    document.body.style.overflow = 'hidden';

    // Reset state
    currentStep = 1;
    form.reset();
    updateStepUI();
    clearAllErrors();
}

/**
 * Close modal
 */
function closeModal() {
    modal.classList.remove('show');
    modal.setAttribute('aria-hidden', 'true');
    document.body.style.overflow = '';
}

/**
 * Initialize step navigation
 */
function initStepNavigation() {
    // Next buttons
    modal.querySelectorAll('[data-step-next]').forEach(btn => {
        btn.addEventListener('click', function() {
            const nextStep = parseInt(this.dataset.stepNext);
            goToStep(nextStep);
        });
    });

    // Previous buttons
    modal.querySelectorAll('[data-step-prev]').forEach(btn => {
        btn.addEventListener('click', function() {
            const prevStep = parseInt(this.dataset.stepPrev);
            goToStep(prevStep);
        });
    });
}

/**
 * Go to specific step
 */
function goToStep(step) {
    // Validate before moving forward
    if (step > currentStep) {
        if (!validateCurrentStep()) return;
    }

    currentStep = step;
    updateStepUI();

    // Update confirm section for step 2
    if (step === 2) {
        updateConfirmSection();
    }
}

/**
 * Validate current step
 */
function validateCurrentStep() {
    if (currentStep === 1) {
        const name = document.getElementById('modalName').value.trim();
        const username = document.getElementById('modalUsername').value.trim();
        const email = document.getElementById('modalEmail').value.trim();

        let isValid = true;

        // Name validation
        if (!name) {
            showFieldError('modalName', '이름을 입력해주세요.');
            isValid = false;
        } else {
            clearFieldError('modalName');
        }

        // Username validation
        const usernameResult = validateUsername(username);
        if (!usernameResult.valid) {
            showFieldError('modalUsername', usernameResult.message);
            isValid = false;
        } else {
            clearFieldError('modalUsername');
        }

        // Email validation
        const emailResult = validateEmail(email);
        if (!emailResult.valid) {
            showFieldError('modalEmail', emailResult.message);
            isValid = false;
        } else {
            clearFieldError('modalEmail');
        }

        return isValid;
    }

    return true;
}

/**
 * Update step UI
 */
function updateStepUI() {
    // Update step indicators
    modal.querySelectorAll('.step').forEach(step => {
        const stepNum = parseInt(step.dataset.step);
        step.classList.remove('active', 'completed');

        if (stepNum === currentStep) {
            step.classList.add('active');
        } else if (stepNum < currentStep) {
            step.classList.add('completed');
        }
    });

    // Update step content
    modal.querySelectorAll('.modal-step-content').forEach(content => {
        const contentStep = parseInt(content.dataset.stepContent);
        content.classList.toggle('active', contentStep === currentStep);
    });
}

/**
 * Update confirm section in step 2
 */
function updateConfirmSection() {
    const name = document.getElementById('modalName').value;
    const organizationSelect = document.getElementById('modalOrganizationId');
    const username = document.getElementById('modalUsername').value;
    const email = document.getElementById('modalEmail').value;
    const password = document.getElementById('modalPassword').value;
    const roleSelect = document.getElementById('modalRole');

    const organizationText = organizationSelect.selectedIndex > 0
        ? organizationSelect.options[organizationSelect.selectedIndex].text
        : '미지정';
    const roleText = roleSelect.options[roleSelect.selectedIndex].text;
    const passwordText = password || '(자동 생성)';

    document.getElementById('confirmName').textContent = name || '-';
    document.getElementById('confirmOrganization').textContent = organizationText;
    document.getElementById('confirmUsername').textContent = username || '-';
    document.getElementById('confirmEmail').textContent = email || '-';
    document.getElementById('confirmPassword').textContent = passwordText;
    document.getElementById('confirmRole').textContent = roleText;
}

/**
 * Initialize password generation
 */
function initPasswordGeneration() {
    const generateBtn = document.getElementById('generatePasswordBtn');
    const passwordInput = document.getElementById('modalPassword');

    if (generateBtn && passwordInput) {
        generateBtn.addEventListener('click', function() {
            const password = generatePassword(12);
            passwordInput.value = password;
            showToast('비밀번호가 생성되었습니다.', 'success');
        });
    }
}

/**
 * Generate secure random password
 */
function generatePassword(length = 12) {
    const lowercase = 'abcdefghijklmnopqrstuvwxyz';
    const uppercase = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ';
    const numbers = '0123456789';
    const special = '!@#$%';
    const allChars = lowercase + uppercase + numbers + special;

    let password = '';

    // Include at least one of each type
    password += lowercase[Math.floor(Math.random() * lowercase.length)];
    password += uppercase[Math.floor(Math.random() * uppercase.length)];
    password += numbers[Math.floor(Math.random() * numbers.length)];
    password += special[Math.floor(Math.random() * special.length)];

    // Fill remaining length
    for (let i = password.length; i < length; i++) {
        password += allChars[Math.floor(Math.random() * allChars.length)];
    }

    // Shuffle
    return password.split('').sort(() => Math.random() - 0.5).join('');
}

/**
 * Initialize real-time validation
 */
function initValidation() {
    const usernameInput = document.getElementById('modalUsername');
    const emailInput = document.getElementById('modalEmail');

    if (usernameInput) {
        usernameInput.addEventListener('blur', function() {
            const result = validateUsername(this.value.trim());
            if (!result.valid) {
                showFieldError('modalUsername', result.message);
            } else {
                clearFieldError('modalUsername');
            }
        });
    }

    if (emailInput) {
        emailInput.addEventListener('blur', function() {
            const result = validateEmail(this.value.trim());
            if (!result.valid) {
                showFieldError('modalEmail', result.message);
            } else {
                clearFieldError('modalEmail');
            }
        });
    }
}

/**
 * Validate username
 */
function validateUsername(username) {
    if (!username || username.length < 4) {
        return { valid: false, message: '사용자명은 4자 이상이어야 합니다.' };
    }
    if (!/^[a-zA-Z0-9_]+$/.test(username)) {
        return { valid: false, message: '영문, 숫자, 밑줄(_)만 사용할 수 있습니다.' };
    }
    return { valid: true, message: '' };
}

/**
 * Validate email
 */
function validateEmail(email) {
    if (!email || !email.includes('@')) {
        return { valid: false, message: '올바른 이메일 형식이 아닙니다.' };
    }
    return { valid: true, message: '' };
}

/**
 * Show field error
 */
function showFieldError(fieldId, message) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    const formGroup = input.closest('.form__group');
    let errorEl = formGroup.querySelector('.form__error');

    if (!errorEl) {
        errorEl = document.createElement('small');
        errorEl.className = 'form__error text-danger';
        formGroup.appendChild(errorEl);
    }

    errorEl.textContent = message;
    input.classList.add('is-invalid');
}

/**
 * Clear field error
 */
function clearFieldError(fieldId) {
    const input = document.getElementById(fieldId);
    if (!input) return;

    const formGroup = input.closest('.form__group');
    const errorEl = formGroup.querySelector('.form__error');

    if (errorEl) {
        errorEl.remove();
    }
    input.classList.remove('is-invalid');
}

/**
 * Clear all errors
 */
function clearAllErrors() {
    modal.querySelectorAll('.form-error').forEach(el => el.remove());
    modal.querySelectorAll('.is-invalid').forEach(el => el.classList.remove('is-invalid'));
}

/**
 * Handle form submission
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    if (!validateCurrentStep()) return;

    const submitBtn = document.getElementById('submitProvisionBtn');
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 처리 중...';

    const formData = {
        name: document.getElementById('modalName').value.trim(),
        username: document.getElementById('modalUsername').value.trim(),
        email: document.getElementById('modalEmail').value.trim(),
        password: document.getElementById('modalPassword').value.trim() || null,
        organization_id: document.getElementById('modalOrganizationId').value || null,
        role: document.getElementById('modalRole').value
    };

    try {
        const result = await post('/employees/api/provision', formData);

        if (result.success) {
            showToast(result.message || '계정이 발급되었습니다.', 'success');
            closeModal();
            location.reload();
        } else {
            showToast(result.message || '계정 발급에 실패했습니다.', 'error');
        }
    } catch (error) {
        console.error('Account provision error:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = '<i class="fas fa-id-card"></i> 계정 발급';
    }
}

// Export for testing
export { openModal, closeModal };
