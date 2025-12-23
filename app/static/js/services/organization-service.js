/**
 * 조직 관련 API 서비스
 *
 * 조직 트리 관리, CRUD 작업을 위한 서비스 레이어
 */

export class OrganizationService {
    constructor() {
        this.baseUrl = '/admin/api/organizations';
    }

    /**
     * 조직 트리 전체 조회
     * @returns {Promise<Array>} 조직 트리 목록
     */
    async getTree() {
        try {
            const response = await fetch(this.baseUrl, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Get organization tree error:', error);
            throw error;
        }
    }

    /**
     * 특정 조직 조회
     * @param {number} id - 조직 ID
     * @returns {Promise<Object>} 조직 정보
     */
    async get(id) {
        try {
            const response = await fetch(`${this.baseUrl}/${id}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Get organization error:', error);
            throw error;
        }
    }

    /**
     * 조직 생성
     * @param {Object} data - 조직 생성 데이터
     * @returns {Promise<Object>} 생성된 조직 정보
     */
    async create(data) {
        try {
            const response = await fetch(this.baseUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Create organization error:', error);
            throw error;
        }
    }

    /**
     * 조직 수정
     * @param {number} id - 조직 ID
     * @param {Object} data - 조직 수정 데이터
     * @returns {Promise<Object>} 수정된 조직 정보
     */
    async update(id, data) {
        try {
            const response = await fetch(`${this.baseUrl}/${id}`, {
                method: 'PUT',
                headers: {
                    'Content-Type': 'application/json',
                    'X-Requested-With': 'XMLHttpRequest'
                },
                body: JSON.stringify(data)
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Update organization error:', error);
            throw error;
        }
    }

    /**
     * 조직 삭제
     * @param {number} id - 조직 ID
     * @returns {Promise<Object>} 삭제 결과
     */
    async delete(id) {
        try {
            const response = await fetch(`${this.baseUrl}/${id}`, {
                method: 'DELETE',
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Delete organization error:', error);
            throw error;
        }
    }
}

// 싱글턴 API 객체
export const OrganizationApi = {
    async getTree() {
        const service = new OrganizationService();
        return await service.getTree();
    },
    async get(id) {
        const service = new OrganizationService();
        return await service.get(id);
    },
    async create(data) {
        const service = new OrganizationService();
        return await service.create(data);
    },
    async update(id, data) {
        const service = new OrganizationService();
        return await service.update(id, data);
    },
    async delete(id) {
        const service = new OrganizationService();
        return await service.delete(id);
    }
};

export default OrganizationApi;
