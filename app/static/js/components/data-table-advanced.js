/**
 * Advanced Data Table Component
 * Phase 7: 프론트엔드 리팩토링 - 모듈 분할
 *
 * 고급 데이터 테이블 - 소팅, 검색, 행선택, 컬럼 토글, 컬럼 재정렬
 *
 * 이 파일은 하위 호환성을 위해 유지됩니다.
 * 개별 기능이 필요한 경우 './data-table/index.js'에서 import하세요:
 *
 * import {
 *   StorageManager,
 *   ColumnManager,
 *   FilterManager,
 *   PaginationManager,
 *   SelectionManager,
 *   CellRenderer,
 *   ExcelExporter
 * } from './data-table/index.js';
 *
 * 사용법 (기존 방식, 유지됨):
 * const table = new DataTableAdvanced('containerId', {
 *   columns: [{ key: 'name', label: '이름', sortable: true, width: '200px' }],
 *   data: [{ id: 1, name: '홍길동' }],
 *   features: { sorting: true, search: true, rowSelection: true, columnToggle: true, columnReorder: true },
 *   pageSize: 10,
 *   storageKey: 'myTable'
 * });
 */

class DataTableAdvanced {
    constructor(containerId, options = {}) {
        this.container = document.getElementById(containerId);
        if (!this.container) {
            console.error(`Container #${containerId} not found`);
            return;
        }

        // 기본 옵션
        this.options = {
            columns: [],
            data: [],
            features: {
                sorting: true,
                search: true,
                rowSelection: true,
                columnToggle: true,
                columnReorder: true,
                pagination: true
            },
            pageSize: 10,
            storageKey: containerId,
            onRowSelect: null,
            onSort: null,
            onSearch: null,
            ...options
        };

        // 상태
        this.state = {
            columnOrder: this.options.columns.map(c => c.key),
            columnVisibility: {},
            sortColumn: null,
            sortDirection: 'asc',
            selectedRows: new Set(),
            searchQuery: '',
            currentPage: 1,
            filteredData: []
        };

        // 초기화
        this._initColumnVisibility();
        this._loadFromStorage();
        this._render();
        this._bindEvents();
    }

    // ========================================
    // 초기화 메서드
    // ========================================

    _initColumnVisibility() {
        this.options.columns.forEach(col => {
            if (this.state.columnVisibility[col.key] === undefined) {
                this.state.columnVisibility[col.key] = col.visible !== false;
            }
        });
    }

    _loadFromStorage() {
        const key = `dataTable_${this.options.storageKey}`;
        try {
            const saved = localStorage.getItem(key);
            if (saved) {
                const parsed = JSON.parse(saved);
                if (parsed.columnOrder) this.state.columnOrder = parsed.columnOrder;
                if (parsed.columnVisibility) this.state.columnVisibility = parsed.columnVisibility;
            }
        } catch (e) {
            console.warn('Failed to load table state from localStorage:', e);
        }
    }

    _saveToStorage() {
        const key = `dataTable_${this.options.storageKey}`;
        try {
            localStorage.setItem(key, JSON.stringify({
                columnOrder: this.state.columnOrder,
                columnVisibility: this.state.columnVisibility
            }));
        } catch (e) {
            console.warn('Failed to save table state to localStorage:', e);
        }
    }

    // ========================================
    // 렌더링 메서드
    // ========================================

    _render() {
        this._filterData();

        const html = `
            <div class="data-table-advanced-container">
                ${this._renderToolbar()}
                <div class="data-table-wrapper">
                    <table class="data-table-advanced">
                        ${this._renderHeader()}
                        ${this._renderBody()}
                        ${this._renderFooter()}
                    </table>
                </div>
                ${this._renderPagination()}
            </div>
        `;

        this.container.innerHTML = html;
        this._bindEvents();
    }

    /**
     * 테이블 본문, 푸터, 페이지네이션만 부분 렌더링
     * 검색 시 입력창 포커스 유지를 위해 사용
     */
    _renderPartial() {
        this._filterData();

        // 테이블 본문 업데이트
        const tbody = this.container.querySelector('tbody');
        if (tbody) {
            tbody.innerHTML = this._renderBodyRows();
        }

        // 테이블 푸터 업데이트
        const tfoot = this.container.querySelector('tfoot');
        if (tfoot) {
            tfoot.innerHTML = this._renderFooterRows();
        }

        // 페이지네이션 업데이트
        const footer = this.container.querySelector('.data-table-footer');
        if (footer) {
            footer.outerHTML = this._renderPagination();
            this._bindPaginationEvents();
        }

        // 초기화 버튼 표시/숨김
        const clearBtn = this.container.querySelector('.clear-search-btn');
        if (clearBtn) {
            clearBtn.style.display = this.state.searchQuery ? '' : 'none';
        }
    }

