/**
 * BusinessCard API Service
 * 명함 API 통신 서비스
 *
 * Usage:
 *   import { businesscardApi } from './services/businesscard-api.js';
 *
 *   // 명함 조회
 *   const result = await businesscardApi.getBusinessCards(employeeId);
 *
 *   // 명함 업로드
 *   const result = await businesscardApi.uploadBusinessCard(employeeId, file, 'front');
 *
 *   // 명함 삭제
 *   const result = await businesscardApi.deleteBusinessCard(employeeId, 'front');
 */

const API_BASE = '/api/businesscard';

/**
 * CSRF 토큰 가져오기
 * @returns {string|null}
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.content : null;
}

/**
 * API 요청 헬퍼
 * @param {string} url - 요청 URL
 * @param {Object} options - fetch 옵션
 * @returns {Promise<Object>}
 */
async function apiRequest(url, options = {}) {
    const headers = {
        ...options.headers
    };

    // CSRF 토큰 추가 (GET 제외)
    if (options.method && options.method !== 'GET') {
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            headers['X-CSRFToken'] = csrfToken;
        }
    }

    // JSON 요청일 경우
    if (options.body && !(options.body instanceof FormData)) {
        headers['Content-Type'] = 'application/json';
        options.body = JSON.stringify(options.body);
    }

    const response = await fetch(url, {
        ...options,
        headers
    });

    const data = await response.json();

    if (!response.ok) {
        throw new Error(data.error || `HTTP ${response.status}`);
    }

    return data;
}

export const businesscardApi = {
    /**
     * 직원의 명함 이미지 조회 (앞면/뒷면 모두)
     * @param {number} employeeId - 직원 ID
     * @returns {Promise<{success: boolean, data: {front: Object|null, back: Object|null}}>}
     */
    async getBusinessCards(employeeId) {
        return apiRequest(`${API_BASE}/employee/${employeeId}`);
    },

    /**
     * 직원의 특정 면 명함 이미지 조회
     * @param {number} employeeId - 직원 ID
     * @param {string} side - 'front' 또는 'back'
     * @returns {Promise<{success: boolean, data: Object}>}
     */
    async getBusinessCard(employeeId, side) {
        return apiRequest(`${API_BASE}/employee/${employeeId}/${side}`);
    },

    /**
     * 명함 이미지 업로드
     * @param {number} employeeId - 직원 ID
     * @param {File} file - 업로드할 파일
     * @param {string} side - 'front' 또는 'back'
     * @returns {Promise<{success: boolean, data: {side: string, file_path: string, attachment: Object}}>}
     */
    async uploadBusinessCard(employeeId, file, side) {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('side', side);

        return apiRequest(`${API_BASE}/employee/${employeeId}`, {
            method: 'POST',
            body: formData
        });
    },

    /**
     * 명함 이미지 삭제
     * @param {number} employeeId - 직원 ID
     * @param {string} side - 'front' 또는 'back'
     * @returns {Promise<{success: boolean, message: string}>}
     */
    async deleteBusinessCard(employeeId, side) {
        return apiRequest(`${API_BASE}/employee/${employeeId}/${side}`, {
            method: 'DELETE'
        });
    }
};

// 레거시 API 경로 지원 (deprecated)
export const legacyBusinesscardApi = {
    /**
     * @deprecated 신규 API 경로 사용 권장: /api/businesscard/employee/{id}
     */
    async uploadBusinessCard(employeeId, file, side) {
        console.warn('Deprecated: Use businesscardApi.uploadBusinessCard instead');

        const formData = new FormData();
        formData.append('file', file);
        formData.append('side', side);

        return apiRequest(`/api/employees/${employeeId}/business-card`, {
            method: 'POST',
            body: formData
        });
    },

    /**
     * @deprecated 신규 API 경로 사용 권장: /api/businesscard/employee/{id}/{side}
     */
    async deleteBusinessCard(employeeId, side) {
        console.warn('Deprecated: Use businesscardApi.deleteBusinessCard instead');

        return apiRequest(`/api/employees/${employeeId}/business-card/${side}`, {
            method: 'DELETE'
        });
    }
};
