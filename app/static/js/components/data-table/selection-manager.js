/**
 * SelectionManager - 행 선택 관리
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class SelectionManager {
    constructor() {
        this.selectedRows = new Set();
        this.onSelectionChange = null;
    }

    /**
     * 행 선택/해제
     * @param {number|string} rowId - 행 ID
     * @param {boolean} selected - 선택 여부
     */
    selectRow(rowId, selected) {
        const id = Number(rowId);

        if (selected) {
            this.selectedRows.add(id);
        } else {
            this.selectedRows.delete(id);
        }

        this._triggerChange();
    }

    /**
     * 전체 선택/해제
     * @param {Array} rows - 대상 행 데이터 배열
     * @param {boolean} selected - 선택 여부
     */
    selectAll(rows, selected) {
        if (selected) {
            rows.forEach(row => this.selectedRows.add(Number(row.id)));
        } else {
            rows.forEach(row => this.selectedRows.delete(Number(row.id)));
        }

        this._triggerChange();
    }

    /**
     * 선택 여부 확인
     * @param {number|string} rowId - 행 ID
     * @returns {boolean} 선택 여부
     */
    isSelected(rowId) {
        return this.selectedRows.has(Number(rowId));
    }

    /**
     * 전체 선택 여부 확인
     * @param {Array} rows - 대상 행 데이터 배열
     * @returns {boolean} 전체 선택 여부
     */
    isAllSelected(rows) {
        return rows.length > 0 && rows.every(row => this.selectedRows.has(Number(row.id)));
    }

    /**
     * 선택된 ID 목록 반환
     * @returns {Array} 선택된 ID 배열
     */
    getSelectedIds() {
        return Array.from(this.selectedRows);
    }

    /**
     * 선택된 데이터 반환
     * @param {Array} allData - 전체 데이터
     * @returns {Array} 선택된 행 데이터
     */
    getSelectedData(allData) {
        return allData.filter(row => this.selectedRows.has(Number(row.id)));
    }

    /**
     * 선택 개수 반환
     * @returns {number} 선택된 행 개수
     */
    getSelectedCount() {
        return this.selectedRows.size;
    }

    /**
     * 선택 초기화
     */
    clear() {
        this.selectedRows.clear();
        this._triggerChange();
    }

    /**
     * 변경 콜백 트리거
     */
    _triggerChange() {
        if (this.onSelectionChange) {
            this.onSelectionChange(this.getSelectedIds());
        }
    }

    /**
     * 변경 콜백 설정
     * @param {Function} callback - 콜백 함수
     */
    setOnSelectionChange(callback) {
        this.onSelectionChange = callback;
    }
}

export default SelectionManager;