    /**
     * 페이지네이션 이벤트만 바인딩
     */
    _bindPaginationEvents() {
        this.container.querySelectorAll('.pagination-btn').forEach(btn => {
            const page = btn.dataset.page;
            if (page) {
                btn.addEventListener('click', () => this.goToPage(parseInt(page)));
            }
        });
    }

    _renderToolbar() {
        const { features } = this.options;

        return `
            <div class="data-table-toolbar">
                <div class="data-table-toolbar-left">
                    ${features.search ? `
                        <div class="data-table-search">
                            <i class="fas fa-search"></i>
                            <input type="text"
                                   placeholder="검색어를 입력하세요..."
                                   value="${this.state.searchQuery}"
                                   class="search-input">
                        </div>
                        <button class="data-table-btn clear-search-btn" ${!this.state.searchQuery ? 'style="display:none"' : ''}>
                            <i class="fas fa-times"></i> 초기화
                        </button>
                    ` : ''}
                </div>
                <div class="data-table-toolbar-right">
                    ${features.excelExport ? `
                        <button class="data-table-btn export-excel-btn">
                            <i class="fas fa-file-excel"></i> 엑셀 다운로드
                        </button>
                    ` : ''}
                    ${features.columnToggle ? `
                        <div style="position: relative;">
                            <button class="data-table-btn column-settings-btn">
                                <i class="fas fa-columns"></i> 컬럼 설정
                            </button>
                            ${this._renderColumnSettings()}
                        </div>
                    ` : ''}
                    <button class="data-table-btn reset-layout-btn">
                        <i class="fas fa-undo"></i> 레이아웃 초기화
                    </button>
                </div>
            </div>
        `;
    }

    _renderColumnSettings() {
        const columns = this._getOrderedColumns(false); // 모든 컬럼 (숨김 포함)

        return `
            <div class="column-settings-popover">
                <div class="column-settings-header">컬럼 설정</div>
                <div class="column-settings-list">
                    ${columns.map((col, idx) => `
                        <div class="column-settings-item" data-key="${col.key}" draggable="true">
                            <i class="fas fa-grip-vertical drag-handle"></i>
                            <input type="checkbox"
                                   ${this.state.columnVisibility[col.key] ? 'checked' : ''}
                                   data-column="${col.key}">
                            <span>${col.label}</span>
                        </div>
                    `).join('')}
                </div>
                <div class="column-settings-footer">
                    <button class="data-table-btn" onclick="this.closest('.column-settings-popover').classList.remove('active')">
                        닫기
                    </button>
                    <button class="data-table-btn show-all-columns-btn">
                        전체 표시
                    </button>
                </div>
            </div>
        `;
    }

    _renderHeader() {
        const { features } = this.options;
        const columns = this._getOrderedColumns();

        return `
            <thead>
                <tr>
                    ${features.rowSelection ? `
                        <th class="checkbox-cell">
                            <input type="checkbox" class="select-all-checkbox"
                                   ${this._isAllSelected() ? 'checked' : ''}>
                        </th>
                    ` : ''}
                    ${columns.map((col, idx) => {
                        const isSorted = this.state.sortColumn === col.key;
                        const sortClass = isSorted ? this.state.sortDirection : '';
                        const draggable = features.columnReorder ? 'draggable' : '';

                        return `
                            <th class="${draggable}"
                                data-key="${col.key}"
                                style="${col.width ? `width: ${col.width}` : ''}">
                                <div class="th-content">
                                    <div class="th-label">
                                        <span>${col.label}</span>
                                        ${features.sorting && col.sortable !== false ? `
                                            <button class="sort-btn ${sortClass}" data-column="${col.key}">
                                                <i class="fas fa-sort"></i>
                                            </button>
                                        ` : ''}
                                    </div>
                                    ${features.columnReorder ? `
                                        <div class="th-actions">
                                            <button class="move-btn move-left-btn"
                                                    data-column="${col.key}"
                                                    ${idx === 0 ? 'disabled' : ''}>
                                                <i class="fas fa-chevron-left"></i>
                                            </button>
                                            <button class="move-btn move-right-btn"
                                                    data-column="${col.key}"
                                                    ${idx === columns.length - 1 ? 'disabled' : ''}>
                                                <i class="fas fa-chevron-right"></i>
                                            </button>
                                        </div>
                                    ` : ''}
                                </div>
                            </th>
                        `;
                    }).join('')}
                </tr>
            </thead>
        `;
    }

