/**
 * Field Registry - 필드 메타데이터 중앙 관리 (JavaScript)
 *
 * Backend FieldRegistry와 동기화되어 필드 순서, 타입, 옵션 등을 관리합니다.
 * SSOT(Single Source of Truth) 원칙에 따라 서버에서 정의를 로드합니다.
 *
 * Phase 29: aliases 시스템 제거 - snake_case 직접 사용
 *
 * Usage:
 *   import { FieldRegistry } from '/static/js/core/field-registry.js';
 *
 *   // 초기화 (페이지 로드 시)
 *   await FieldRegistry.loadFromServer();
 *
 *   // 섹션 조회
 *   const section = FieldRegistry.getSection('education');
 *
 *   // 정렬된 필드 목록
 *   const fields = FieldRegistry.getOrderedFields('education');
 *
 *   // 필드명 정규화
 *   const canonical = FieldRegistry.normalizeFieldName('education', 'graduation_year');
 */

export class FieldRegistry {
    static _sections = {};
    static _domains = {};
    static _loaded = false;
    static _loading = null;  // 로딩 Promise (중복 요청 방지)
    static _accountType = null;

    /**
     * 서버에서 섹션 정의 로드
     *
     * @param {Object} options - 로드 옵션
     * @param {string} options.domain - 특정 도메인만 로드
     * @param {string} options.accountType - 계정 타입 (필터링용)
     * @param {boolean} options.force - 강제 재로드
     * @returns {Promise<void>}
     */
    static async loadFromServer(options = {}) {
        const { domain, accountType, force = false } = options;

        // 이미 로드됨 (강제 아닐 경우 스킵)
        if (this._loaded && !force) {
            return;
        }

        // 이미 로딩 중이면 기존 Promise 반환
        if (this._loading) {
            return this._loading;
        }

        this._loading = this._doLoad(domain, accountType);

        try {
            await this._loading;
            this._loaded = true;
            this._accountType = accountType;
        } finally {
            this._loading = null;
        }
    }

    /**
     * 실제 로드 수행
     * @private
     */
    static async _doLoad(domain, accountType) {
        const params = new URLSearchParams();
        if (domain) params.set('domain', domain);
        if (accountType) params.set('account_type', accountType);

        const url = `/api/fields/sections${params.toString() ? '?' + params.toString() : ''}`;

        try {
            const response = await fetch(url, {
                headers: {
                    'X-Requested-With': 'XMLHttpRequest'
                }
            });

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const data = await response.json();

            // 섹션 저장
            this._sections = {};
            for (const section of data.sections || []) {
                this._sections[section.id] = section;
            }

            // 도메인 매핑 (서버 응답에 포함된 경우)
            if (data.domain) {
                this._domains[data.domain] = Object.keys(this._sections);
            }

        } catch (error) {
            console.error('[FieldRegistry] Failed to load sections:', error);
            throw error;
        }
    }

    /**
     * 특정 섹션 조회
     *
     * @param {string} sectionId - 섹션 ID
     * @returns {Object|null} 섹션 정의
     */
    static getSection(sectionId) {
        return this._sections[sectionId] || null;
    }

    /**
     * 모든 섹션 조회
     *
     * @returns {Object[]} 섹션 목록 (order 기준 정렬)
     */
    static getAllSections() {
        return Object.values(this._sections)
            .sort((a, b) => a.order - b.order);
    }

    /**
     * 동적 섹션만 조회 (is_dynamic = true)
     *
     * @returns {Object[]} 동적 섹션 목록
     */
    static getDynamicSections() {
        return this.getAllSections()
            .filter(section => section.isDynamic);
    }

    /**
     * 섹션의 정렬된 필드 목록 반환
     *
     * @param {string} sectionId - 섹션 ID
     * @returns {Object[]} 필드 정의 목록 (order 기준 정렬)
     */
    static getOrderedFields(sectionId) {
        const section = this.getSection(sectionId);
        if (!section || !section.fields) {
            return [];
        }
        return [...section.fields].sort((a, b) => a.order - b.order);
    }

    /**
     * 섹션의 정렬된 필드명 목록 반환
     *
     * @param {string} sectionId - 섹션 ID
     * @returns {string[]} 필드명 리스트
     */
    static getOrderedFieldNames(sectionId) {
        return this.getOrderedFields(sectionId).map(f => f.name);
    }

    /**
     * 특정 필드 정의 조회
     *
     * Phase 29: alias 검색 제거 - 필드명 직접 매칭만 지원
     *
     * @param {string} sectionId - 섹션 ID
     * @param {string} fieldName - 필드명
     * @returns {Object|null} 필드 정의
     */
    static getField(sectionId, fieldName) {
        const section = this.getSection(sectionId);
        if (!section || !section.fields) {
            return null;
        }
        return section.fields.find(f => f.name === fieldName) || null;
    }

    /**
     * 필드명 정규화 (Phase 29: 입력값 그대로 반환)
     *
     * @param {string} sectionId - 섹션 ID
     * @param {string} name - 필드명
     * @returns {string} 정규화된 필드명
     */
    static normalizeFieldName(sectionId, name) {
        const field = this.getField(sectionId, name);
        return field ? field.name : name;
    }

    /**
     * 섹션의 필드명 매핑 반환
     *
     * Phase 29: alias 매핑 제거 - 필드명 직접 매핑만 반환
     *
     * @param {string} sectionId - 섹션 ID
     * @returns {Object} 매핑 객체
     */
    static getFieldMapping(sectionId) {
        const section = this.getSection(sectionId);
        if (!section || !section.fields) {
            return {};
        }

        const mapping = {};
        for (const field of section.fields) {
            mapping[field.name] = field.name;
        }
        return mapping;
    }

    /**
     * 데이터를 정렬된 순서로 변환
     *
     * @param {string} sectionId - 섹션 ID
     * @param {Object} data - 원본 데이터
     * @returns {Object} 정렬된 객체
     */
    static toOrderedData(sectionId, data) {
        const orderedNames = this.getOrderedFieldNames(sectionId);
        const mapping = this.getFieldMapping(sectionId);
        const result = {};

        // 정렬된 필드부터 추가
        for (const name of orderedNames) {
            // 원본 데이터에서 필드명으로 찾기
            for (const [key, value] of Object.entries(data)) {
                if (mapping[key] === name) {
                    result[name] = value;
                    break;
                }
            }
        }

        // 정의되지 않은 필드는 마지막에 추가 (하위 호환성)
        for (const [key, value] of Object.entries(data)) {
            const canonical = mapping[key] || key;
            if (!(canonical in result)) {
                result[canonical] = value;
            }
        }

        return result;
    }

    /**
     * 필수 필드 목록 반환
     *
     * @param {string} sectionId - 섹션 ID
     * @returns {string[]} 필수 필드명 리스트
     */
    static getRequiredFields(sectionId) {
        return this.getOrderedFields(sectionId)
            .filter(f => f.required)
            .map(f => f.name);
    }

    /**
     * 로드 상태 확인
     *
     * @returns {boolean} 로드 완료 여부
     */
    static isLoaded() {
        return this._loaded;
    }

    /**
     * 캐시 초기화 (테스트용)
     */
    static clear() {
        this._sections = {};
        this._domains = {};
        this._loaded = false;
        this._loading = null;
        this._accountType = null;
    }
}

// 전역 접근용 (기존 코드 호환성)
if (typeof window !== 'undefined') {
    window.FieldRegistry = FieldRegistry;
}
