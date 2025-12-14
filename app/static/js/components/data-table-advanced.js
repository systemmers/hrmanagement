/**
 * Advanced Data Table Component
 * Phase 7: 프론트엔드 리팩토링 - 모듈 분할 후 re-export
 *
 * 이 파일은 하위 호환성을 위해 유지됩니다.
 * 새 코드에서는 './data-table/index.js'에서 직접 import하세요.
 *
 * 기능:
 * - 소팅, 검색, 행선택, 컬럼 토글, 컬럼 재정렬
 * - 페이지네이션
 * - 엑셀 내보내기
 * - 컬럼 상태 localStorage 저장
 *
 * 사용법:
 * const table = new DataTableAdvanced('containerId', {
 *   columns: [{ key: 'name', label: '이름', sortable: true, width: '200px' }],
 *   data: [{ id: 1, name: '홍길동' }],
 *   features: { sorting: true, search: true, rowSelection: true, columnToggle: true, columnReorder: true },
 *   pageSize: 10,
 *   storageKey: 'myTable'
 * });
 */

// 분할된 모듈에서 re-export
export {
    // 개별 매니저 모듈
    StorageManager,
    ColumnManager,
    FilterManager,
    PaginationManager,
    SelectionManager,
    CellRenderer,
    ExcelExporter,
    // 통합 클래스
    DataTableAdvanced
} from './data-table/index.js';

// 기존 코드 호환을 위한 기본 내보내기
export { default } from './data-table/index.js';

// 전역으로 내보내기 (비모듈 환경 지원)
// data-table/data-table-advanced.js에서 window.DataTableAdvanced 설정됨