    _renderBody() {
        return `<tbody>${this._renderBodyRows()}</tbody>`;
    }

    /**
     * tbody 내부의 행들만 반환 (부분 렌더링용)
     */
    _renderBodyRows() {
        const { features } = this.options;
        const columns = this._getOrderedColumns();
        const pageData = this._getPageData();

        if (pageData.length === 0) {
            const colSpan = columns.length + (features.rowSelection ? 1 : 0);
            return `
                <tr>
                    <td colspan="${colSpan}" class="data-table-empty">
                        <i class="fas fa-inbox"></i>
                        <p>데이터가 없습니다</p>
                    </td>
                </tr>
            `;
        }

        return pageData.map(row => {
            const isSelected = this.state.selectedRows.has(Number(row.id));
            return `
                <tr data-id="${row.id}" class="${isSelected ? 'selected' : ''}">
                    ${features.rowSelection ? `
                        <td class="checkbox-cell">
                            <input type="checkbox" class="row-checkbox"
                                   data-id="${row.id}"
                                   ${isSelected ? 'checked' : ''}>
                        </td>
                    ` : ''}
                    ${columns.map(col => {
                        const value = row[col.key];
                        const rendered = this._renderCell(col, value, row);
                        return `<td>${rendered}</td>`;
                    }).join('')}
                </tr>
            `;
        }).join('');
    }

    _renderCell(column, value, row) {
        // 커스텀 렌더러가 있으면 사용
        if (column.render) {
            return column.render(value, row);
        }

        // 기본 렌더러
        if (value === null || value === undefined) {
            return '<span class="text-muted">-</span>';
        }

        // 상태 컬럼 처리
        if (column.type === 'status') {
            const statusClass = String(value).toLowerCase().replace(/\s+/g, '-');
            return `<span class="status-badge ${statusClass}">${value}</span>`;
        }

        // 숫자 포맷
        if (column.type === 'number' || column.type === 'currency') {
            const formatted = new Intl.NumberFormat('ko-KR').format(value);
            if (column.type === 'currency') {
                return `${column.prefix || ''}${formatted}${column.suffix || '원'}`;
            }
            return formatted;
        }

        // 날짜 포맷
        if (column.type === 'date') {
            const date = new Date(value);
            return date.toLocaleDateString('ko-KR');
        }

        return String(value);
    }

    _renderFooter() {
        const sumColumns = this._getOrderedColumns().filter(c => c.sum);
        if (sumColumns.length === 0) return '';
        return `<tfoot>${this._renderFooterRows()}</tfoot>`;
    }

    /**
     * tfoot 내부의 행들만 반환 (부분 렌더링용)
     */
    _renderFooterRows() {
        const columns = this._getOrderedColumns();
        const { features } = this.options;

        const sumColumns = columns.filter(c => c.sum);
        if (sumColumns.length === 0) return '';

        return `
            <tr>
                ${features.rowSelection ? '<td></td>' : ''}
                ${columns.map(col => {
                    if (col.sum) {
                        const sum = this.state.filteredData.reduce((acc, row) => {
                            return acc + (Number(row[col.key]) || 0);
                        }, 0);
                        return `<td class="text-right font-semibold">
                            ${this._renderCell(col, sum, {})}
                        </td>`;
                    }
                    return '<td></td>';
                }).join('')}
            </tr>
        `;
    }

