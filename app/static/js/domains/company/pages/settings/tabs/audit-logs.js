/**
 * 감사 로그 탭 모듈
 *
 * 법인 설정 페이지의 감사 로그 탭 기능
 */

import { showToast } from '../../../../../shared/components/toast.js';
import { AUDIT_ACTION_LABELS, AUDIT_STATUS_LABELS } from '../shared/constants.js';

/**
 * 감사 로그 상태
 */
const auditState = {
    currentPage: 1,
    perPage: 20,
    total: 0,
    filters: {
        action: '',
        resourceType: '',
        status: '',
        startDate: '',
        endDate: ''
    }
};

/**
 * HTML 이스케이프 (SSOT: window.HRFormatters.escapeHtml)
 */
function escapeHtml(str) {
    return window.HRFormatters?.escapeHtml?.(str) || '';
}

/**
 * 감사 로그 데이터 로드
 */
export async function loadAuditData() {
    try {
        // 통계와 로그를 병렬 로드
        await Promise.all([
            loadAuditStats(),
            loadAuditLogs()
        ]);
    } catch (error) {
        console.error('감사 로그 데이터 로드 실패:', error);
        showToast('감사 로그를 불러오는데 실패했습니다', 'error');
    }
}

/**
 * 감사 로그 통계 로드
 */
async function loadAuditStats() {
    try {
        const response = await fetch('/api/audit/stats/company');
        const result = await response.json();

        if (result.success && result.data) {
            const stats = result.data.stats || {};

            // 통계 업데이트
            const totalEl = document.getElementById('auditTotalLogs');
            const viewEl = document.getElementById('auditViewCount');
            const updateEl = document.getElementById('auditUpdateCount');
            const deniedEl = document.getElementById('auditDeniedCount');

            if (totalEl) totalEl.textContent = stats.total || 0;
            if (viewEl) viewEl.textContent = stats.by_action?.view || 0;
            if (updateEl) updateEl.textContent = stats.by_action?.update || 0;
            if (deniedEl) deniedEl.textContent = stats.by_action?.access_denied || 0;
        }
    } catch (error) {
        console.error('감사 통계 로드 실패:', error);
    }
}

/**
 * 감사 로그 목록 로드
 */
async function loadAuditLogs() {
    const { filters, currentPage, perPage } = auditState;
    const offset = (currentPage - 1) * perPage;

    // URL 파라미터 구성
    const params = new URLSearchParams();
    params.set('limit', perPage);
    params.set('offset', offset);

    if (filters.action) params.set('action', filters.action);
    if (filters.resourceType) params.set('resource_type', filters.resourceType);
    if (filters.status) params.set('status', filters.status);
    if (filters.startDate) params.set('start_date', filters.startDate);
    if (filters.endDate) params.set('end_date', filters.endDate);

    try {
        const response = await fetch(`/api/audit/logs?${params.toString()}`);
        const result = await response.json();

        if (result.success && result.data) {
            auditState.total = result.data.total || 0;
            renderAuditLogs(result.data.logs || []);
            renderAuditPagination();

            // 결과 건수 업데이트
            const countEl = document.querySelector('#tab-audit .audit-log-count');
            if (countEl) {
                countEl.textContent = `${auditState.total}건`;
            }
        }
    } catch (error) {
        console.error('감사 로그 로드 실패:', error);
        const tbody = document.getElementById('auditLogTableBody');
        if (tbody) {
            tbody.innerHTML = `
                <tr>
                    <td colspan="7" class="audit-empty">
                        <i class="fas fa-exclamation-circle"></i>
                        <p>로그를 불러오는데 실패했습니다</p>
                    </td>
                </tr>
            `;
        }
    }
}

/**
 * 감사 로그 테이블 렌더링
 * @param {Array} logs - 로그 데이터
 */
