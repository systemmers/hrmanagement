/**
 * Attachment API Client
 *
 * 첨부파일 도메인 API 클라이언트
 * 파일 업로드, 삭제, 조회, 순서 변경 기능을 제공합니다.
 */
class AttachmentAPI {
    /**
     * 소유자별 첨부파일 목록 조회
     * @param {string} ownerType - 소유자 타입 (employee, profile, company)
     * @param {number} ownerId - 소유자 ID
     * @returns {Promise<Object>} - API 응답
     */
    static async getByOwner(ownerType, ownerId) {
        const response = await fetch(`/api/attachments/${ownerType}/${ownerId}`);
        return response.json();
    }

    /**
     * 첨부파일 업로드
     * @param {string} ownerType - 소유자 타입
     * @param {number} ownerId - 소유자 ID
     * @param {File} file - 업로드할 파일
     * @param {string} category - 카테고리 (기본값: document)
     * @returns {Promise<Object>} - API 응답
     */
    static async upload(ownerType, ownerId, file, category = 'document') {
        const formData = new FormData();
        formData.append('file', file);
        formData.append('owner_type', ownerType);
        formData.append('owner_id', ownerId);
        formData.append('category', category);

        const response = await fetch('/api/attachments', {
            method: 'POST',
            body: formData
        });
        return response.json();
    }

    /**
     * 첨부파일 삭제
     * @param {number} attachmentId - 첨부파일 ID
     * @returns {Promise<Object>} - API 응답
     */
    static async delete(attachmentId) {
        const response = await fetch(`/api/attachments/${attachmentId}`, {
            method: 'DELETE'
        });
        return response.json();
    }

    /**
     * 첨부파일 순서 변경
     * @param {string} ownerType - 소유자 타입
     * @param {number} ownerId - 소유자 ID
     * @param {number[]} order - 첨부파일 ID 순서 배열
     * @returns {Promise<Object>} - API 응답
     */
    static async updateOrder(ownerType, ownerId, order) {
        const response = await fetch(`/api/attachments/${ownerType}/${ownerId}/order`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order })
        });
        return response.json();
    }
}


/**
 * Employee 관계형 데이터 순서 변경 API
 */
class EmployeeRelationOrderAPI {
    /**
     * 학력 순서 변경
     * @param {number} employeeId - 직원 ID
     * @param {number[]} order - 학력 ID 순서 배열
     * @returns {Promise<Object>} - API 응답
     */
    static async updateEducationOrder(employeeId, order) {
        const response = await fetch(`/api/employees/${employeeId}/educations/order`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order })
        });
        return response.json();
    }

    /**
     * 경력 순서 변경
     * @param {number} employeeId - 직원 ID
     * @param {number[]} order - 경력 ID 순서 배열
     * @returns {Promise<Object>} - API 응답
     */
    static async updateCareerOrder(employeeId, order) {
        const response = await fetch(`/api/employees/${employeeId}/careers/order`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order })
        });
        return response.json();
    }

    /**
     * 자격증 순서 변경
     * @param {number} employeeId - 직원 ID
     * @param {number[]} order - 자격증 ID 순서 배열
     * @returns {Promise<Object>} - API 응답
     */
    static async updateCertificateOrder(employeeId, order) {
        const response = await fetch(`/api/employees/${employeeId}/certificates/order`, {
            method: 'PATCH',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ order })
        });
        return response.json();
    }
}


// 전역 export
window.AttachmentAPI = AttachmentAPI;
window.EmployeeRelationOrderAPI = EmployeeRelationOrderAPI;
