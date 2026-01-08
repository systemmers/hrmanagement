/**
 * PaginationManager - 페이지네이션 관리
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 */

export class PaginationManager {
    constructor(pageSize = 10) {
        this.pageSize = pageSize;
        this.currentPage = 1;
        this.totalItems = 0;
    }

    /**
     * 총 아이템 수 설정
     * @param {number} total - 총 아이템 수
     */
    setTotalItems(total) {
        this.totalItems = total;
        // 현재 페이지가 범위를 벗어나면 조정
        const totalPages = this.getTotalPages();
        if (this.currentPage > totalPages && totalPages > 0) {
            this.currentPage = totalPages;
        }
    }

    /**
     * 페이지 이동
     * @param {number} page - 이동할 페이지
     * @returns {boolean} 이동 성공 여부
     */
    goToPage(page) {
        const totalPages = this.getTotalPages();
        const newPage = Math.max(1, Math.min(page, totalPages || 1));

        if (newPage !== this.currentPage) {
            this.currentPage = newPage;
            return true;
        }
        return false;
    }

    /**
     * 첫 페이지로 이동
     */
    goToFirst() {
        return this.goToPage(1);
    }

    /**
     * 마지막 페이지로 이동
     */
    goToLast() {
        return this.goToPage(this.getTotalPages());
    }

    /**
     * 이전 페이지로 이동
     */
    goToPrev() {
        return this.goToPage(this.currentPage - 1);
    }

    /**
     * 다음 페이지로 이동
     */
    goToNext() {
        return this.goToPage(this.currentPage + 1);
    }

    /**
     * 총 페이지 수 반환
     * @returns {number} 총 페이지 수
     */
    getTotalPages() {
        return Math.ceil(this.totalItems / this.pageSize);
    }

    /**
     * 현재 페이지 데이터 범위 반환
     * @returns {Object} { start, end }
     */
    getPageRange() {
        const start = (this.currentPage - 1) * this.pageSize;
        const end = start + this.pageSize;
        return { start, end };
    }

    /**
     * 현재 페이지 데이터 슬라이스
     * @param {Array} data - 전체 데이터
     * @returns {Array} 현재 페이지 데이터
     */
    getPageData(data) {
        const { start, end } = this.getPageRange();
        return data.slice(start, end);
    }

    /**
     * 페이지 번호 목록 생성 (UI 렌더링용)
     * @returns {Array} 페이지 번호 배열 (숫자 또는 '...')
     */
    getPageNumbers() {
        const current = this.currentPage;
        const total = this.getTotalPages();

        if (total <= 7) {
            return Array.from({ length: total }, (_, i) => i + 1);
        }

        if (current <= 4) {
            return [1, 2, 3, 4, 5, '...', total];
        } else if (current >= total - 3) {
            return [1, '...', total - 4, total - 3, total - 2, total - 1, total];
        } else {
            return [1, '...', current - 1, current, current + 1, '...', total];
        }
    }

    /**
     * 표시 정보 반환
     * @returns {Object} { from, to, total, selectedCount }
     */
    getDisplayInfo(selectedCount = 0) {
        const from = this.totalItems > 0
            ? (this.currentPage - 1) * this.pageSize + 1
            : 0;
        const to = Math.min(this.currentPage * this.pageSize, this.totalItems);

        return {
            from,
            to,
            total: this.totalItems,
            selectedCount,
            currentPage: this.currentPage,
            totalPages: this.getTotalPages()
        };
    }

    /**
     * 페이지 크기 변경
     * @param {number} newSize - 새 페이지 크기
     */
    setPageSize(newSize) {
        this.pageSize = newSize;
        this.currentPage = 1;
    }

    /**
     * 초기화
     */
    reset() {
        this.currentPage = 1;
    }
}

export default PaginationManager;