    _renderPagination() {
        if (!this.options.features.pagination) return '';

        const totalItems = this.state.filteredData.length;
        const totalPages = Math.ceil(totalItems / this.options.pageSize);
        const { currentPage } = this.state;
        const selectedCount = this.state.selectedRows.size;

        return `
            <div class="data-table-footer">
                <div class="data-table-info">
                    ${selectedCount > 0 ? `<strong>${selectedCount}</strong>개 선택됨 / ` : ''}
                    총 <strong>${totalItems}</strong>개 중
                    <strong>${(currentPage - 1) * this.options.pageSize + 1}</strong>-<strong>${Math.min(currentPage * this.options.pageSize, totalItems)}</strong> 표시
                </div>
                <div class="data-table-pagination">
                    <button class="pagination-btn first-page-btn" ${currentPage === 1 ? 'disabled' : ''}>
                        <i class="fas fa-angle-double-left"></i>
                    </button>
                    <button class="pagination-btn prev-page-btn" ${currentPage === 1 ? 'disabled' : ''}>
                        <i class="fas fa-angle-left"></i>
                    </button>
                    ${this._renderPageNumbers(currentPage, totalPages)}
                    <button class="pagination-btn next-page-btn" ${currentPage === totalPages ? 'disabled' : ''}>
                        <i class="fas fa-angle-right"></i>
                    </button>
                    <button class="pagination-btn last-page-btn" ${currentPage === totalPages ? 'disabled' : ''}>
                        <i class="fas fa-angle-double-right"></i>
                    </button>
                </div>
            </div>
        `;
    }

    _renderPageNumbers(current, total) {
        if (total <= 7) {
            return Array.from({ length: total }, (_, i) => i + 1)
                .map(p => `<button class="pagination-btn page-btn ${p === current ? 'active' : ''}" data-page="${p}">${p}</button>`)
                .join('');
        }

        let pages = [];
        if (current <= 4) {
            pages = [1, 2, 3, 4, 5, '...', total];
        } else if (current >= total - 3) {
            pages = [1, '...', total - 4, total - 3, total - 2, total - 1, total];
        } else {
            pages = [1, '...', current - 1, current, current + 1, '...', total];
        }

        return pages.map(p => {
            if (p === '...') return '<span class="pagination-ellipsis">...</span>';
            return `<button class="pagination-btn page-btn ${p === current ? 'active' : ''}" data-page="${p}">${p}</button>`;
        }).join('');
    }

    // ========================================
    // 데이터 처리 메서드
    // ========================================

    _filterData() {
        let data = [...this.options.data];

        // 검색 필터
        if (this.state.searchQuery) {
            const query = this.state.searchQuery.toLowerCase();
            data = data.filter(row => {
                return this.options.columns.some(col => {
                    const value = row[col.key];
                    return value && String(value).toLowerCase().includes(query);
                });
            });
        }

        // 소팅
        if (this.state.sortColumn) {
            const col = this.options.columns.find(c => c.key === this.state.sortColumn);
            data.sort((a, b) => {
                let aVal = a[this.state.sortColumn];
                let bVal = b[this.state.sortColumn];

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

                if (aVal < bVal) return this.state.sortDirection === 'asc' ? -1 : 1;
                if (aVal > bVal) return this.state.sortDirection === 'asc' ? 1 : -1;
                return 0;
            });
        }

        this.state.filteredData = data;
    }

    _getPageData() {
        if (!this.options.features.pagination) {
            return this.state.filteredData;
        }

        const start = (this.state.currentPage - 1) * this.options.pageSize;
        const end = start + this.options.pageSize;
        return this.state.filteredData.slice(start, end);
    }

    _getOrderedColumns(visibleOnly = true) {
        return this.state.columnOrder
            .map(key => this.options.columns.find(c => c.key === key))
            .filter(col => col && (!visibleOnly || this.state.columnVisibility[col.key]));
    }

    _isAllSelected() {
        const pageData = this._getPageData();
        return pageData.length > 0 && pageData.every(row => this.state.selectedRows.has(Number(row.id)));
    }

    // ========================================
    // 이벤트 바인딩
    // ========================================

