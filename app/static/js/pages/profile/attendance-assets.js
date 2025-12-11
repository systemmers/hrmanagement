/**
 * 근태 및 비품 섹션 데이터 로더
 *
 * 기능:
 * - loadAttendances: 근태 현황 로드
 * - loadAssets: 비품 현황 로드
 * - initAttendanceAssets: 전체 초기화
 */

/**
 * 근태 현황 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 * @param {number} limit - 표시할 최대 건수 (기본: 10)
 */
export function loadAttendances(apiUrl, limit = 10) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('attendanceContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                const recentData = data.data.slice(0, limit);

                let html = '<table class="data-table"><thead><tr>';
                html += '<th>날짜</th><th>출근</th><th>퇴근</th><th>근무시간</th><th>상태</th>';
                html += '</tr></thead><tbody>';

                recentData.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.date || '-') + '</td>';
                    html += '<td>' + (item.check_in || '-') + '</td>';
                    html += '<td>' + (item.check_out || '-') + '</td>';
                    html += '<td>' + (item.work_hours || '-') + '</td>';
                    html += '<td><span class="status-badge status-badge--' + (item.status || 'default') + '">' + (item.status || '-') + '</span></td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state empty-state--small"><p>근태 기록이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('attendanceContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><p>데이터 로드 실패</p></div>';
            }
        });
}

/**
 * 비품 현황 로드
 * @param {string} apiUrl - API 엔드포인트 URL
 */
export function loadAssets(apiUrl) {
    fetch(apiUrl)
        .then(response => response.json())
        .then(data => {
            const container = document.getElementById('assetContainer');
            if (!container) return;

            if (data.success && data.data && data.data.length > 0) {
                let html = '<table class="data-table"><thead><tr>';
                html += '<th>품목명</th><th>관리번호</th><th>지급일</th><th>상태</th>';
                html += '</tr></thead><tbody>';

                data.data.forEach(item => {
                    html += '<tr>';
                    html += '<td>' + (item.asset_name || item.name || '-') + '</td>';
                    html += '<td>' + (item.asset_number || '-') + '</td>';
                    html += '<td>' + (item.issue_date || '-') + '</td>';
                    html += '<td><span class="status-badge status-badge--' + (item.status || 'default') + '">' + (item.status || '-') + '</span></td>';
                    html += '</tr>';
                });

                html += '</tbody></table>';
                container.innerHTML = html;
            } else {
                container.innerHTML = '<div class="empty-state empty-state--small"><p>지급된 비품이 없습니다.</p></div>';
            }
        })
        .catch(() => {
            const container = document.getElementById('assetContainer');
            if (container) {
                container.innerHTML = '<div class="error-state"><p>데이터 로드 실패</p></div>';
            }
        });
}

/**
 * 근태 및 비품 섹션 전체 초기화
 * @param {Object} urls - API URL 객체
 * @param {string} urls.attendances - 근태 현황 API URL
 * @param {string} urls.assets - 비품 현황 API URL
 */
export function initAttendanceAssets(urls) {
    if (urls.attendances) loadAttendances(urls.attendances);
    if (urls.assets) loadAssets(urls.assets);
}

// 전역 노출 (레거시 호환)
if (typeof window !== 'undefined') {
    window.AttendanceAssets = {
        loadAttendances,
        loadAssets,
        initAttendanceAssets
    };
}
