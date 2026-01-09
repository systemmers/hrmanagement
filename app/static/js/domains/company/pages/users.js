/**
 * Corporate Users Management
 * 법인 사용자 관리 페이지 JavaScript
 *
 * Used by:
 * - corporate/users.html
 */

import { post } from '../../../shared/utils/api.js';
import { showToast } from '../../../shared/components/toast.js';

document.addEventListener('DOMContentLoaded', function() {
    initCorporateUsersEventDelegation();
    initDropdowns();
});

/**
 * Initialize event delegation for corporate users page
 */
function initCorporateUsersEventDelegation() {
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        const userId = target.dataset.userId;

        switch (action) {
            case 'edit-user':
                editUser(userId);
                break;
            case 'toggle-user-status':
                toggleUserStatus(userId);
                break;
            case 'change-status':
                e.preventDefault();
                const status = target.dataset.status;
                changeUserStatus(userId, status);
                break;
        }
    });
}

/**
 * Initialize dropdown menus
 */
function initDropdowns() {
    document.addEventListener('click', function(e) {
        const toggle = e.target.closest('[data-toggle="dropdown"]');

        if (toggle) {
            e.preventDefault();
            e.stopPropagation();

            // Close other dropdowns
            document.querySelectorAll('.dropdown.show').forEach(d => {
                if (d !== toggle.closest('.dropdown')) {
                    d.classList.remove('show');
                }
            });

            // Toggle current dropdown
            const dropdown = toggle.closest('.dropdown');
            dropdown.classList.toggle('show');
            return;
        }

        // Close all dropdowns when clicking outside
        if (!e.target.closest('.dropdown-menu')) {
            document.querySelectorAll('.dropdown.show').forEach(d => {
                d.classList.remove('show');
            });
        }
    });
}

/**
 * Edit user - open edit modal
 * @param {string} userId - User ID
 */
function editUser(userId) {
    // Open user edit modal (defined in user-edit-modal.js)
    if (typeof window.openUserEditModal === 'function') {
        window.openUserEditModal(userId);
    } else {
        showToast('사용자 수정 모달을 로드할 수 없습니다.', 'error');
    }
}

/**
 * Toggle user status (active/inactive) - legacy function
 * @param {string} userId - User ID
 */
function toggleUserStatus(userId) {
    if (confirm('사용자 상태를 변경하시겠습니까?')) {
        // TODO: Implement API call
        showToast('상태 변경 기능은 추후 구현 예정입니다.', 'info');
    }
}

/**
 * Change user status (active/dormant/withdrawn)
 * @param {string} userId - User ID
 * @param {string} status - New status ('active', 'dormant', 'withdrawn')
 */
async function changeUserStatus(userId, status) {
    const statusLabels = {
        'active': '활성화',
        'dormant': '휴면 처리',
        'withdrawn': '계정 탈퇴'
    };

    const statusLabel = statusLabels[status] || status;

    // 탈퇴의 경우 추가 확인
    if (status === 'withdrawn') {
        if (!confirm(`정말로 이 계정을 탈퇴 처리하시겠습니까?\n이 작업은 되돌리기 어려울 수 있습니다.`)) {
            return;
        }
    } else {
        if (!confirm(`이 계정을 ${statusLabel}하시겠습니까?`)) {
            return;
        }
    }

    try {
        const result = await post(`/corporate/api/users/${userId}/status`, { status });

        if (result.success) {
            showToast(result.message || `계정이 ${statusLabel}되었습니다.`, 'success');
            location.reload();
        } else {
            showToast(result.message || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('계정 상태 변경 오류:', error);
        showToast(error.message || '요청 처리 중 오류가 발생했습니다.', 'error');
    }
}

// Expose functions for non-module environments
window.editUser = editUser;
window.toggleUserStatus = toggleUserStatus;
window.changeUserStatus = changeUserStatus;
