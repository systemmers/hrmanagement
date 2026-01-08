/**
 * StorageManager - 테이블 상태 로컬 스토리지 관리
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class StorageManager {
    constructor(storageKey) {
        this.storageKey = `dataTable_${storageKey}`;
    }

    /**
     * 상태 로드
     * @returns {Object|null} 저장된 상태
     */
    load() {
        try {
            const saved = localStorage.getItem(this.storageKey);
            if (saved) {
                return JSON.parse(saved);
            }
        } catch (e) {
            console.warn('Failed to load table state from localStorage:', e);
        }
        return null;
    }

    /**
     * 상태 저장
     * @param {Object} state - 저장할 상태
     */
    save(state) {
        try {
            localStorage.setItem(this.storageKey, JSON.stringify(state));
        } catch (e) {
            console.warn('Failed to save table state to localStorage:', e);
        }
    }

    /**
     * 상태 삭제
     */
    clear() {
        localStorage.removeItem(this.storageKey);
    }
}

export default StorageManager;
