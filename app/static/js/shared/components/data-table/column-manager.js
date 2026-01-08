/**
 * ColumnManager - 컬럼 순서 및 가시성 관리
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class ColumnManager {
    constructor(columns, storageManager) {
        this.columns = columns;
        this.storageManager = storageManager;
        this.columnOrder = columns.map(c => c.key);
        this.columnVisibility = {};

        this._initVisibility();
        this._loadSavedState();
    }

    /**
     * 초기 가시성 설정
     */
    _initVisibility() {
        this.columns.forEach(col => {
            this.columnVisibility[col.key] = col.visible !== false;
        });
    }

    /**
     * 저장된 상태 로드
     */
    _loadSavedState() {
        const saved = this.storageManager?.load();
        if (saved) {
            if (saved.columnOrder) {
                // 저장된 순서 중 현재 존재하는 컬럼만 유지
                const existingKeys = new Set(this.columns.map(c => c.key));
                this.columnOrder = saved.columnOrder.filter(key => existingKeys.has(key));

                // 새로 추가된 컬럼은 끝에 추가
                this.columns.forEach(col => {
                    if (!this.columnOrder.includes(col.key)) {
                        this.columnOrder.push(col.key);
                    }
                });
            }
            if (saved.columnVisibility) {
                Object.assign(this.columnVisibility, saved.columnVisibility);
            }
        }
    }

    /**
     * 상태 저장
     */
    saveState() {
        this.storageManager?.save({
            columnOrder: this.columnOrder,
            columnVisibility: this.columnVisibility
        });
    }

    /**
     * 정렬된 컬럼 목록 반환
     * @param {boolean} visibleOnly - 보이는 컬럼만 반환
     * @returns {Array} 컬럼 목록
     */
    getOrderedColumns(visibleOnly = true) {
        return this.columnOrder
            .map(key => this.columns.find(c => c.key === key))
            .filter(col => col && (!visibleOnly || this.columnVisibility[col.key]));
    }

    /**
     * 컬럼 가시성 토글
     * @param {string} columnKey - 컬럼 키
     */
    toggleVisibility(columnKey) {
        this.columnVisibility[columnKey] = !this.columnVisibility[columnKey];
        this.saveState();
    }

    /**
     * 모든 컬럼 표시
     */
    showAll() {
        this.columns.forEach(col => {
            this.columnVisibility[col.key] = true;
        });
        this.saveState();
    }

    /**
     * 컬럼 이동
     * @param {string} columnKey - 이동할 컬럼 키
     * @param {number} direction - 이동 방향 (-1: 왼쪽, 1: 오른쪽)
     * @returns {boolean} 이동 성공 여부
     */
    move(columnKey, direction) {
        const idx = this.columnOrder.indexOf(columnKey);
        if (idx === -1) return false;

        const newIdx = idx + direction;
        if (newIdx < 0 || newIdx >= this.columnOrder.length) return false;

        // 스왑
        [this.columnOrder[idx], this.columnOrder[newIdx]] =
        [this.columnOrder[newIdx], this.columnOrder[idx]];

        this.saveState();
        return true;
    }

    /**
     * 컬럼 순서 재정렬
     * @param {string} srcKey - 소스 컬럼 키
     * @param {string} targetKey - 타겟 컬럼 키
     * @returns {boolean} 재정렬 성공 여부
     */
    reorder(srcKey, targetKey) {
        const srcIdx = this.columnOrder.indexOf(srcKey);
        const targetIdx = this.columnOrder.indexOf(targetKey);

        if (srcIdx === -1 || targetIdx === -1) return false;

        const newOrder = [...this.columnOrder];
        newOrder.splice(srcIdx, 1);
        newOrder.splice(targetIdx, 0, srcKey);

        this.columnOrder = newOrder;
        this.saveState();
        return true;
    }

    /**
     * 기본 상태로 초기화
     */
    reset() {
        this.columnOrder = this.columns.map(c => c.key);
        this.columns.forEach(col => {
            this.columnVisibility[col.key] = col.visible !== false;
        });
        this.storageManager?.clear();
    }

    /**
     * 컬럼 정보 조회
     * @param {string} key - 컬럼 키
     * @returns {Object|undefined} 컬럼 정보
     */
    getColumn(key) {
        return this.columns.find(c => c.key === key);
    }

    /**
     * 컬럼 가시성 확인
     * @param {string} key - 컬럼 키
     * @returns {boolean} 가시성 여부
     */
    isVisible(key) {
        return this.columnVisibility[key] !== false;
    }
}

export default ColumnManager;
