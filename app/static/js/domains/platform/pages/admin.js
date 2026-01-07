/**
 * admin.js - 관리자 페이지 공통 스크립트
 * Phase 7: ES6 모듈 전환
 *
 * 포함 기능:
 * - 감사 로그 대시보드
 * - 통계 로드 및 표시
 * - 로그 필터링 및 페이지네이션
 */

import { formatDateTime } from '../../shared/utils/formatting.js';
import { get } from '../../shared/utils/api.js';

/**
 * 감사 로그 대시보드 클래스
 */
class AuditDashboard {
    constructor() {
        this.currentPage = 1;
        this.totalLogs = 0;
        this.pageSize = 20;

        // 액션 라벨 매핑
        this.actionLabels = {
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

        // 상태 라벨 매핑
        this.statusLabels = {
            'success': '성공',
            'failed': '실패',
            'pending': '대기'
        };
    }

    /**
     * DOM 요소 텍스트 설정
     */
    setElementText(id, text) {
        const el = document.getElementById(id);
        if (el) el.textContent = text;
    }

    /**
     * 필터 값 가져오기
     */
    getFilterValue(id) {
        const el = document.getElementById(id);
        return el ? el.value : '';
    }

    /**
     * 액션 라벨 반환
     */
    getActionLabel(action) {
        return this.actionLabels[action] || action;
    }

    /**
     * 상태 라벨 반환
     */
    getStatusLabel(status) {
        return this.statusLabels[status] || '성공';
    }

    /**
     * 초기화
     */
    init() {
        this.loadStats();
        this.loadLogs();
        this.setDefaultDates();
    }

    /**
     * 기본 날짜 설정 (최근 30일)
     */
    setDefaultDates() {
        const endDate = new Date();
        const startDate = new Date();
        startDate.setDate(startDate.getDate() - 30);

        const endDateEl = document.getElementById('filterEndDate');
        const startDateEl = document.getElementById('filterStartDate');

        if (endDateEl) endDateEl.value = endDate.toISOString().split('T')[0];
        if (startDateEl) startDateEl.value = startDate.toISOString().split('T')[0];
    }

    /**
     * 통계 로드
     */
    async loadStats() {
        try {
            const data = await get('/api/audit/stats');
            if (data.success) {
                this.setElementText('totalLogs', data.stats.total || 0);
                this.setElementText('viewCount', data.stats.by_action?.view || 0);
                this.setElementText('updateCount', data.stats.by_action?.update || 0);
                this.setElementText('deniedCount', data.stats.by_action?.access_denied || 0);
            }
        } catch (error) {
            console.error('통계 로드 실패:', error);
        }
    }

    /**
     * 로그 로드
     */
    async loadLogs() {
        const params = {
            limit: this.pageSize,
            offset: (this.currentPage - 1) * this.pageSize
        };

        const action = this.getFilterValue('filterAction');
        const resource = this.getFilterValue('filterResource');
        const status = this.getFilterValue('filterStatus');
        const startDate = this.getFilterValue('filterStartDate');
        const endDate = this.getFilterValue('filterEndDate');

        if (action) params.action = action;
        if (resource) params.resource_type = resource;
        if (status) params.status = status;
        if (startDate) params.start_date = startDate;
        if (endDate) params.end_date = endDate;

        try {
            const data = await get('/api/audit/logs', params);
            if (data.success) {
                this.totalLogs = data.total;
                this.setElementText('logCount', `${this.totalLogs}건`);
                this.renderLogs(data.logs);
                this.renderPagination();
            }
        } catch (error) {
            console.error('로그 로드 실패:', error);
            const tbody = document.getElementById('logTableBody');
            if (tbody) {
                tbody.innerHTML = '<tr><td colspan="7" class="table-empty-cell error"><i class="fas fa-exclamation-circle"></i> 로드 실패</td></tr>';
            }
        }
    }

    /**
     * 로그 렌더링
     */
    renderLogs(logs) {
        const tbody = document.getElementById('logTableBody');
        if (!tbody) return;

        if (!logs || logs.length === 0) {
            tbody.innerHTML = '<tr><td colspan="7" class="table-empty-cell"><i class="fas fa-inbox"></i> 로그가 없습니다</td></tr>';
            return;
        }

        tbody.innerHTML = logs.map(log => `
            <tr>
                <td>${formatDateTime(log.created_at)}</td>
                <td>${log.user_id || '-'}</td>
                <td><span class="action-badge ${log.action}">${this.getActionLabel(log.action)}</span></td>
                <td>${log.resource_type || '-'}${log.resource_id ? ` #${log.resource_id}` : ''}</td>
                <td><span class="status-badge ${log.status || 'success'}">${this.getStatusLabel(log.status)}</span></td>
                <td>${log.ip_address || '-'}</td>
                <td><button class="btn btn-sm btn-outline" data-log-id="${log.id}"><i class="fas fa-eye"></i></button></td>
            </tr>
        `).join('');

        // 이벤트 위임으로 상세 보기 버튼 처리
        tbody.querySelectorAll('[data-log-id]').forEach(btn => {
            btn.addEventListener('click', () => this.showLogDetail(btn.dataset.logId));
        });
    }

    /**
     * 페이지네이션 렌더링
     */
    renderPagination() {
        const totalPages = Math.ceil(this.totalLogs / this.pageSize);
        const pagination = document.getElementById('pagination');
        if (!pagination) return;

        if (totalPages <= 1) {
            pagination.innerHTML = '';
            return;
        }

        const startPage = Math.max(1, this.currentPage - 2);
        const endPage = Math.min(totalPages, this.currentPage + 2);

        let html = '';

        // 이전 버튼
        if (this.currentPage > 1) {
            html += `<button class="pagination-btn" data-page="${this.currentPage - 1}"><i class="fas fa-chevron-left"></i></button>`;
        }

        // 페이지 번호
        for (let i = startPage; i <= endPage; i++) {
            const activeClass = i === this.currentPage ? ' active' : '';
            html += `<button class="pagination-btn${activeClass}" data-page="${i}">${i}</button>`;
        }

        // 다음 버튼
        if (this.currentPage < totalPages) {
            html += `<button class="pagination-btn" data-page="${this.currentPage + 1}"><i class="fas fa-chevron-right"></i></button>`;
        }

        pagination.innerHTML = html;

        // 이벤트 위임으로 페이지 버튼 처리
        pagination.querySelectorAll('[data-page]').forEach(btn => {
            btn.addEventListener('click', () => this.goToPage(parseInt(btn.dataset.page)));
        });
    }

    /**
     * 페이지 이동
     */
    goToPage(page) {
        this.currentPage = page;
        this.loadLogs();
    }

    /**
     * 필터 적용
     */
    applyFilters() {
        this.currentPage = 1;
        this.loadLogs();
    }

    /**
     * 새로고침
     */
    refreshData() {
        this.loadStats();
        this.loadLogs();
    }

    /**
     * 내보내기
     */
    exportLogs() {
        alert('CSV 내보내기 기능은 준비 중입니다.');
    }

    /**
     * 로그 상세 보기
     */
    showLogDetail(logId) {
        alert(`로그 ID ${logId}의 상세 정보를 표시합니다.`);
    }
}

// 싱글톤 인스턴스 생성 및 내보내기
const auditDashboard = new AuditDashboard();
export { AuditDashboard, auditDashboard };
export default auditDashboard;

// 페이지 로드 시 자동 초기화 및 이벤트 위임
document.addEventListener('DOMContentLoaded', () => {
    // 감사 대시보드 페이지인 경우에만 초기화
    if (document.querySelector('.audit-dashboard')) {
        auditDashboard.init();

        // 이벤트 위임 - data-action 기반 클릭 핸들러
        document.addEventListener('click', (e) => {
            const target = e.target.closest('[data-action]');
            if (!target) return;

            const action = target.dataset.action;

            switch (action) {
                case 'export-logs':
                    auditDashboard.exportLogs();
                    break;
                case 'refresh-data':
                    auditDashboard.refreshData();
                    break;
                case 'apply-filters':
                    auditDashboard.applyFilters();
                    break;
            }
        });
    }
});