    _bindEvents() {
        // 검색
        const searchInput = this.container.querySelector('.search-input');
        if (searchInput) {
            searchInput.addEventListener('input', (e) => this.search(e.target.value));
        }

        // 검색 초기화
        const clearSearchBtn = this.container.querySelector('.clear-search-btn');
        if (clearSearchBtn) {
            clearSearchBtn.addEventListener('click', () => this.search(''));
        }

        // 컬럼 설정 토글
        const columnSettingsBtn = this.container.querySelector('.column-settings-btn');
        const columnSettingsPopover = this.container.querySelector('.column-settings-popover');
        if (columnSettingsBtn && columnSettingsPopover) {
            columnSettingsBtn.addEventListener('click', (e) => {
                e.stopPropagation();
                columnSettingsPopover.classList.toggle('active');
            });

            // 외부 클릭 시 닫기
            document.addEventListener('click', (e) => {
                if (!columnSettingsPopover.contains(e.target) && e.target !== columnSettingsBtn) {
                    columnSettingsPopover.classList.remove('active');
                }
            });
        }

        // 컬럼 가시성 토글
        this.container.querySelectorAll('.column-settings-item input[type="checkbox"]').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.toggleColumn(e.target.dataset.column);
            });
        });

        // 전체 컬럼 표시
        const showAllBtn = this.container.querySelector('.show-all-columns-btn');
        if (showAllBtn) {
            showAllBtn.addEventListener('click', () => this.showAllColumns());
        }

        // 레이아웃 초기화
        const resetLayoutBtn = this.container.querySelector('.reset-layout-btn');
        if (resetLayoutBtn) {
            resetLayoutBtn.addEventListener('click', () => this.resetLayout());
        }

        // 엑셀 내보내기
        const exportExcelBtn = this.container.querySelector('.export-excel-btn');
        if (exportExcelBtn) {
            exportExcelBtn.addEventListener('click', () => this.exportToExcel());
        }

        // 소팅
        this.container.querySelectorAll('.sort-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.sort(btn.dataset.column);
            });
        });

        // 컬럼 이동 버튼
        this.container.querySelectorAll('.move-left-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.moveColumn(btn.dataset.column, -1);
            });
        });

        this.container.querySelectorAll('.move-right-btn').forEach(btn => {
            btn.addEventListener('click', (e) => {
                e.stopPropagation();
                this.moveColumn(btn.dataset.column, 1);
            });
        });

        // 드래그 앤 드롭 (헤더)
        this._bindHeaderDragDrop();

        // 드래그 앤 드롭 (컬럼 설정)
        this._bindSettingsDragDrop();

        // 행 선택
        const selectAllCheckbox = this.container.querySelector('.select-all-checkbox');
        if (selectAllCheckbox) {
            selectAllCheckbox.addEventListener('change', (e) => this.selectAll(e.target.checked));
        }

        this.container.querySelectorAll('.row-checkbox').forEach(checkbox => {
            checkbox.addEventListener('change', (e) => {
                this.selectRow(checkbox.dataset.id, e.target.checked);
            });
        });

        // 페이지네이션
        this.container.querySelectorAll('.page-btn').forEach(btn => {
            btn.addEventListener('click', () => this.goToPage(Number(btn.dataset.page)));
        });

        const firstPageBtn = this.container.querySelector('.first-page-btn');
        if (firstPageBtn) {
            firstPageBtn.addEventListener('click', () => this.goToPage(1));
        }

        const lastPageBtn = this.container.querySelector('.last-page-btn');
        if (lastPageBtn) {
            const totalPages = Math.ceil(this.state.filteredData.length / this.options.pageSize);
            lastPageBtn.addEventListener('click', () => this.goToPage(totalPages));
        }

        const prevPageBtn = this.container.querySelector('.prev-page-btn');
        if (prevPageBtn) {
            prevPageBtn.addEventListener('click', () => this.goToPage(this.state.currentPage - 1));
        }

        const nextPageBtn = this.container.querySelector('.next-page-btn');
        if (nextPageBtn) {
            nextPageBtn.addEventListener('click', () => this.goToPage(this.state.currentPage + 1));
        }
    }

    _bindHeaderDragDrop() {
        const headers = this.container.querySelectorAll('th.draggable');
        let dragSrcEl = null;

        headers.forEach(th => {
            th.addEventListener('dragstart', (e) => {
                dragSrcEl = th;
                th.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
                e.dataTransfer.setData('text/plain', th.dataset.key);
            });

            th.addEventListener('dragend', () => {
                th.classList.remove('dragging');
                headers.forEach(h => h.classList.remove('drag-over'));
            });

            th.addEventListener('dragover', (e) => {
                e.preventDefault();
                e.dataTransfer.dropEffect = 'move';
            });

            th.addEventListener('dragenter', () => {
                if (th !== dragSrcEl) {
                    th.classList.add('drag-over');
                }
            });

            th.addEventListener('dragleave', () => {
                th.classList.remove('drag-over');
            });

            th.addEventListener('drop', (e) => {
                e.preventDefault();
                th.classList.remove('drag-over');

                if (dragSrcEl && dragSrcEl !== th) {
                    const srcKey = dragSrcEl.dataset.key;
                    const targetKey = th.dataset.key;
                    this._reorderColumns(srcKey, targetKey);
                }
            });
        });
    }

    _bindSettingsDragDrop() {
        const items = this.container.querySelectorAll('.column-settings-item');
        let dragSrcEl = null;

        items.forEach(item => {
            item.addEventListener('dragstart', (e) => {
                dragSrcEl = item;
                item.classList.add('dragging');
                e.dataTransfer.effectAllowed = 'move';
            });

            item.addEventListener('dragend', () => {
                item.classList.remove('dragging');
            });

            item.addEventListener('dragover', (e) => {
                e.preventDefault();
            });

            item.addEventListener('drop', (e) => {
                e.preventDefault();
                if (dragSrcEl && dragSrcEl !== item) {
                    const srcKey = dragSrcEl.dataset.key;
                    const targetKey = item.dataset.key;
                    this._reorderColumns(srcKey, targetKey);
                }
            });
        });
    }

    _reorderColumns(srcKey, targetKey) {
        const srcIdx = this.state.columnOrder.indexOf(srcKey);
        const targetIdx = this.state.columnOrder.indexOf(targetKey);

        if (srcIdx === -1 || targetIdx === -1) return;

        const newOrder = [...this.state.columnOrder];
        newOrder.splice(srcIdx, 1);
        newOrder.splice(targetIdx, 0, srcKey);

        this.state.columnOrder = newOrder;
        this._saveToStorage();
        this._render();
    }

    // ========================================
    // 공개 API
    // ========================================

    search(query) {
        this.state.searchQuery = query;
        this.state.currentPage = 1;

        // 부분 렌더링으로 검색창 포커스 유지
        this._renderPartial();

        if (this.options.onSearch) {
            this.options.onSearch(query, this.state.filteredData);
        }
    }

    sort(columnKey) {
        if (this.state.sortColumn === columnKey) {
            this.state.sortDirection = this.state.sortDirection === 'asc' ? 'desc' : 'asc';
        } else {
            this.state.sortColumn = columnKey;
            this.state.sortDirection = 'asc';
        }

        this._render();

        if (this.options.onSort) {
            this.options.onSort(columnKey, this.state.sortDirection);
        }
    }

    toggleColumn(columnKey) {
        this.state.columnVisibility[columnKey] = !this.state.columnVisibility[columnKey];
        this._saveToStorage();
        this._render();
    }

    showAllColumns() {
        this.options.columns.forEach(col => {
            this.state.columnVisibility[col.key] = true;
        });
        this._saveToStorage();
        this._render();
    }

    moveColumn(columnKey, direction) {
        const idx = this.state.columnOrder.indexOf(columnKey);
        if (idx === -1) return;

        const newIdx = idx + direction;
        if (newIdx < 0 || newIdx >= this.state.columnOrder.length) return;

        const newOrder = [...this.state.columnOrder];
        [newOrder[idx], newOrder[newIdx]] = [newOrder[newIdx], newOrder[idx]];

        this.state.columnOrder = newOrder;
        this._saveToStorage();
        this._render();
    }

    selectRow(rowId, selected) {
        // ID를 숫자로 통일하여 비교
        const id = Number(rowId);

        if (selected) {
            this.state.selectedRows.add(id);
        } else {
            this.state.selectedRows.delete(id);
        }

        this._render();

        if (this.options.onRowSelect) {
            this.options.onRowSelect(Array.from(this.state.selectedRows), this.getSelectedData());
        }
    }

    selectAll(selected) {
        const pageData = this._getPageData();

        if (selected) {
            pageData.forEach(row => this.state.selectedRows.add(Number(row.id)));
        } else {
            pageData.forEach(row => this.state.selectedRows.delete(Number(row.id)));
        }

        this._render();

        if (this.options.onRowSelect) {
            this.options.onRowSelect(Array.from(this.state.selectedRows), this.getSelectedData());
        }
    }

    goToPage(page) {
        const totalPages = Math.ceil(this.state.filteredData.length / this.options.pageSize);
        this.state.currentPage = Math.max(1, Math.min(page, totalPages));
        this._render();
    }

    resetLayout() {
        this.state.columnOrder = this.options.columns.map(c => c.key);
        this.options.columns.forEach(col => {
            this.state.columnVisibility[col.key] = col.visible !== false;
        });

        localStorage.removeItem(`dataTable_${this.options.storageKey}`);
        this._render();
    }

    // ========================================
    // 유틸리티
    // ========================================

    getSelectedData() {
        return this.options.data.filter(row => this.state.selectedRows.has(Number(row.id)));
    }

    getFilteredData() {
        return this.state.filteredData;
    }

    setData(data) {
        this.options.data = data;
        this.state.selectedRows.clear();
        this.state.currentPage = 1;
        this._render();
    }

    refresh() {
        this._render();
    }

    // ========================================
    // 엑셀 내보내기
    // ========================================

    /**
     * 현재 테이블 데이터를 엑셀 파일로 내보내기
     * - 현재 정렬/필터 상태 반영
     * - 현재 표시된 컬럼 순서 및 가시성 반영
     * - 선택된 행이 있으면 선택된 행만 내보내기
     * @param {Object} options - 내보내기 옵션
     * @param {string} options.filename - 파일명 (기본값: 'data_export')
     * @param {boolean} options.selectedOnly - 선택된 행만 내보내기 (기본값: 선택된 행이 있으면 true)
     */
    exportToExcel(options = {}) {
        // SheetJS 라이브러리 확인
        if (typeof XLSX === 'undefined') {
            console.error('SheetJS (XLSX) 라이브러리가 로드되지 않았습니다.');
            alert('엑셀 내보내기 기능을 사용하려면 SheetJS 라이브러리가 필요합니다.');
            return;
        }

        // 내보낼 데이터 결정 (선택된 행 또는 필터링된 데이터)
        const hasSelection = this.state.selectedRows.size > 0;
        const selectedOnly = options.selectedOnly !== undefined ? options.selectedOnly : hasSelection;

        let exportData;
        if (selectedOnly && hasSelection) {
            exportData = this.getSelectedData();
        } else {
            exportData = this.state.filteredData;
        }

        if (exportData.length === 0) {
            alert('내보낼 데이터가 없습니다.');
            return;
        }

        // 현재 표시된 컬럼만, 현재 순서대로 가져오기
        const visibleColumns = this._getOrderedColumns(true);

        // 헤더 행 생성
        const headers = visibleColumns.map(col => col.label);

        // 데이터 행 생성
        const rows = exportData.map(row => {
            return visibleColumns.map(col => {
                const value = row[col.key];

                // 값 포맷팅
                if (value === null || value === undefined) {
                    return '';
                }

                // 숫자 타입은 숫자로 유지 (엑셀에서 숫자로 인식)
                if (col.type === 'number' || col.type === 'currency') {
                    return Number(value) || 0;
                }

                return String(value);
            });
        });

        // 합계 행 추가 (sum 컬럼이 있는 경우)
        const sumColumns = visibleColumns.filter(c => c.sum);
        if (sumColumns.length > 0) {
            const sumRow = visibleColumns.map(col => {
                if (col.sum) {
                    const sum = exportData.reduce((acc, row) => {
                        return acc + (Number(row[col.key]) || 0);
                    }, 0);
                    return sum;
                }
                return '';
            });
            // 첫 번째 셀에 '합계' 표시
            sumRow[0] = '합계';
            rows.push(sumRow);
        }

        // 워크시트 데이터 구성
        const wsData = [headers, ...rows];

        // 워크시트 생성
        const ws = XLSX.utils.aoa_to_sheet(wsData);

        // 컬럼 너비 설정
        const colWidths = visibleColumns.map(col => {
            // 기본 너비 또는 컬럼 설정 기반
            const width = parseInt(col.width) || 100;
            return { wch: Math.max(10, Math.min(50, width / 8)) };
        });
        ws['!cols'] = colWidths;

        // 워크북 생성
        const wb = XLSX.utils.book_new();
        XLSX.utils.book_append_sheet(wb, ws, '데이터');

        // 파일명 생성
        const filename = options.filename || this.options.exportFilename || 'data_export';
        const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
        const fullFilename = `${filename}_${timestamp}.xlsx`;

        // 파일 다운로드
        XLSX.writeFile(wb, fullFilename);

        // 콜백 호출
        if (this.options.onExport) {
            this.options.onExport({
                filename: fullFilename,
                rowCount: exportData.length,
                columnCount: visibleColumns.length,
                selectedOnly: selectedOnly
            });
        }

    }
}

// 전역으로 내보내기
window.DataTableAdvanced = DataTableAdvanced;
