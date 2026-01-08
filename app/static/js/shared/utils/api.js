/**
 * API 호출 유틸리티
 * Phase 7: 프론트엔드 리팩토링
 *
 * fetch API 래퍼 및 API 요청 관련 헬퍼를 제공합니다.
 */

/**
 * CSRF 토큰 가져오기
 * @returns {string|null} CSRF 토큰
 */
function getCsrfToken() {
    const meta = document.querySelector('meta[name="csrf-token"]');
    return meta ? meta.getAttribute('content') : null;
}

/**
 * API 기본 설정
 */
function getDefaultHeaders() {
    const headers = {
        'Content-Type': 'application/json',
        'X-Requested-With': 'XMLHttpRequest'
    };

    const csrfToken = getCsrfToken();
    if (csrfToken) {
        headers['X-CSRFToken'] = csrfToken;
    }

    return headers;
}

/**
 * API 에러 클래스
 */
export class ApiError extends Error {
    constructor(message, status, data = null) {
        super(message);
        this.name = 'ApiError';
        this.status = status;
        this.data = data;
    }
}

/**
 * 응답 처리
 * @param {Response} response - fetch 응답
 * @returns {Promise} 파싱된 응답
 */
async function handleResponse(response) {
    const contentType = response.headers.get('content-type');
    const isJson = contentType && contentType.includes('application/json');

    const data = isJson ? await response.json() : await response.text();

    if (!response.ok) {
        const message = isJson && data.error
            ? data.error
            : `HTTP Error: ${response.status}`;
        throw new ApiError(message, response.status, data);
    }

    return data;
}

/**
 * API 요청 함수
 * @param {string} url - 요청 URL
 * @param {Object} options - 요청 옵션
 * @returns {Promise} 응답 데이터
 */
export async function request(url, options = {}) {
    const {
        method = 'GET',
        headers = {},
        body = null,
        timeout = 30000,
        ...rest
    } = options;

    const controller = new AbortController();
    const timeoutId = setTimeout(() => controller.abort(), timeout);

    try {
        const fetchOptions = {
            method,
            headers: { ...getDefaultHeaders(), ...headers },
            signal: controller.signal,
            ...rest
        };

        if (body && method !== 'GET') {
            fetchOptions.body = typeof body === 'string'
                ? body
                : JSON.stringify(body);
        }

        const response = await fetch(url, fetchOptions);
        return await handleResponse(response);

    } catch (error) {
        if (error.name === 'AbortError') {
            throw new ApiError('요청 시간이 초과되었습니다.', 408);
        }
        throw error;
    } finally {
        clearTimeout(timeoutId);
    }
}

/**
 * GET 요청
 * @param {string} url - 요청 URL
 * @param {Object} params - 쿼리 파라미터
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function get(url, params = {}, options = {}) {
    const queryString = new URLSearchParams(params).toString();
    const fullUrl = queryString ? `${url}?${queryString}` : url;
    return request(fullUrl, { method: 'GET', ...options });
}

/**
 * POST 요청
 * @param {string} url - 요청 URL
 * @param {Object} data - 요청 데이터
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function post(url, data = {}, options = {}) {
    return request(url, { method: 'POST', body: data, ...options });
}

/**
 * PUT 요청
 * @param {string} url - 요청 URL
 * @param {Object} data - 요청 데이터
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function put(url, data = {}, options = {}) {
    return request(url, { method: 'PUT', body: data, ...options });
}

/**
 * PATCH 요청
 * @param {string} url - 요청 URL
 * @param {Object} data - 요청 데이터
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function patch(url, data = {}, options = {}) {
    return request(url, { method: 'PATCH', body: data, ...options });
}

/**
 * DELETE 요청
 * @param {string} url - 요청 URL
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function del(url, options = {}) {
    return request(url, { method: 'DELETE', ...options });
}

/**
 * 폼 데이터 전송 (파일 업로드 포함)
 * @param {string} url - 요청 URL
 * @param {FormData} formData - 폼 데이터
 * @param {Object} options - 추가 옵션
 * @returns {Promise} 응답 데이터
 */
export async function postForm(url, formData, options = {}) {
    const { headers = {}, ...rest } = options;

    // FormData 전송 시 Content-Type 헤더 제거 (브라우저가 자동 설정)
    const formHeaders = { ...headers };
    delete formHeaders['Content-Type'];

    return request(url, {
        method: 'POST',
        headers: formHeaders,
        body: formData,
        ...rest
    });
}