function renderAuditLogs(logs) {
    const tbody = document.getElementById('auditLogTableBody');
    if (!tbody) return;

    if (!logs || logs.length === 0) {
        tbody.innerHTML = `
            <tr>
                <td colspan="7" class="audit-empty">
                    <i class="fas fa-clipboard-list"></i>
                    <p>조회된 로그가 없습니다</p>
                </td>
            </tr>
        `;
        return;
    }

    tbody.innerHTML = logs.map(log => {
        const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString('ko-KR') : '-';
        const actionLabel = AUDIT_ACTION_LABELS[log.action] || log.action;
        const statusLabel = AUDIT_STATUS_LABELS[log.status] || log.status;
        const actionClass = getActionBadgeClass(log.action);
        const statusClass = getStatusBadgeClass(log.status);

        return `
            <tr data-log-id="${log.id}">
                <td class="audit-log-time">${timestamp}</td>
                <td class="audit-log-user">${escapeHtml(log.username || '-')}</td>
                <td class="audit-log-action">
                    <span class="audit-action-badge audit-action-badge--${actionClass}">${actionLabel}</span>
                </td>
                <td class="audit-log-resource">${escapeHtml(log.resource_type || '-')}</td>
                <td class="audit-log-status">
                    <span class="audit-status-badge audit-status-badge--${statusClass}">${statusLabel}</span>
                </td>
                <td class="audit-log-ip">${escapeHtml(log.ip_address || '-')}</td>
                <td class="audit-log-actions">
                    <button class="btn-icon" data-action="audit-detail" data-log='${JSON.stringify(log).replace(/'/g, "\\'")}' title="상세 보기">
                        <i class="fas fa-eye"></i>
                    </button>
                </td>
            </tr>
        `;
    }).join('');
}

/**
 * 액션 배지 클래스 반환
 * @param {string} action - 액션 유형
 * @returns {string} CSS 클래스
 */
function getActionBadgeClass(action) {
    const classMap = {
        'view': 'view',
        'create': 'create',
        'update': 'update',
        'delete': 'delete',
        'export': 'export',
        'sync': 'sync',
        'login': 'login',
        'logout': 'logout',
        'access_denied': 'denied'
    };
    return classMap[action] || 'default';
}

/**
 * 상태 배지 클래스 반환
 * @param {string} status - 상태
 * @returns {string} CSS 클래스
 */
function getStatusBadgeClass(status) {
    const classMap = {
        'success': 'success',
        'failure': 'failure',
        'denied': 'denied'
    };
    return classMap[status] || 'default';
}

/**
 * 감사 로그 페이지네이션 렌더링
 */
function renderAuditPagination() {
    const container = document.getElementById('auditPagination');
    if (!container) return;

    const { total, currentPage, perPage } = auditState;
    const totalPages = Math.ceil(total / perPage);

    if (totalPages <= 1) {
        container.innerHTML = '';
        return;
    }

    let html = '';

    // 이전 페이지 버튼
    html += `
        <button class="pagination-btn" data-action="audit-page" data-page="${currentPage - 1}"
                ${currentPage === 1 ? 'disabled' : ''}>
            <i class="fas fa-chevron-left"></i>
        </button>
    `;

    // 페이지 번호
    const maxVisiblePages = 5;
    let startPage = Math.max(1, currentPage - Math.floor(maxVisiblePages / 2));
    let endPage = Math.min(totalPages, startPage + maxVisiblePages - 1);

    if (endPage - startPage < maxVisiblePages - 1) {
        startPage = Math.max(1, endPage - maxVisiblePages + 1);
    }

    if (startPage > 1) {
        html += `<button class="pagination-btn" data-action="audit-page" data-page="1">1</button>`;
        if (startPage > 2) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
    }

    for (let i = startPage; i <= endPage; i++) {
        html += `
            <button class="pagination-btn ${i === currentPage ? 'active' : ''}"
                    data-action="audit-page" data-page="${i}">${i}</button>
        `;
    }

    if (endPage < totalPages) {
        if (endPage < totalPages - 1) {
            html += `<span class="pagination-ellipsis">...</span>`;
        }
        html += `<button class="pagination-btn" data-action="audit-page" data-page="${totalPages}">${totalPages}</button>`;
    }

    // 다음 페이지 버튼
    html += `
        <button class="pagination-btn" data-action="audit-page" data-page="${currentPage + 1}"
                ${currentPage === totalPages ? 'disabled' : ''}>
            <i class="fas fa-chevron-right"></i>
        </button>
    `;

    container.innerHTML = html;
}

