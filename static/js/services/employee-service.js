/**
 * 직원 관련 API 서비스
 */

export class EmployeeService {
    constructor() {
        this.baseUrl = '/api/employees';
    }

    async search(query) {
        try {
            const response = await fetch(`/search?q=${encodeURIComponent(query)}`, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            return await response.json();
        } catch (error) {
            console.error('Search error:', error);
            throw error;
        }
    }

    async getById(id) {
        try {
            const response = await fetch(`/employees/${id}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Get employee error:', error);
            throw error;
        }
    }

    async getAll(filters = {}) {
        try {
            const params = new URLSearchParams(filters);
            const response = await fetch(`/employees?${params.toString()}`);
            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }
            return await response.json();
        } catch (error) {
            console.error('Get employees error:', error);
            throw error;
        }
    }
}

// 전역 함수로도 사용 가능하도록 (기존 코드 호환성)
export async function searchEmployees(query) {
    const service = new EmployeeService();
    return await service.search(query);
}
