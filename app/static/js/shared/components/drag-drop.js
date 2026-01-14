/**
 * Drag & Drop Module for Data Tables
 * data-table 컴포넌트의 행 드래그 앤 드롭 기능
 *
 * Usage:
 * 1. HTML에 드래그 핸들 추가:
 *    <th class="data-table__th--drag"></th>
 *    <td class="data-table__drag-handle"><svg>...</svg></td>
 *
 * 2. JavaScript 초기화:
 *    import { TableDragDrop } from './shared/components/drag-drop.js';
 *    const dragDrop = new TableDragDrop('#family-table');
 *    dragDrop.onReorder((newOrder) => { ... });
 */

/**
 * TableDragDrop - 테이블 행 드래그 앤 드롭 클래스
 */
export class TableDragDrop {
    /**
     * @param {string|HTMLElement} tableSelector - 테이블 선택자 또는 요소
     * @param {Object} options - 옵션
     * @param {string} options.handleSelector - 드래그 핸들 선택자 (기본: '.data-table__drag-handle')
     * @param {string} options.rowSelector - 행 선택자 (기본: 'tbody tr')
     * @param {string} options.draggingClass - 드래그 중 클래스 (기본: 'data-table__row--dragging')
     * @param {string} options.dragOverClass - 드래그 오버 클래스 (기본: 'data-table__row--drag-over')
     * @param {Function} options.onReorder - 순서 변경 콜백
     */
    constructor(tableSelector, options = {}) {
        this.table = typeof tableSelector === 'string'
            ? document.querySelector(tableSelector)
            : tableSelector;

        if (!this.table) {
            console.warn('TableDragDrop: 테이블을 찾을 수 없습니다:', tableSelector);
            return;
        }

        this.options = {
            handleSelector: options.handleSelector || '.data-table__drag-handle',
            rowSelector: options.rowSelector || 'tbody tr',
            draggingClass: options.draggingClass || 'data-table__row--dragging',
            dragOverClass: options.dragOverClass || 'data-table__row--drag-over',
            onReorder: options.onReorder || null
        };

        this.draggedRow = null;
        this.tbody = this.table.querySelector('tbody');

        this.init();
    }

    /**
     * 초기화
     */
    init() {
        if (!this.tbody) return;

        this.tbody.addEventListener('dragstart', this.handleDragStart.bind(this));
        this.tbody.addEventListener('dragend', this.handleDragEnd.bind(this));
        this.tbody.addEventListener('dragover', this.handleDragOver.bind(this));
        this.tbody.addEventListener('dragleave', this.handleDragLeave.bind(this));
        this.tbody.addEventListener('drop', this.handleDrop.bind(this));

        // 각 행에 draggable 속성 추가
        this.updateRows();
    }

    /**
     * 행 업데이트 (동적으로 추가된 행 지원)
     */
    updateRows() {
        const rows = this.tbody.querySelectorAll(this.options.rowSelector);
        rows.forEach((row, index) => {
            // 빈 상태 행은 제외
            if (row.querySelector('.data-table__cell--empty')) return;

            row.draggable = true;
            row.dataset.index = index;

            // 드래그 핸들에 커서 스타일 적용
            const handle = row.querySelector(this.options.handleSelector);
            if (handle) {
                handle.style.cursor = 'grab';
            }
        });
    }

    /**
     * 드래그 시작
     */
    handleDragStart(e) {
        const row = e.target.closest(this.options.rowSelector);
        if (!row) return;

        // 빈 상태 행은 드래그 불가
        if (row.querySelector('.data-table__cell--empty')) {
            e.preventDefault();
            return;
        }

        this.draggedRow = row;
        row.classList.add(this.options.draggingClass);

        // 드래그 데이터 설정
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', row.dataset.index);

        // 드래그 이미지 설정 (전체 행)
        e.dataTransfer.setDragImage(row, 0, row.offsetHeight / 2);
    }

    /**
     * 드래그 종료
     */
    handleDragEnd(e) {
        const row = e.target.closest(this.options.rowSelector);
        if (row) {
            row.classList.remove(this.options.draggingClass);
        }

        // 모든 드래그 오버 클래스 제거
        this.clearDragOverClass();
        this.draggedRow = null;
    }

    /**
     * 드래그 오버
     */
    handleDragOver(e) {
        e.preventDefault();
        e.dataTransfer.dropEffect = 'move';

        const row = e.target.closest(this.options.rowSelector);
        if (!row || row === this.draggedRow) return;

        // 빈 상태 행 위에는 드롭 불가
        if (row.querySelector('.data-table__cell--empty')) return;

        // 기존 드래그 오버 클래스 제거 후 현재 행에 추가
        this.clearDragOverClass();
        row.classList.add(this.options.dragOverClass);
    }

    /**
     * 드래그 리브
     */
    handleDragLeave(e) {
        const row = e.target.closest(this.options.rowSelector);
        if (row) {
            row.classList.remove(this.options.dragOverClass);
        }
    }