/**
 * 감사 로그 상세 모달 표시
 * @param {Object} log - 로그 데이터
 */
function showAuditDetail(log) {
    const modal = document.getElementById('auditDetailModal');
    if (!modal) return;

    const timestamp = log.timestamp ? new Date(log.timestamp).toLocaleString('ko-KR') : '-';
    const actionLabel = AUDIT_ACTION_LABELS[log.action] || log.action;
    const statusLabel = AUDIT_STATUS_LABELS[log.status] || log.status;

    // 모달 내용 채우기
    const setTextContent = (id, value) => {
        const el = document.getElementById(id);
        if (el) el.textContent = value || '-';
    };

    setTextContent('auditDetailTimestamp', timestamp);
    setTextContent('auditDetailUser', log.username);
    setTextContent('auditDetailAction', actionLabel);
    setTextContent('auditDetailResource', `${log.resource_type || '-'} ${log.resource_id ? `#${log.resource_id}` : ''}`);
    setTextContent('auditDetailStatus', statusLabel);
    setTextContent('auditDetailIp', log.ip_address);
    setTextContent('auditDetailUserAgent', log.user_agent);

    // 상세 데이터
    const detailsEl = document.getElementById('auditDetailData');
    if (detailsEl) {
        if (log.details) {
            try {
                const details = typeof log.details === 'string' ? JSON.parse(log.details) : log.details;
                detailsEl.textContent = JSON.stringify(details, null, 2);
            } catch {
                detailsEl.textContent = log.details;
            }
        } else {
            detailsEl.textContent = '-';
        }
    }

    modal.classList.add('show');
}

/**
 * 감사 로그 필터 초기화
 */
function resetAuditFilters() {
    auditState.filters = {
        action: '',
        resourceType: '',
        status: '',
        startDate: '',
        endDate: ''
    };
    auditState.currentPage = 1;

    // 폼 초기화
    const filterElements = {
        'auditFilterAction': '',
        'auditFilterResource': '',
        'auditFilterStatus': '',
        'auditFilterStartDate': '',
        'auditFilterEndDate': ''
    };

    Object.entries(filterElements).forEach(([id, value]) => {
        const el = document.getElementById(id);
        if (el) el.value = value;
    });

    // 리로드
    loadAuditLogs();
}

/**
 * 감사 로그 필터 적용
 */
function applyAuditFilters() {
    auditState.filters = {
        action: document.getElementById('auditFilterAction')?.value || '',
        resourceType: document.getElementById('auditFilterResource')?.value || '',
        status: document.getElementById('auditFilterStatus')?.value || '',
        startDate: document.getElementById('auditFilterStartDate')?.value || '',
        endDate: document.getElementById('auditFilterEndDate')?.value || ''
    };
    auditState.currentPage = 1;

    loadAuditLogs();
}

/**
 * 감사 탭 이벤트 핸들러 초기화
 */
export function initAuditHandlers() {
    const container = document.getElementById('tab-audit');
    if (!container || container.dataset.handlersInitialized) return;

    container.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'audit-search':
                applyAuditFilters();
                break;
            case 'audit-reset':
                resetAuditFilters();
                break;
            case 'audit-detail':
                try {
                    const logData = JSON.parse(target.dataset.log);
                    showAuditDetail(logData);
                } catch (err) {
                    console.error('로그 데이터 파싱 실패:', err);
                }
                break;
            case 'audit-page':
                const page = parseInt(target.dataset.page);
                if (page && page !== auditState.currentPage) {
                    auditState.currentPage = page;
                    loadAuditLogs();
                }
                break;
            case 'close-audit-modal':
                document.getElementById('auditDetailModal')?.classList.remove('show');
                break;
        }
    });

    // Enter 키로 검색
    container.querySelectorAll('.audit-filter-section input, .audit-filter-section select').forEach(el => {
        el.addEventListener('keydown', (e) => {
            if (e.key === 'Enter') {
                applyAuditFilters();
            }
        });
    });

    container.dataset.handlersInitialized = 'true';
}

/**
 * 감사 로그 탭 초기화 엔트리 포인트
 */
export async function initAuditLogsTab() {
    initAuditHandlers();
    await loadAuditData();
}
