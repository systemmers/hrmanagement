/**
 * User Edit Modal JavaScript
 * 사용자 수정 모달 스크립트
 *
 * Used by:
 * - corporate/users.html
 */

import { get, put } from '../../../shared/utils/api.js';
import { showToast } from '../../../shared/components/toast.js';

// DOM Elements
let modal, form;

// Status labels
const STATUS_LABELS = {
    'active': '활성',
    'dormant': '휴면',
    'withdrawn': '탈퇴'
};

const CONTRACT_STATUS_LABELS = {
    'none': '계약없음',
    'requested': '대기중',
    'approved': '승인됨',
    'rejected': '거절됨',
    'terminated': '종료',
    'termination_requested': '종료대기'
};

const ROLE_LABELS = {
    'admin': '관리자',
    'manager': '매니저',
    'employee': '일반 직원'
};

document.addEventListener('DOMContentLoaded', function() {
    initUserEditModal();
});

/**
 * Initialize user edit modal
 */
function initUserEditModal() {
    modal = document.getElementById('userEditModal');
    form = document.getElementById('userEditForm');

    if (!modal || !form) return;

    // Close modal buttons
    modal.querySelectorAll('[data-modal-close]').forEach(btn => {
        btn.addEventListener('click', closeModal);
    });

    // Backdrop click
    const backdrop = modal.querySelector('.modal__backdrop');
    if (backdrop) {
        backdrop.addEventListener('click', closeModal);
    }

    // Password reset toggle
    initPasswordResetToggle();

    // Password generation
    initPasswordGeneration();

    // Form submission
    form.addEventListener('submit', handleFormSubmit);
}

/**
 * Open modal with user data
 * @param {number} userId - User ID to edit
 */
export async function openUserEditModal(userId) {
    if (!modal || !form) {
        console.error('User edit modal not initialized');
        return;
    }

    try {
        // Fetch user data
        const response = await get(`/corporate/api/users/${userId}`);

        if (!response.success) {
            showToast(response.message || '사용자 정보를 불러올 수 없습니다.', 'error');
            return;
        }

        const user = response.data;

        // Populate form
        document.getElementById('editUserId').value = user.id;
        document.getElementById('editUsername').value = user.username || '-';
        document.getElementById('editName').value = user.name || '-';
        document.getElementById('editStatus').value = STATUS_LABELS[user.is_active ? 'active' : 'dormant'] || '-';
        document.getElementById('editContractStatus').value = CONTRACT_STATUS_LABELS[user.contract_status] || '-';
        document.getElementById('editEmail').value = user.email || '';
        document.getElementById('editRole').value = user.role || 'employee';

        // Update role help text based on contract status
        updateRoleHelpText(user.contract_status);

        // Reset password fields
        document.getElementById('resetPassword').checked = false;
        document.getElementById('editNewPassword').value = '';
        document.getElementById('newPasswordGroup').style.display = 'none';

        // Show modal
        modal.classList.add('show');
        modal.setAttribute('aria-hidden', 'false');
        document.body.style.overflow = 'hidden';

    } catch (error) {
        console.error('Failed to fetch user data:', error);
        showToast('사용자 정보를 불러오는 중 오류가 발생했습니다.', 'error');
    }
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
 * Update role help text based on contract status
 * @param {string} contractStatus - Current contract status
 */
function updateRoleHelpText(contractStatus) {
    const helpText = document.getElementById('roleHelpText');
    if (!helpText) return;

    if (contractStatus !== 'approved') {
        helpText.textContent = '계약이 승인되지 않으면 역할이 "대기"로 표시됩니다.';
        helpText.classList.add('text-warning');
    } else {
        helpText.textContent = '';
        helpText.classList.remove('text-warning');
    }
}

/**
 * Initialize password reset toggle
 */
function initPasswordResetToggle() {
    const checkbox = document.getElementById('resetPassword');
    const passwordGroup = document.getElementById('newPasswordGroup');

    if (!checkbox || !passwordGroup) return;

    checkbox.addEventListener('change', function() {
        passwordGroup.style.display = this.checked ? 'block' : 'none';
    });
}

/**
 * Initialize password generation
 */
function initPasswordGeneration() {
    const btn = document.getElementById('generateEditPasswordBtn');
    const input = document.getElementById('editNewPassword');

    if (!btn || !input) return;

    btn.addEventListener('click', function() {
        input.value = generateSecurePassword(12);
    });
}

/**
 * Generate secure password
 * @param {number} length - Password length
 * @returns {string} Generated password
 */
function generateSecurePassword(length = 12) {
    const charset = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789';
    let password = '';
    const randomValues = new Uint32Array(length);
    crypto.getRandomValues(randomValues);
    for (let i = 0; i < length; i++) {
        password += charset[randomValues[i] % charset.length];
    }
    return password;
}

/**
 * Handle form submission
 * @param {Event} e - Submit event
 */
async function handleFormSubmit(e) {
    e.preventDefault();

    const userId = document.getElementById('editUserId').value;
    const email = document.getElementById('editEmail').value.trim();
    const role = document.getElementById('editRole').value;
    const resetPassword = document.getElementById('resetPassword').checked;
    const newPassword = document.getElementById('editNewPassword').value.trim();

    // Validation
    if (!email) {
        showToast('이메일을 입력해주세요.', 'error');
        return;
    }

    // Prepare data
    const data = {
        email: email,
        role: role
    };

    if (resetPassword) {
        data.reset_password = true;
        if (newPassword) {
            data.new_password = newPassword;
        }
    }

    // Submit
    const submitBtn = document.getElementById('submitEditBtn');
    const originalText = submitBtn.innerHTML;
    submitBtn.disabled = true;
    submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> 저장 중...';

    try {
        const response = await put(`/corporate/api/users/${userId}`, data);

        if (response.success) {
            let message = response.data?.message || '사용자 정보가 수정되었습니다.';

            // Show new password if generated
            if (response.data?.new_password) {
                message += `\n새 비밀번호: ${response.data.new_password}`;
                alert(`사용자 정보가 수정되었습니다.\n\n새 비밀번호: ${response.data.new_password}\n\n이 비밀번호를 안전하게 사용자에게 전달해주세요.`);
            }

            showToast(message, 'success');
            closeModal();
            location.reload();
        } else {
            showToast(response.message || '수정 중 오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('User update error:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
    } finally {
        submitBtn.disabled = false;
        submitBtn.innerHTML = originalText;
    }
}

// Expose for non-module environments and event handlers
window.openUserEditModal = openUserEditModal;