    /**
     * 드롭
     */
    handleDrop(e) {
        e.preventDefault();
        this.clearDragOverClass();

        const targetRow = e.target.closest(this.options.rowSelector);
        if (!targetRow || !this.draggedRow || targetRow === this.draggedRow) return;

        // 빈 상태 행 위에는 드롭 불가
        if (targetRow.querySelector('.data-table__cell--empty')) return;

        // 행 위치 교환
        const allRows = Array.from(this.tbody.querySelectorAll(this.options.rowSelector));
        const draggedIndex = allRows.indexOf(this.draggedRow);
        const targetIndex = allRows.indexOf(targetRow);

        if (draggedIndex < targetIndex) {
            targetRow.after(this.draggedRow);
        } else {
            targetRow.before(this.draggedRow);
        }

        // 인덱스 업데이트
        this.updateRows();

        // 새 순서 계산 및 콜백 호출
        if (this.options.onReorder) {
            const newOrder = this.getRowOrder();
            this.options.onReorder(newOrder);
        }
    }

    /**
     * 드래그 오버 클래스 전체 제거
     */
    clearDragOverClass() {
        const rows = this.tbody.querySelectorAll(`.${this.options.dragOverClass}`);
        rows.forEach(row => row.classList.remove(this.options.dragOverClass));
    }

    /**
     * 현재 행 순서 반환
     * @returns {Array} - 행 데이터 배열 (각 행의 data-id 또는 인덱스)
     */
    getRowOrder() {
        const rows = this.tbody.querySelectorAll(this.options.rowSelector);
        return Array.from(rows)
            .filter(row => !row.querySelector('.data-table__cell--empty'))
            .map((row, index) => ({
                index,
                id: row.dataset.id || null,
                element: row
            }));
    }

    /**
     * 순서 변경 콜백 등록
     * @param {Function} callback - (newOrder: Array) => void
     */
    onReorder(callback) {
        this.options.onReorder = callback;
        return this;
    }

    /**
     * 드래그 앤 드롭 비활성화
     */
    disable() {
        const rows = this.tbody.querySelectorAll(this.options.rowSelector);
        rows.forEach(row => {
            row.draggable = false;
            const handle = row.querySelector(this.options.handleSelector);
            if (handle) {
                handle.style.cursor = 'default';
            }
        });
    }

    /**
     * 드래그 앤 드롭 활성화
     */
    enable() {
        this.updateRows();
    }

    /**
     * 정리
     */
    destroy() {
        this.disable();
        this.tbody.removeEventListener('dragstart', this.handleDragStart);
        this.tbody.removeEventListener('dragend', this.handleDragEnd);
        this.tbody.removeEventListener('dragover', this.handleDragOver);
        this.tbody.removeEventListener('dragleave', this.handleDragLeave);
        this.tbody.removeEventListener('drop', this.handleDrop);
    }
}

/**
 * 드래그 핸들 SVG 아이콘 생성
 * @returns {string} - SVG HTML 문자열
 */
export function createDragHandleIcon() {
    return `<svg xmlns="http://www.w3.org/2000/svg" fill="none" viewBox="0 0 24 24" stroke="currentColor">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 8h16M4 16h16" />
    </svg>`;
}

/**
 * 테이블에 드래그 핸들 컬럼 추가
 * @param {HTMLTableElement} table - 테이블 요소
 */
export function addDragHandleColumn(table) {
    const thead = table.querySelector('thead');
    const tbody = table.querySelector('tbody');

    if (!thead || !tbody) return;

    // 헤더에 드래그 컬럼 추가
    const headerRow = thead.querySelector('tr');
    if (headerRow) {
        const th = document.createElement('th');
        th.className = 'data-table__header data-table__th--drag';
        headerRow.insertBefore(th, headerRow.firstChild);
    }

    // 각 데이터 행에 드래그 핸들 추가
    const rows = tbody.querySelectorAll('tr');
    rows.forEach(row => {
        // 빈 상태 행은 colspan 증가만
        const emptyCell = row.querySelector('.data-table__cell--empty');
        if (emptyCell) {
            const colspan = parseInt(emptyCell.getAttribute('colspan') || '1');
            emptyCell.setAttribute('colspan', (colspan + 1).toString());
            return;
        }

        const td = document.createElement('td');
        td.className = 'data-table__drag-handle';
        td.innerHTML = createDragHandleIcon();
        row.insertBefore(td, row.firstChild);
    });
}

/**
 * 모든 data-table에 드래그 앤 드롭 자동 초기화
 * @param {string} selector - 테이블 선택자 (기본: '.data-table[data-draggable="true"]')
 * @returns {TableDragDrop[]} - 초기화된 인스턴스 배열
 */
export function initAllDraggableTables(selector = '.data-table[data-draggable="true"]') {
    const tables = document.querySelectorAll(selector);
    return Array.from(tables).map(table => new TableDragDrop(table));
}

// 기본 내보내기
export default TableDragDrop;
