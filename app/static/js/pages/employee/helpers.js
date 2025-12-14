/**
 * Employee Form Helpers
 * Phase 7: 프론트엔드 리팩토링 - employee-form.js 분할
 *
 * 공통 헬퍼 함수 모음
 */

/**
 * 폼에서 직원 ID 추출
 * 프로필 수정 페이지(profileEditForm)와 직원 수정 페이지(employeeForm) 모두 지원
 * @returns {number|null} 직원 ID 또는 null
 */
export function getEmployeeIdFromForm() {
    // 여러 폼 ID 지원 (직원 수정, 프로필 수정)
    const form = document.getElementById('employeeForm')
              || document.getElementById('profileEditForm');
    if (!form) return null;

    // data-employee-id 속성 우선 사용 (프로필 수정 페이지)
    const dataId = form.dataset.employeeId;
    if (dataId) return parseInt(dataId, 10);

    // URL 패턴에서 ID 추출 (직원 수정 페이지 폴백)
    const actionUrl = form.getAttribute('action');
    const match = actionUrl.match(/\/employees\/(\d+)\/update/);
    return match ? parseInt(match[1], 10) : null;
}

/**
 * Toast 메시지 표시
 * @param {string} message - 메시지 내용
 * @param {string} type - 메시지 타입 (info, success, error, warning)
 */
export function showToast(message, type = 'info') {
    // Toast 컴포넌트가 있으면 사용
    if (typeof Toast !== 'undefined' && Toast.show) {
        Toast.show(message, type);
        return;
    }

    // 기본 alert 대체
    if (type === 'error') {
        alert('오류: ' + message);
    } else {
        alert(message);
    }
}

/**
 * 허용된 이미지 타입 목록
 */
export const ALLOWED_IMAGE_TYPES = ['image/jpeg', 'image/png', 'image/gif', 'image/webp'];

/**
 * 최대 파일 크기 (5MB)
 */
export const MAX_FILE_SIZE = 5 * 1024 * 1024;

/**
 * 이미지 파일 유효성 검사
 * @param {File} file - 검사할 파일
 * @returns {{valid: boolean, error?: string}} 검사 결과
 */
export function validateImageFile(file) {
    if (!ALLOWED_IMAGE_TYPES.includes(file.type)) {
        return {
            valid: false,
            error: '이미지 파일만 업로드 가능합니다. (JPG, PNG, GIF, WebP)'
        };
    }

    if (file.size > MAX_FILE_SIZE) {
        return {
            valid: false,
            error: '파일 크기가 5MB를 초과합니다.'
        };
    }

    return { valid: true };
}

export default {
    getEmployeeIdFromForm,
    showToast,
    validateImageFile,
    ALLOWED_IMAGE_TYPES,
    MAX_FILE_SIZE
};
