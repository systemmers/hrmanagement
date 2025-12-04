/**
 * DataTable 모듈 인덱스
 * Phase 7: 프론트엔드 리팩토링 - data-table-advanced.js 분할
 *
 * 모든 데이터 테이블 관련 컴포넌트를 하나의 진입점에서 내보냅니다.
 */

export { StorageManager } from './storage-manager.js';
export { ColumnManager } from './column-manager.js';
export { FilterManager } from './filter-manager.js';
export { PaginationManager } from './pagination-manager.js';
export { SelectionManager } from './selection-manager.js';
export { CellRenderer } from './cell-renderer.js';
export { ExcelExporter } from './excel-exporter.js';

/**
 * 모듈화된 DataTable 사용 예시:
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
 * // 각 매니저 인스턴스 생성
 * const storageManager = new StorageManager('myTable');
 * const columnManager = new ColumnManager(columns, storageManager);
 * const filterManager = new FilterManager(columns);
 * const paginationManager = new PaginationManager(10);
 * const selectionManager = new SelectionManager();
 * const cellRenderer = new CellRenderer();
 * const excelExporter = new ExcelExporter();
 *
 * 기존 DataTableAdvanced 클래스는 data-table-advanced.js에서 계속 사용 가능합니다.
 */
