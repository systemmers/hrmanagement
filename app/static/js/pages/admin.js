/**
 * admin.js - 관리자 페이지 공통 스크립트
 *
 * 포함 기능:
 * - 감사 로그 대시보드
 * - 통계 로드 및 표시
 * - 로그 필터링 및 페이지네이션
 */

// 감사 로그 대시보드 모듈
var AuditDashboard = (function() {
    // 상태 관리
    var currentPage = 1;
    var totalLogs = 0;
    var pageSize = 20;

    // 유틸리티 함수
    function setElementText(id, text) {
        var el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    function getFilterValue(id) {
        var el = document.getElementById(id);
        return el ? el.value : '';
    }

    function formatDate(dateStr) {
        if (!dateStr) return '-';
        var date = new Date(dateStr);
        return date.toLocaleString('ko-KR');
    }

    function getActionLabel(action) {
        var labels = {
            'view': '조회',
            'create': '생성',
            'update': '수정',
            'delete': '삭제',
            'export': '내보내기',
            'sync': '동기화',
            'login': '로그인',
            'logout': '로그아웃',
            'access_denied': '접근 거부'
        };
        return labels[action] || action;
    }

    function getStatusLabel(status) {
        var labels = {
            'success': '성공',
            'failed': '실패',
            'pending': '대기'
        };
        return labels[status] || '성공';
    }

    // 초기화
    function init() {
        loadStats();
        loadLogs();
        setDefaultDates();
    }

    // 기본 날짜 설정 (최근 30일)
    function setDefaultDates() {
        var endDate = new Date();
        var startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);

        var endDateEl = document.getElementById('filterEndDate');
        var startDateEl = document.getElementById('filterStartDate');

        if (endDateEl) endDateEl.value = endDate.toISOString().split('T')[0];
        if (startDateEl) startDateEl.value = startDate.toISOString().split('T')[0];
    }

    // 통계 로드
    function loadStats() {
        fetch('/api/audit/stats')
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    setElementText('totalLogs', data.stats.total || 0);
                    setElementText('viewCount', (data.stats.by_action && data.stats.by_action.view) || 0);
                    setElementText('updateCount', (data.stats.by_action && data.stats.by_action.update) || 0);
                    setElementText('deniedCount', (data.stats.by_action && data.stats.by_action.access_denied) || 0);
                }
            })
            .catch(function(error) {
                console.error('통계 로드 실패:', error);
            });
    }

    // 로그 로드
    function loadLogs() {
        var params = new URLSearchParams({
            limit: pageSize,
            offset: (currentPage - 1) * pageSize
        });

        var action = getFilterValue('filterAction');
        var resource = getFilterValue('filterResource');
        var status = getFilterValue('filterStatus');
        var startDate = getFilterValue('filterStartDate');
        var endDate = getFilterValue('filterEndDate');

        if (action) params.append('action', action);
        if (resource) params.append('resource_type', resource);
        if (status) params.append('status', status);
        if (startDate) params.append('start_date', startDate);
        if (endDate) params.append('end_date', endDate);

        fetch('/api/audit/logs?' + params)
            .then(function(response) { return response.json(); })
            .then(function(data) {
                if (data.success) {
                    totalLogs = data.total;
                    setElementText('logCount', totalLogs + '건');
                    renderLogs(data.logs);
                    renderPagination();
                }
            })
            .catch(function(error) {
                console.error('로그 로드 실패:', error);
                var tbody = document.getElementById('logTableBody');
                if (tbody) {
                    tbody.innerHTML = '<tr><td colspan="7" class="table-empty-cell error"><i class="fas fa-exclamation-circle"></i> 로드 실패</td></tr>';
                }
            });
    }

    // 로그 렌더링
    function renderLogs(logs) {
        var tbody = document.getElementById('logTableBody');
        if (!tbody) return;

        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="table-empty-cell"><i class="fas fa-inbox"></i> 로그가 없습니다</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(function(log) {
            return '<tr>' +
                '<td>' + formatDate(log.created_at) + '</td>' +
                '<td>' + (log.user_id || '-') + '</td>' +
                '<td><span class="action-badge ' + log.action + '">' + getActionLabel(log.action) + '</span></td>' +
                '<td>' + (log.resource_type || '-') + (log.resource_id ? ' #' + log.resource_id : '') + '</td>' +
                '<td><span class="status-badge ' + (log.status || 'success') + '">' + getStatusLabel(log.status) + '</span></td>' +
                '<td>' + (log.ip_address || '-') + '</td>' +
                '<td><button class="btn btn-sm btn-outline" onclick="AuditDashboard.showLogDetail(' + log.id + ')"><i class="fas fa-eye"></i></button></td>' +
            '</tr>';
        }).join('');
    }

    // 페이지네이션 렌더링
    function renderPagination() {
        var totalPages = Math.ceil(totalLogs / pageSize);
        var pagination = document.getElementById('pagination');
        if (!pagination) return;

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        var html = '';
        var startPage = Math.max(1, currentPage - 2);
        var endPage = Math.min(totalPages, currentPage + 2);

        // 이전 버튼
        if (currentPage > 1) {
            html += '<button class="pagination-btn" onclick="AuditDashboard.goToPage(' + (currentPage - 1) + ')"><i class="fas fa-chevron-left"></i></button>';
        }

        // 페이지 번호
        for (var i = startPage; i <= endPage; i++) {
            var activeClass = i === currentPage ? ' active' : '';
            html += '<button class="pagination-btn' + activeClass + '" onclick="AuditDashboard.goToPage(' + i + ')">' + i + '</button>';
        }

        // 다음 버튼
        if (currentPage < totalPages) {
            html += '<button class="pagination-btn" onclick="AuditDashboard.goToPage(' + (currentPage + 1) + ')"><i class="fas fa-chevron-right"></i></button>';
        }

        pagination.innerHTML = html;
    }

    // 페이지 이동
    function goToPage(page) {
        currentPage = page;
        loadLogs();
    }

    // 필터 적용
    function applyFilters() {
        currentPage = 1;
        loadLogs();
    }

    // 새로고침
    function refreshData() {
        loadStats();
        loadLogs();
    }

    // 내보내기
    function exportLogs() {
        alert('CSV 내보내기 기능은 준비 중입니다.');
    }

    // 로그 상세 보기
    function showLogDetail(logId) {
        alert('로그 ID ' + logId + '의 상세 정보를 표시합니다.');
    }

    // 공개 API
    return {
        init: init,
        loadStats: loadStats,
        loadLogs: loadLogs,
        goToPage: goToPage,
        applyFilters: applyFilters,
        refreshData: refreshData,
        exportLogs: exportLogs,
        showLogDetail: showLogDetail
    };
})();

// 전역 함수로 노출 (하위 호환성)
if (typeof window !== 'undefined') {
    window.AuditDashboard = AuditDashboard;

    // 기존 전역 함수 호환성
    window.applyFilters = function() { AuditDashboard.applyFilters(); };
    window.refreshData = function() { AuditDashboard.refreshData(); };
    window.exportLogs = function() { AuditDashboard.exportLogs(); };
    window.goToPage = function(page) { AuditDashboard.goToPage(page); };
    window.showLogDetail = function(id) { AuditDashboard.showLogDetail(id); };
}

// 페이지 로드 시 자동 초기화
document.addEventListener('DOMContentLoaded', function() {
    // 감사 대시보드 페이지인 경우에만 초기화
    if (document.querySelector('.audit-dashboard')) {
        AuditDashboard.init();
    }
});
