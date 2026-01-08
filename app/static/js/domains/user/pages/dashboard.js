/**
 * Dashboard Page JavaScript
 * 대시보드 페이지 전용 기능
 *
 * Used by:
 * - templates/index.html
 *
 * Dependencies:
 * - SheetJS (xlsx) - Excel 내보내기용 (CDN)
 */

/**
 * 직원 데이터 내보내기 컬럼 설정
 */
const EXPORT_COLUMNS = [
    { key: 'employee_number', label: '사번', width: 100 },
    { key: 'name', label: '이름', width: 100 },
    { key: 'department', label: '부서', width: 100 },
    { key: 'position', label: '직급', width: 80 },
    { key: 'email', label: '이메일', width: 180 },
    { key: 'phone', label: '연락처', width: 120 },
    { key: 'hire_date', label: '입사일', width: 100 },
    { key: 'status', label: '상태', width: 80 }
];

/**
 * 버튼 로딩 상태 설정
 * @param {HTMLElement} btn - 버튼 요소
 * @param {boolean} isLoading - 로딩 상태
 * @param {string} loadingText - 로딩 중 텍스트
 * @param {string} defaultText - 기본 텍스트
 * @param {string} icon - 아이콘 클래스
 */
function setButtonLoading(btn, isLoading, loadingText = '처리 중...', defaultText = '버튼', icon = 'fa-download') {
    btn.disabled = isLoading;
    if (isLoading) {
        btn.innerHTML = `<i class="fas fa-spinner fa-spin"></i> <span>${loadingText}</span>`;
    } else {
        btn.innerHTML = `<i class="fas ${icon}"></i> <span>${defaultText}</span>`;
    }
}

/**
 * 직원 목록 API에서 데이터 가져오기
 * @returns {Promise<Array>} 직원 목록
 */
async function fetchEmployees() {
    const response = await fetch('/api/employees');
    const result = await response.json();

    if (!result.success || !result.employees || result.employees.length === 0) {
        throw new Error('내보낼 직원 데이터가 없습니다.');
    }

    return result.employees;
}

/**
 * 직원 데이터를 Excel 파일로 내보내기
 * @param {Array} employees - 직원 데이터 배열
 * @param {string} sheetName - 시트 이름
 * @returns {string} 생성된 파일명
 */
function exportToExcel(employees, sheetName = '직원현황') {
    // XLSX 라이브러리 확인
    if (typeof XLSX === 'undefined') {
        throw new Error('Excel 내보내기 라이브러리가 로드되지 않았습니다.');
    }

    // 헤더 행 생성
    const headers = EXPORT_COLUMNS.map(col => col.label);

    // 데이터 행 생성
    const rows = employees.map(emp =>
        EXPORT_COLUMNS.map(col => emp[col.key] || '')
    );

    // 워크시트 데이터 구성
    const wsData = [headers, ...rows];

    // 워크시트 생성
    const ws = XLSX.utils.aoa_to_sheet(wsData);

    // 컬럼 너비 설정
    ws['!cols'] = EXPORT_COLUMNS.map(col => ({ wch: col.width / 8 || 15 }));

    // 워크북 생성
    const wb = XLSX.utils.book_new();
    XLSX.utils.book_append_sheet(wb, ws, sheetName);

    // 파일명 생성 (YYYYMMDD 형식)
    const timestamp = new Date().toISOString().slice(0, 10).replace(/-/g, '');
    const filename = `${sheetName}_${timestamp}.xlsx`;

    // 파일 다운로드
    XLSX.writeFile(wb, filename);

    return filename;
}

/**
 * 내보내기 버튼 클릭 핸들러
 * @param {Event} event - 클릭 이벤트
 */
async function handleExportClick(event) {
    const btn = event.currentTarget;

    setButtonLoading(btn, true, '내보내기 중...', '내보내기', 'fa-download');

    try {
        const employees = await fetchEmployees();
        const filename = exportToExcel(employees);
        alert(`${employees.length}명의 직원 정보가 내보내기되었습니다.`);
    } catch (error) {
        console.error('Export error:', error);
        alert(error.message || '내보내기 중 오류가 발생했습니다.');
    } finally {
        setButtonLoading(btn, false, '내보내기 중...', '내보내기', 'fa-download');
    }
}

/**
 * 대시보드 내보내기 기능 초기화
 */
function initDashboardExport() {
    const exportBtn = document.querySelector('[data-action="print-page"]');
    if (exportBtn) {
        exportBtn.addEventListener('click', handleExportClick);
    }
}

/**
 * 대시보드 초기화
 */
function initDashboard() {
    initDashboardExport();
}

// DOM 로드 완료 시 초기화
document.addEventListener('DOMContentLoaded', initDashboard);

// 모듈 내보내기 (ES Module 환경용)
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        initDashboard,
        initDashboardExport,
        handleExportClick,
        exportToExcel,
        fetchEmployees,
        setButtonLoading,
        EXPORT_COLUMNS
    };
}

// 전역 함수 노출 (비모듈 환경용)
window.DashboardModule = {
    initDashboard,
    initDashboardExport,
    handleExportClick,
    exportToExcel,
    fetchEmployees
};
