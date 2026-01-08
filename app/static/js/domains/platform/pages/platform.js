/**
 * platform.js - 플랫폼 관리 페이지 공통 스크립트
 *
 * Phase 31.1: 인라인 스크립트 통합 - CLAUDE.md 규칙 준수
 *
 * 포함 기능:
 * - toggleCompanyActive: 법인 활성화/비활성화 토글
 * - toggleUserActive: 사용자 활성화/비활성화 토글
 * - grantSuperadmin: 슈퍼관리자 권한 부여
 * - revokeSuperadmin: 슈퍼관리자 권한 해제
 * - updateSetting: 시스템 설정 업데이트
 * - initPlatformActions: 플랫폼 액션 버튼 초기화 (이벤트 위임)
 */

import { showToast } from '../../../shared/components/toast.js';

/**
 * 법인 활성화/비활성화 토글
 * @param {number} companyId - 법인 ID
 */
export async function toggleCompanyActive(companyId) {
    if (!confirm('법인 상태를 변경하시겠습니까?')) return;

    try {
        const response = await fetch(`/platform/api/companies/${companyId}/toggle-active`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('법인 상태가 변경되었습니다.', 'success');
            location.reload();
        } else {
            showToast(data.error || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('오류가 발생했습니다.', 'error');
    }
}

/**
 * 사용자 활성화/비활성화 토글
 * @param {number} userId - 사용자 ID
 */
export async function toggleUserActive(userId) {
    if (!confirm('사용자 상태를 변경하시겠습니까?')) return;

    try {
        const response = await fetch(`/platform/api/users/${userId}/toggle-active`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast('사용자 상태가 변경되었습니다.', 'success');
            location.reload();
        } else {
            showToast(data.error || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('오류가 발생했습니다.', 'error');
    }
}

/**
 * 슈퍼관리자 권한 부여
 * @param {number} userId - 사용자 ID
 */
export async function grantSuperadmin(userId) {
    if (!confirm('이 사용자에게 슈퍼관리자 권한을 부여하시겠습니까?')) return;

    try {
        const response = await fetch(`/platform/api/users/${userId}/grant-superadmin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            location.reload();
        } else {
            showToast(data.error || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('오류가 발생했습니다.', 'error');
    }
}

/**
 * 슈퍼관리자 권한 해제
 * @param {number} userId - 사용자 ID
 */
export async function revokeSuperadmin(userId) {
    if (!confirm('이 사용자의 슈퍼관리자 권한을 해제하시겠습니까?')) return;

    try {
        const response = await fetch(`/platform/api/users/${userId}/revoke-superadmin`, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
            location.reload();
        } else {
            showToast(data.error || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('오류가 발생했습니다.', 'error');
    }
}

/**
 * 시스템 설정 업데이트
 * @param {string} key - 설정 키
 */
export async function updateSetting(key) {
    const input = document.getElementById(`setting-${key}`);
    if (!input) return;

    const value = input.value;

    try {
        const response = await fetch(`/platform/api/settings/${key}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({ value: value })
        });

        const data = await response.json();

        if (data.success) {
            showToast(data.message, 'success');
        } else {
            showToast(data.error || '오류가 발생했습니다.', 'error');
        }
    } catch (error) {
        console.error('Error:', error);
        showToast('오류가 발생했습니다.', 'error');
    }
}

/**
 * 플랫폼 액션 버튼 초기화 (이벤트 위임)
 * @param {string} containerSelector - 컨테이너 셀렉터
 */
export function initPlatformActions(containerSelector = '.platform-page') {
    const container = document.querySelector(containerSelector);
    if (!container) return;

    container.addEventListener('click', async (e) => {
        const btn = e.target.closest('[data-action]');
        if (!btn) return;

        const action = btn.dataset.action;
        const companyId = btn.dataset.companyId;
        const userId = btn.dataset.userId;
        const settingKey = btn.dataset.settingKey;

        switch (action) {
            case 'toggle-company-active':
                if (companyId) await toggleCompanyActive(companyId);
                break;
            case 'toggle-user-active':
                if (userId) await toggleUserActive(userId);
                break;
            case 'grant-superadmin':
                if (userId) await grantSuperadmin(userId);
                break;
            case 'revoke-superadmin':
                if (userId) await revokeSuperadmin(userId);
                break;
            case 'update-setting':
                if (settingKey) await updateSetting(settingKey);
                break;
        }
    });
}

// 전역 함수로 노출 (비모듈 환경 호환)
if (typeof window !== 'undefined') {
    window.HRPlatform = {
        toggleCompanyActive,
        toggleUserActive,
        grantSuperadmin,
        revokeSuperadmin,
        updateSetting,
        initPlatformActions
    };

    // 기존 전역 함수 호환성 유지
    window.toggleCompanyActive = toggleCompanyActive;
    window.toggleUserActive = toggleUserActive;
    window.grantSuperadmin = grantSuperadmin;
    window.revokeSuperadmin = revokeSuperadmin;
    window.updateSetting = updateSetting;
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', () => {
    initPlatformActions();
});
