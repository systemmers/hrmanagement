/**
 * 법인 세팅 API 서비스
 */

import { get, post, put, del } from '../../../shared/utils/api.js';

const BASE_URL = '/api/corporate';

export const ClassificationApi = {
    async getAll() {
        return get(`${BASE_URL}/classifications`);
    },

    async getOrganization() {
        return get(`${BASE_URL}/classifications/organization`);
    },

    async getEmployment() {
        return get(`${BASE_URL}/classifications/employment`);
    },

    async getByCategory(category) {
        return get(`${BASE_URL}/classifications/${category}`);
    },

    async add(category, data) {
        return post(`${BASE_URL}/classifications/${category}`, data);
    },

    async update(category, optionId, data) {
        return put(`${BASE_URL}/classifications/${category}/${optionId}`, data);
    },

    async delete(category, optionId) {
        return del(`${BASE_URL}/classifications/${category}/${optionId}`);
    },

    async toggleSystemOption(category, data) {
        return post(`${BASE_URL}/classifications/${category}/toggle`, data);
    }
};

export const SettingsApi = {
    async getAll() {
        return get(`${BASE_URL}/settings`);
    },

    async saveAll(data) {
        return put(`${BASE_URL}/settings`, data);
    },

    async get(key) {
        return get(`${BASE_URL}/settings/${key}`);
    },

    async set(key, value) {
        return put(`${BASE_URL}/settings/${key}`, { value });
    },

    async initializeDefaults() {
        return post(`${BASE_URL}/settings/initialize`);
    }
};

export const NumberCategoryApi = {
    async getAll(type = null) {
        const params = type ? { type } : {};
        return get(`${BASE_URL}/number-categories`, params);
    },

    async getEmployee() {
        return get(`${BASE_URL}/number-categories/employee`);
    },

    async getAsset() {
        return get(`${BASE_URL}/number-categories/asset`);
    },

    async create(data) {
        return post(`${BASE_URL}/number-categories`, data);
    },

    async update(categoryId, data) {
        return put(`${BASE_URL}/number-categories/${categoryId}`, data);
    },

    async delete(categoryId) {
        return del(`${BASE_URL}/number-categories/${categoryId}`);
    },

    async previewNext(categoryId) {
        return get(`${BASE_URL}/number-categories/${categoryId}/preview`);
    },

    async initializeAssets() {
        return post(`${BASE_URL}/number-categories/initialize-assets`);
    }
};

export const VisibilityApi = {
    async get() {
        return get(`${BASE_URL}/visibility`);
    },

    async save(data) {
        return put(`${BASE_URL}/visibility`, data);
    },

    async reset() {
        return post(`${BASE_URL}/visibility/reset`);
    }
};

export const DocumentsApi = {
    async getAll() {
        return get(`${BASE_URL}/documents`);
    },

    async getByCategory(category) {
        return get(`${BASE_URL}/documents/${category}`);
    },

    async getStatistics() {
        return get(`${BASE_URL}/documents/statistics`);
    },

    async getExpiring(days = 30) {
        return get(`${BASE_URL}/documents/expiring`, { days });
    },

    async create(data) {
        return post(`${BASE_URL}/documents`, data);
    },

    async update(documentId, data) {
        return put(`${BASE_URL}/documents/${documentId}`, data);
    },

    async delete(documentId) {
        return del(`${BASE_URL}/documents/${documentId}`);
    },

    /**
     * 파일과 함께 서류 업로드
     * @param {FormData} formData - 파일과 메타데이터가 포함된 FormData
     * @returns {Promise<Object>} 생성된 서류 정보
     */
    async upload(formData) {
        const response = await fetch(`${BASE_URL}/documents/upload`, {
            method: 'POST',
            body: formData
            // Content-Type은 자동 설정됨 (multipart/form-data)
        });

        if (!response.ok) {
            const error = await response.json().catch(() => ({ error: '업로드 실패' }));
            throw new Error(error.error || '서류 업로드에 실패했습니다.');
        }

        return response.json();
    },

    /**
     * 서류 다운로드
     * @param {number} documentId - 문서 ID
     */
    download(documentId) {
        window.location.href = `${BASE_URL}/documents/${documentId}/download`;
    }
};

export const CorporateSettingsApi = {
    classifications: ClassificationApi,
    settings: SettingsApi,
    numberCategories: NumberCategoryApi,
    visibility: VisibilityApi,
    documents: DocumentsApi
};

export default CorporateSettingsApi;