/**
 * 파일 업로드
 * @param {string} url - 업로드 URL
 * @param {File|FileList} files - 파일 또는 파일 목록
 * @param {string} fieldName - 파일 필드명
 * @param {Object} additionalData - 추가 데이터
 * @param {Function} onProgress - 진행률 콜백
 * @returns {Promise} 응답 데이터
 */
export function uploadFile(url, files, fieldName = 'file', additionalData = {}, onProgress = null) {
    return new Promise((resolve, reject) => {
        const formData = new FormData();

        // 파일 추가
        if (files instanceof FileList) {
            Array.from(files).forEach(file => {
                formData.append(fieldName, file);
            });
        } else {
            formData.append(fieldName, files);
        }

        // 추가 데이터
        Object.entries(additionalData).forEach(([key, value]) => {
            formData.append(key, value);
        });

        const xhr = new XMLHttpRequest();

        // 진행률 이벤트
        if (onProgress) {
            xhr.upload.addEventListener('progress', (event) => {
                if (event.lengthComputable) {
                    const percent = Math.round((event.loaded / event.total) * 100);
                    onProgress(percent, event.loaded, event.total);
                }
            });
        }

        xhr.addEventListener('load', () => {
            if (xhr.status >= 200 && xhr.status < 300) {
                try {
                    const data = JSON.parse(xhr.responseText);
                    resolve(data);
                } catch {
                    resolve(xhr.responseText);
                }
            } else {
                reject(new ApiError('업로드 실패', xhr.status));
            }
        });

        xhr.addEventListener('error', () => {
            reject(new ApiError('네트워크 오류', 0));
        });

        xhr.addEventListener('abort', () => {
            reject(new ApiError('업로드 취소됨', 0));
        });

        xhr.open('POST', url);
        xhr.setRequestHeader('X-Requested-With', 'XMLHttpRequest');
        const csrfToken = getCsrfToken();
        if (csrfToken) {
            xhr.setRequestHeader('X-CSRFToken', csrfToken);
        }
        xhr.send(formData);
    });
}

/**
 * 파일 다운로드
 * @param {string} url - 다운로드 URL
 * @param {string} filename - 저장할 파일명
 */
export async function downloadFile(url, filename = null) {
    const response = await fetch(url);

    if (!response.ok) {
        throw new ApiError('다운로드 실패', response.status);
    }

    const blob = await response.blob();
    const downloadUrl = window.URL.createObjectURL(blob);

    const link = document.createElement('a');
    link.href = downloadUrl;
    link.download = filename || getFilenameFromResponse(response) || 'download';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);

    window.URL.revokeObjectURL(downloadUrl);
}

/**
 * Content-Disposition 헤더에서 파일명 추출
 * @param {Response} response - fetch 응답
 * @returns {string|null} 파일명
 */
function getFilenameFromResponse(response) {
    const disposition = response.headers.get('content-disposition');
    if (!disposition) return null;

    const filenameMatch = disposition.match(/filename[^;=\n]*=((['"]).*?\2|[^;\n]*)/);
    if (filenameMatch) {
        return filenameMatch[1].replace(/['"]/g, '');
    }
    return null;
}

/**
 * API 요청 재시도
 * @param {Function} requestFn - 요청 함수
 * @param {number} maxRetries - 최대 재시도 횟수
 * @param {number} delay - 재시도 간격 (ms)
 * @returns {Promise} 응답 데이터
 */
export async function retry(requestFn, maxRetries = 3, delay = 1000) {
    let lastError;

    for (let i = 0; i < maxRetries; i++) {
        try {
            return await requestFn();
        } catch (error) {
            lastError = error;

            // 재시도하지 않을 에러 (4xx)
            if (error instanceof ApiError && error.status >= 400 && error.status < 500) {
                throw error;
            }

            if (i < maxRetries - 1) {
                await new Promise(resolve => setTimeout(resolve, delay * (i + 1)));
            }
        }
    }

    throw lastError;
}

/**
 * API 요청 취소 가능한 래퍼
 * @param {string} url - 요청 URL
 * @param {Object} options - 요청 옵션
 * @returns {Object} { promise, cancel }
 */
export function cancellableRequest(url, options = {}) {
    const controller = new AbortController();

    const promise = request(url, {
        ...options,
        signal: controller.signal
    });

    return {
        promise,
        cancel: () => controller.abort()
    };
}
