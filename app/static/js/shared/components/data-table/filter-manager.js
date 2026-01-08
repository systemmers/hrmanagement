/**
 * FilterManager - 데이터 필터링 및 정렬 관리
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class FilterManager {
    constructor(columns) {
        this.columns = columns;
        this.searchQuery = '';
        this.sortColumn = null;
        this.sortDirection = 'asc';
    }

    /**
     * 검색어 설정
     * @param {string} query - 검색어
     */
    setSearchQuery(query) {
        this.searchQuery = query;
    }

    /**
     * 정렬 설정
     * @param {string} columnKey - 정렬할 컬럼 키
     */
    setSort(columnKey) {
        if (this.sortColumn === columnKey) {
            this.sortDirection = this.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.sortColumn = columnKey;
            this.sortDirection = 'asc';
        }
    }

    /**
     * 정렬 초기화
     */
    clearSort() {
        this.sortColumn = null;
        this.sortDirection = 'asc';
    }

    /**
     * 데이터 필터링 및 정렬
     * @param {Array} data - 원본 데이터
     * @returns {Array} 필터링된 데이터
     */
    filter(data) {
        let result = [...data];

        // 검색 필터
        if (this.searchQuery) {
            const query = this.searchQuery.toLowerCase();
            result = result.filter(row => {
                return this.columns.some(col => {
                    const value = row[col.key];
                    return value && String(value).toLowerCase().includes(query);
                });
            });
        }

        // 정렬
        if (this.sortColumn) {
            const col = this.columns.find(c => c.key === this.sortColumn);
            result.sort((a, b) => {
                let aVal = a[this.sortColumn];
                let bVal = b[this.sortColumn];

                // null 처리
                if (aVal === null || aVal === undefined) return 1;
                if (bVal === null || bVal === undefined) return -1;

                // 숫자 비교
                if (col && (col.type === 'number' || col.type === 'currency')) {
                    aVal = Number(aVal) || 0;
                    bVal = Number(bVal) || 0;
                }

                // 문자열 비교
                if (typeof aVal === 'string') {
                    aVal = aVal.toLowerCase();
                    bVal = String(bVal).toLowerCase();
                }

                if (aVal < bVal) return this.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }

        return result;
    }

    /**
     * 현재 상태 반환
     * @returns {Object} 현재 필터 상태
     */
    getState() {
        return {
            searchQuery: this.searchQuery,
            sortColumn: this.sortColumn,
            sortDirection: this.sortDirection
        };
    }
}

export default FilterManager;
