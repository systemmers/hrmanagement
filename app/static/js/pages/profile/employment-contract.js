/**
 * 근로계약 및 연봉 섹션 데이터 로더
 *
 * 기능:
 * - loadSalaryHistory: 급여 이력 로드
 * - initEmploymentContract: 전체 초기화
 */

/**
 * 급여 이력 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 */
export function loadSalaryHistory(apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('salaryHistoryContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                let html = '<table class="data-table"><thead><tr>';
                html += '<th>적용일</th><th>연봉</th><th>기본급</th><th>변경사유</th>';
                html += '</tr></thead><tbody>';

                data.data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.effective_date || '-') + '</td>';
                    html += '<td class="text-right">' + (item.annual_salary ? Number(item.annual_salary).toLocaleString() + '원' : '-') + '</td>';
                    html += '<td class="text-right">' + (item.base_salary ? Number(item.base_salary).toLocaleString() + '원' : '-') + '</td>';
                    html += '<td>' + (item.change_reason || '-') + '</td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state"><i class="fas fa-file-signature"></i><p>등록된 연봉 이력이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('salaryHistoryContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><i class="fas fa-exclamation-triangle"></i><p>데이터를 불러오는데 실패했습니다.</p></div>';
            }
        });
}

/**
 * 근로계약 섹션 전체 초기화
 * @param {Object} urls - API URL 객체
 * @param {string} urls.salaryHistory - 급여 이력 API URL
 */
export function initEmploymentContract(urls) {
    if (urls.salaryHistory) loadSalaryHistory(urls.salaryHistory);
}

// 전역 노출 (레거시 호환)
if (typeof window !== 'undefined') {
    window.EmploymentContract = {
        loadSalaryHistory,
        initEmploymentContract
    };
}
