/**
 * 통합 프로필 서비스
 *
 * 계정 타입(corporate, employee_sub, personal)에 따라 적절한 API 엔드포인트를 자동 선택합니다.
 * Phase 5 리팩토링: Frontend 서비스 통합
 */

export class ProfileService {
    constructor(accountType = null, ownerId = null) {
        // accountType: 'corporate' | 'employee_sub' | 'personal'
        this.accountType = accountType || this._detectAccountType();
        this.ownerId = ownerId;
        this.baseUrls = {
            corporate: '/employees',
            employee_sub: '/employees',
            personal: '/personal'
        };
    }

    /**
     * 계정 타입 자동 감지 (DOM 또는 전역 변수 기반)
     */
    _detectAccountType() {
        // HTML data 속성에서 감지
        const profileContainer = document.querySelector('[data-account-type]');
        if (profileContainer) {
            return profileContainer.dataset.accountType;
        }

        // 전역 변수에서 감지
        if (typeof window.ACCOUNT_TYPE !== 'undefined') {
            return window.ACCOUNT_TYPE;
        }

        // URL 패턴으로 감지
        const path = window.location.pathname;
        if (path.startsWith('/personal')) {
            return 'personal';
        }
        if (path.startsWith('/employees')) {
            return 'corporate';
        }

        // 기본값
        return 'corporate';
    }

    /**
     * 현재 계정 타입에 맞는 base URL 반환
     */
    get baseUrl() {
        return this.baseUrls[this.accountType] || this.baseUrls.corporate;
    }

    /**
     * API 요청 공통 헤더
     */
    get headers() {
        return {
            'Content-Type': 'application/json',
            'X-Requested-With': 'XMLHttpRequest'
        };
    }

    /**
     * API 응답 처리
     */
    async _handleResponse(response) {
        if (!response.ok) {
            const error = await response.json().catch(() => ({}));
            throw new Error(error.message || `HTTP error! status: ${response.status}`);
        }
        return await response.json();
    }

    // ========================================
    // 프로필 CRUD
    // ========================================

    /**
     * 프로필 조회
     */
    async getProfile(id = null) {
        const targetId = id || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/profile`
            : `${this.baseUrl}/${targetId}`;

        try {
            const response = await fetch(url, { headers: this.headers });
            return await this._handleResponse(response);
        } catch (error) {
            console.error('Get profile error:', error);
            throw error;
        }
    }

    /**
     * 프로필 수정
     */
    async updateProfile(id, data) {
        const targetId = id || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/profile/update`
            : `${this.baseUrl}/${targetId}/update`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            });
            return await this._handleResponse(response);
        } catch (error) {
            console.error('Update profile error:', error);
            throw error;
        }
    }

    // ========================================
    // 이력 데이터 CRUD (공통 패턴)
    // ========================================

    /**
     * 이력 데이터 조회 (학력, 경력, 자격증, 어학 등)
     * @param {string} historyType - 'education' | 'career' | 'certificate' | 'language' | 'military' | 'family'
     */
    async getHistory(historyType, ownerId = null) {
        const targetId = ownerId || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/api/${historyType}`
            : `${this.baseUrl}/${targetId}/${historyType}`;

        try {
            const response = await fetch(url, { headers: this.headers });
            return await this._handleResponse(response);
        } catch (error) {
            console.error(`Get ${historyType} error:`, error);
            throw error;
        }
    }

    /**
     * 이력 데이터 추가
     */
    async addHistory(historyType, data, ownerId = null) {
        const targetId = ownerId || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/api/${historyType}`
            : `${this.baseUrl}/${targetId}/${historyType}`;

        try {
            const response = await fetch(url, {
                method: 'POST',
                headers: this.headers,
                body: JSON.stringify(data)
            });
            return await this._handleResponse(response);
        } catch (error) {
            console.error(`Add ${historyType} error:`, error);
            throw error;
        }
    }

    /**
     * 이력 데이터 삭제
     */
    async deleteHistory(historyType, itemId, ownerId = null) {
        const targetId = ownerId || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/api/${historyType}/${itemId}`
            : `${this.baseUrl}/${targetId}/${historyType}/${itemId}`;

        try {
            const response = await fetch(url, {
                method: 'DELETE',
                headers: this.headers
            });
            return await this._handleResponse(response);
        } catch (error) {
            console.error(`Delete ${historyType} error:`, error);
            throw error;
        }
    }

    /**
     * 이력 데이터 전체 교체 (Employee 패턴)
     */
    async replaceHistory(historyType, items, ownerId = null) {
        const targetId = ownerId || this.ownerId;
        const url = this.accountType === 'personal'
            ? `${this.baseUrl}/api/${historyType}/replace`
            : `${this.baseUrl}/${targetId}/${historyType}/replace`;

        try {
            const response = await fetch(url, {
                method: 'PUT',
                headers: this.headers,
                body: JSON.stringify({ items })
            });
            return await this._handleResponse(response);
        } catch (error) {
            console.error(`Replace ${historyType} error:`, error);
            throw error;
        }
    }

    // ========================================
    // 편의 메서드 (명시적 이름)
    // ========================================

    // 학력
    async getEducations(ownerId = null) {
        return this.getHistory('education', ownerId);
    }

    async addEducation(data, ownerId = null) {
        return this.addHistory('education', data, ownerId);
    }

    async deleteEducation(educationId, ownerId = null) {
        return this.deleteHistory('education', educationId, ownerId);
    }

    // 경력
    async getCareers(ownerId = null) {
        return this.getHistory('career', ownerId);
    }

    async addCareer(data, ownerId = null) {
        return this.addHistory('career', data, ownerId);
    }

    async deleteCareer(careerId, ownerId = null) {
        return this.deleteHistory('career', careerId, ownerId);
    }

    // 자격증
    async getCertificates(ownerId = null) {
        return this.getHistory('certificate', ownerId);
    }

    async addCertificate(data, ownerId = null) {
        return this.addHistory('certificate', data, ownerId);
    }

    async deleteCertificate(certificateId, ownerId = null) {
        return this.deleteHistory('certificate', certificateId, ownerId);
    }

    // 어학
    async getLanguages(ownerId = null) {
        return this.getHistory('language', ownerId);
    }

    async addLanguage(data, ownerId = null) {
        return this.addHistory('language', data, ownerId);
    }

    async deleteLanguage(languageId, ownerId = null) {
        return this.deleteHistory('language', languageId, ownerId);
    }

    // 병역
    async getMilitary(ownerId = null) {
        return this.getHistory('military', ownerId);
    }

    async saveMilitary(data, ownerId = null) {
        return this.addHistory('military', data, ownerId);
    }

    // 가족
    async getFamilies(ownerId = null) {
        return this.getHistory('family', ownerId);
    }

    async addFamily(data, ownerId = null) {
        return this.addHistory('family', data, ownerId);
    }

    async deleteFamily(familyId, ownerId = null) {
        return this.deleteHistory('family', familyId, ownerId);
    }
}

// 전역 인스턴스 생성 함수
export function createProfileService(accountType = null, ownerId = null) {
    return new ProfileService(accountType, ownerId);
}

// 기본 export
export default ProfileService;
