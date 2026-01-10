/**
 * 법인 설정 페이지 컨트롤러
 */

import { ClassificationApi, SettingsApi, VisibilityApi, DocumentsApi } from '../services/settings-api.js';
import { Accordion } from '../../../shared/components/accordion.js';
import { MAX_FILE_SIZE, MAX_FILE_SIZE_MB, FILE_UPLOAD_MESSAGES } from '../../../shared/constants/file-upload-constants.js';

const state = {
    activeTab: 'basic',
    loadedTabs: new Set(['basic']),
    treeExpanded: false,  // 조직 트리 펼침 상태
    // 감사 로그 상태
    audit: {
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
    }
};

// 감사 로그 상수
const AUDIT_ACTION_LABELS = {
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

const AUDIT_STATUS_LABELS = {
    'success': '성공',
    'failure': '실패',
    'denied': '거부'
};

const TOAST_COLORS = {
    success: '#10b981',
    error: '#ef4444',
    warning: '#f59e0b',
    info: '#3b82f6'
};

/**
 * 콘텐츠 영역에 에러 메시지 표시
 * @param {Element} contentEl - 콘텐츠 엘리먼트
 */
function showContentError(contentEl) {
    if (!contentEl) return;
    contentEl.innerHTML = `
        <div class="category-empty">
            <i class="fas fa-exclamation-circle"></i>
            <p>데이터를 불러오는데 실패했습니다</p>
            <button class="btn btn-sm btn-secondary" onclick="location.reload()">다시 시도</button>
        </div>
    `;
}

function initTabs() {
    const hash = window.location.hash.replace('#', '');
    if (hash && document.getElementById(`tab-${hash}`)) {
        state.activeTab = hash;
    }

    document.querySelectorAll('.tab-btn').forEach(btn => {
        btn.addEventListener('click', () => switchTab(btn.dataset.tab));
    });

    switchTab(state.activeTab);
}

function switchTab(tabId) {
    document.querySelectorAll('.tab-btn').forEach(btn => {
        const isActive = btn.dataset.tab === tabId;
        btn.classList.toggle('active', isActive);
        btn.setAttribute('aria-selected', isActive);
    });

    document.querySelectorAll('.tab-panel').forEach(panel => {
        panel.classList.toggle('active', panel.id === `tab-${tabId}`);
    });

    state.activeTab = tabId;
    window.location.hash = tabId;

    if (!state.loadedTabs.has(tabId)) {
        loadTabData(tabId);
    }
}

/**
 * 탭 데이터 로드
 * @param {string} tabId - 탭 ID
 */
async function loadTabData(tabId) {
    switch (tabId) {
        case 'org-management':
            await loadOrgManagementData();
            break;
        case 'organization':
            await loadOrganizationData();
            break;
        case 'patterns':
            await loadPatternsData();
            break;
        case 'employment':
            await loadEmploymentData();
            break;
        case 'documents':
            await loadDocumentsData();
            break;
        case 'visibility':
            await loadVisibilityData();
            break;
        case 'audit':
            await loadAuditData();
            break;
    }
    state.loadedTabs.add(tabId);
}

// ========================================
// 조직 관리 탭 관련 변수 및 함수
// ========================================
let selectedOrgId = null;
let deleteOrgId = null;

/**
 * 조직 관리 탭 데이터 로드
 */
async function loadOrgManagementData() {
    const content = document.getElementById('org-management-content');

    try {
        // 조직 트리, 통계, 조직유형 설정 데이터 병렬 로드
        const [treeResponse, statsResponse, typesResponse] = await Promise.all([
            fetch('/admin/api/organizations?format=tree'),
            fetch('/admin/api/organizations/stats'),
            fetch('/api/corporate/organization-types')
        ]);

        const treeResult = await treeResponse.json();
        const statsResult = await statsResponse.json();
        const typesResult = await typesResponse.json();

        // 조직유형 설정 렌더링
        if (typesResult.success) {
            renderOrgTypeSettings(typesResult.data);
        }

        // 통계 업데이트
        if (statsResult.success) {
            updateOrgStats(statsResult.data);
        }

        // 트리 렌더링
        if (treeResult.success) {
            renderOrgTree(treeResult.data);
            // 상위 조직 선택 옵션 업데이트
            await updateParentOrgOptions();
        }

        // 조직관리 이벤트 핸들러 초기화
        initOrgManagementHandlers();
    } catch (error) {
        console.error('조직 관리 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 조직 통계 업데이트 (동적 렌더링)
 */
function updateOrgStats(stats) {
    const container = document.getElementById('org-stats-row');
    if (!container) return;

    // 전체 조직 통계 업데이트
    const totalEl = document.getElementById('stat-total');
    if (totalEl) {
        totalEl.textContent = stats.total || 0;
    }

    // 기존 동적 카드 제거 (전체 조직 카드 유지)
    const dynamicCards = container.querySelectorAll('.stat-card.dynamic');
    dynamicCards.forEach(card => card.remove());

    // 활성화된 조직유형별 통계 카드 동적 생성
    if (stats.active_types && stats.active_types.length > 0) {
        stats.active_types.forEach(type => {
            const card = createStatCard(type.label, type.count, type.icon || 'fa-folder');
            container.appendChild(card);
        });
    }
}

/**
 * 통계 카드 HTML 요소 생성
 */
function createStatCard(label, count, icon) {
    const card = document.createElement('div');
    card.className = 'stat-card dynamic';
    card.innerHTML = `
        <div class="stat-icon"><i class="fas ${icon}"></i></div>
        <div class="stat-content">
            <div class="stat-value">${count}</div>
            <div class="stat-label">${escapeHtml(label)}</div>
        </div>
    `;
    return card;
}

// ========================================
// 조직유형 설정 관련 함수
// ========================================

/**
 * 조직유형 설정 렌더링
 */
function renderOrgTypeSettings(types) {
    const container = document.getElementById('orgTypeList');
    if (!container) return;

    if (!types || types.length === 0) {
        container.innerHTML = '<p class="text-muted">조직유형이 없습니다.</p>';
        return;
    }

    container.innerHTML = `
        <div class="org-type-table" id="orgTypeTable">
            <div class="org-type-header">
                <span class="org-type-col org-type-col--drag"></span>
                <span class="org-type-col org-type-col--order">순번</span>
                <span class="org-type-col org-type-col--icon">아이콘</span>
                <span class="org-type-col org-type-col--label-ko">한글명</span>
                <span class="org-type-col org-type-col--label-en">영문명</span>
                <span class="org-type-col org-type-col--delete"></span>
            </div>
            ${types.map((type, index) => renderOrgTypeRow(type, index)).join('')}
        </div>
        <div class="org-type-add-row">
            <button type="button" class="btn btn--sm btn--secondary" data-action="add-org-type">
                <i class="fas fa-plus"></i> 조직유형 추가
            </button>
        </div>
    `;

    // 드래그 앤 드롭 초기화
    initOrgTypeSortable();
}

/**
 * 조직유형 행 렌더링
 */
function renderOrgTypeRow(type, index) {
    return `
        <div class="org-type-row" data-id="${type.id}" data-sort-order="${type.sort_order}" draggable="true">
            <span class="org-type-col org-type-col--drag">
                <i class="fas fa-grip-vertical drag-handle" title="드래그하여 순서 변경"></i>
            </span>
            <span class="org-type-col org-type-col--order">${index + 1}</span>
            <span class="org-type-col org-type-col--icon">
                <button type="button" class="btn btn--icon btn--sm" data-action="select-icon" data-id="${type.id}" title="아이콘 선택">
                    <i class="fas ${type.icon || 'fa-folder'}"></i>
                </button>
            </span>
            <span class="org-type-col org-type-col--label-ko">
                <input type="text" class="form__input form__input--sm org-type-label-input"
                       value="${escapeHtml(type.type_label_ko || type.type_label || '')}"
                       data-id="${type.id}"
                       data-field="type_label_ko"
                       data-original="${escapeHtml(type.type_label_ko || type.type_label || '')}"
                       placeholder="한글명">
            </span>
            <span class="org-type-col org-type-col--label-en">
                <input type="text" class="form__input form__input--sm org-type-label-input"
                       value="${escapeHtml(type.type_label_en || '')}"
                       data-id="${type.id}"
                       data-field="type_label_en"
                       data-original="${escapeHtml(type.type_label_en || '')}"
                       placeholder="English">
            </span>
            <span class="org-type-col org-type-col--delete">
                <button type="button" class="btn btn--icon btn--sm btn--ghost"
                        data-action="delete-org-type" data-id="${type.id}"
                        data-type-code="${escapeHtml(type.type_code)}" title="삭제">
                    <i class="fas fa-trash"></i>
                </button>
            </span>
        </div>
    `;
}

/**
 * 조직유형 순서 드래그 앤 드롭 초기화
 */
function initOrgTypeSortable() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    let draggedItem = null;

    table.addEventListener('dragstart', (e) => {
        const row = e.target.closest('.org-type-row');
        if (row) {
            draggedItem = row;
            row.classList.add('dragging');
            e.dataTransfer.effectAllowed = 'move';
        }
    });

    table.addEventListener('dragend', (e) => {
        const row = e.target.closest('.org-type-row');
        if (row) {
            row.classList.remove('dragging');
            draggedItem = null;
            // 순서 저장
            saveOrgTypeOrder();
        }
    });

    table.addEventListener('dragover', (e) => {
        e.preventDefault();
        const row = e.target.closest('.org-type-row');
        if (row && row !== draggedItem) {
            const rect = row.getBoundingClientRect();
            const midY = rect.top + rect.height / 2;
            if (e.clientY < midY) {
                row.parentNode.insertBefore(draggedItem, row);
            } else {
                row.parentNode.insertBefore(draggedItem, row.nextSibling);
            }
        }
    });
}

/**
 * 조직유형 순서 저장
 */
async function saveOrgTypeOrder() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    const rows = table.querySelectorAll('.org-type-row');
    const typeIds = Array.from(rows).map(row => parseInt(row.dataset.id));

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ type_ids: typeIds })
        });

        const result = await response.json();

        if (result.success) {
            showToast('순서가 저장되었습니다', 'success');
            // 순번 UI 즉시 업데이트
            updateOrgTypeOrderNumbers();
        } else {
            showToast(result.error || '순서 저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 순서 저장 오류:', error);
        showToast('순서 저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 순번 UI 업데이트
 */
function updateOrgTypeOrderNumbers() {
    const table = document.getElementById('orgTypeTable');
    if (!table) return;

    const rows = table.querySelectorAll('.org-type-row');
    rows.forEach((row, index) => {
        const orderCol = row.querySelector('.org-type-col--order');
        if (orderCol) {
            orderCol.textContent = index + 1;
        }
    });
}

/**
 * 조직유형 라벨 저장 (한글명/영문명)
 * @param {number} configId - 설정 ID
 * @param {string} field - 필드명 (type_label_ko 또는 type_label_en)
 * @param {string} value - 새 값
 */
async function saveOrgTypeLabel(configId, field, value) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    const data = {};
    data[field] = value;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            showToast('저장되었습니다', 'success');
            // 입력 필드의 original 값 업데이트
            const input = document.querySelector(`.org-type-label-input[data-id="${configId}"][data-field="${field}"]`);
            if (input) {
                input.dataset.original = value;
            }
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 라벨 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 삭제
 * @param {number} configId - 설정 ID
 * @param {string} typeCode - 유형 코드
 */
async function deleteOrgType(configId, typeCode) {
    const confirmed = confirm(`이 조직유형을 삭제하시겠습니까?\n\n사용 중인 조직이 있으면 삭제할 수 없습니다.`);
    if (!confirmed) return;

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'DELETE',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            showToast('조직유형이 삭제되었습니다', 'success');
            // 해당 행 제거 및 순번 재정렬
            const row = document.querySelector(`.org-type-row[data-id="${configId}"]`);
            if (row) {
                row.remove();
                updateOrgTypeOrderNumbers();
            }
        } else {
            showToast(result.error || '삭제에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 삭제 오류:', error);
        showToast('삭제 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 추가
 */
async function addOrgType() {
    const labelKo = prompt('새 조직유형의 한글명을 입력하세요:');
    if (!labelKo || !labelKo.trim()) return;

    const labelEn = prompt('영문명을 입력하세요 (선택사항):');

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                type_label_ko: labelKo.trim(),
                type_label_en: labelEn ? labelEn.trim() : null,
                icon: 'fa-folder'
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast('조직유형이 추가되었습니다', 'success');
            // 새 행 추가
            const table = document.getElementById('orgTypeTable');
            if (table && result.data) {
                const rowCount = table.querySelectorAll('.org-type-row').length;
                const newRowHtml = renderOrgTypeRow(result.data, rowCount);
                table.insertAdjacentHTML('beforeend', newRowHtml);
            }
        } else {
            showToast(result.error || '추가에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 추가 오류:', error);
        showToast('추가 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 아이콘 저장
 * @param {number} configId - 설정 ID
 * @param {string} icon - 아이콘 클래스
 */
async function saveOrgTypeIcon(configId, icon) {
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/api/corporate/organization-types/${configId}`, {
            method: 'PUT',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({ icon: icon })
        });

        const result = await response.json();

        if (result.success) {
            showToast('아이콘이 저장되었습니다', 'success');
            // 아이콘 버튼 업데이트
            const btn = document.querySelector(`.org-type-row[data-id="${configId}"] [data-action="select-icon"] i`);
            if (btn) {
                btn.className = `fas ${icon}`;
            }
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 아이콘 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 아이콘 선택 모달 표시
 * @param {number} configId - 설정 ID
 */
function showIconSelector(configId) {
    const icons = [
        'fa-building', 'fa-layer-group', 'fa-users', 'fa-user-friends',
        'fa-sitemap', 'fa-door-open', 'fa-puzzle-piece', 'fa-folder',
        'fa-briefcase', 'fa-cog', 'fa-chart-line', 'fa-code-branch',
        'fa-cube', 'fa-cubes', 'fa-database', 'fa-globe',
        'fa-landmark', 'fa-network-wired', 'fa-project-diagram', 'fa-server'
    ];

    // 기존 모달 제거
    const existingModal = document.getElementById('iconSelectorModal');
    if (existingModal) {
        existingModal.remove();
    }

    const modalHtml = `
        <div class="modal show" id="iconSelectorModal">
            <div class="modal__content modal__content--sm">
                <div class="modal__header">
                    <h3 class="modal__title">아이콘 선택</h3>
                    <button class="modal__close" data-action="close-icon-modal">&times;</button>
                </div>
                <div class="modal__body">
                    <div class="icon-grid">
                        ${icons.map(icon => `
                            <button type="button" class="icon-grid__item" data-icon="${icon}" data-config-id="${configId}">
                                <i class="fas ${icon}"></i>
                            </button>
                        `).join('')}
                    </div>
                </div>
            </div>
        </div>
    `;

    document.body.insertAdjacentHTML('beforeend', modalHtml);

    const modal = document.getElementById('iconSelectorModal');

    // 이벤트 리스너
    modal.addEventListener('click', (e) => {
        const closeBtn = e.target.closest('[data-action="close-icon-modal"]');
        if (closeBtn || e.target === modal) {
            modal.remove();
            return;
        }

        const iconBtn = e.target.closest('.icon-grid__item');
        if (iconBtn) {
            const icon = iconBtn.dataset.icon;
            const cId = parseInt(iconBtn.dataset.configId);
            saveOrgTypeIcon(cId, icon);
            modal.remove();
        }
    });
}

/**
 * 조직유형 초기화
 */
async function resetOrgTypes() {
    if (!confirm('조직유형 설정을 기본값으로 초기화하시겠습니까?')) {
        return;
    }

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/api/corporate/organization-types/reset', {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            showToast('기본값으로 초기화되었습니다', 'success');
            // 데이터 새로고침
            state.loadedTabs.delete('org-management');
            await loadOrgManagementData();
        } else {
            showToast(result.error || '초기화에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직유형 초기화 오류:', error);
        showToast('초기화 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직 트리 렌더링
 */
function renderOrgTree(tree) {
    const treeContainer = document.getElementById('orgTree');
    if (!treeContainer) return;

    if (!tree || tree.length === 0) {
        treeContainer.innerHTML = `
            <div class="empty-tree">
                <i class="fas fa-folder-open"></i>
                <p>등록된 조직이 없습니다.</p>
                <button class="btn btn-primary" data-action="add-org">
                    첫 번째 조직 추가
                </button>
            </div>
        `;
        return;
    }

    treeContainer.innerHTML = tree.map(org => renderTreeNode(org, null)).join('');

    // 첫 번째 레벨 펼치기
    document.querySelectorAll('#orgTree > .tree-node > .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('#orgTree > .tree-node > .tree-node-content .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });

    // 드래그앤드롭 초기화
    initOrgTreeDragDrop();
}

// 트리 드래그 상태
let treeDraggedNode = null;
let treeDraggedParentId = null;

/**
 * 조직 트리 드래그앤드롭 초기화
 */
function initOrgTreeDragDrop() {
    const treeContainer = document.getElementById('orgTree');
    if (!treeContainer || treeContainer.dataset.dragInitialized) return;

    // 드래그 시작
    treeContainer.addEventListener('dragstart', (e) => {
        const node = e.target.closest('.tree-node[draggable="true"]');
        if (!node) return;

        // 드래그 핸들에서만 드래그 시작 허용 (아이콘 포함)
        const handle = e.target.closest('.tree-drag-handle');
        if (!handle) {
            e.preventDefault();
            return;
        }

        treeDraggedNode = node;
        treeDraggedParentId = node.dataset.parentId || '';
        node.classList.add('dragging');

        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', node.dataset.id);
    });

    // 드래그 종료
    treeContainer.addEventListener('dragend', (e) => {
        if (treeDraggedNode) {
            treeDraggedNode.classList.remove('dragging');
        }
        // 모든 드롭 표시 제거
        treeContainer.querySelectorAll('.tree-node.drag-over, .tree-node.drag-over-above, .tree-node.drag-over-below').forEach(el => {
            el.classList.remove('drag-over', 'drag-over-above', 'drag-over-below');
        });
        treeDraggedNode = null;
        treeDraggedParentId = null;
    });

    // 드래그 오버
    treeContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        if (!treeDraggedNode) return;

        const targetNode = e.target.closest('.tree-node[draggable="true"]');
        if (!targetNode || targetNode === treeDraggedNode) return;

        // 같은 부모의 자식만 허용 (빈 문자열도 동일 취급)
        const targetParentId = targetNode.dataset.parentId || '';
        if (targetParentId !== treeDraggedParentId) {
            e.dataTransfer.dropEffect = 'none';
            return;
        }

        e.dataTransfer.dropEffect = 'move';

        // 드롭 위치 표시 (위/아래)
        const rect = targetNode.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;

        // 기존 표시 제거
        treeContainer.querySelectorAll('.tree-node.drag-over-above, .tree-node.drag-over-below').forEach(el => {
            el.classList.remove('drag-over-above', 'drag-over-below');
        });

        if (e.clientY < midY) {
            targetNode.classList.add('drag-over-above');
        } else {
            targetNode.classList.add('drag-over-below');
        }
    });

    // 드래그 리브
    treeContainer.addEventListener('dragleave', (e) => {
        const targetNode = e.target.closest('.tree-node');
        if (targetNode) {
            targetNode.classList.remove('drag-over', 'drag-over-above', 'drag-over-below');
        }
    });

    // 드롭
    treeContainer.addEventListener('drop', async (e) => {
        e.preventDefault();
        if (!treeDraggedNode) return;

        const targetNode = e.target.closest('.tree-node[draggable="true"]');
        if (!targetNode || targetNode === treeDraggedNode) return;

        // 같은 부모의 자식만 허용
        const targetParentId = targetNode.dataset.parentId || '';
        if (targetParentId !== treeDraggedParentId) return;

        const rect = targetNode.getBoundingClientRect();
        const midY = rect.top + rect.height / 2;
        const insertBefore = e.clientY < midY;

        // DOM 업데이트
        const parent = targetNode.parentNode;
        if (insertBefore) {
            parent.insertBefore(treeDraggedNode, targetNode);
        } else {
            parent.insertBefore(treeDraggedNode, targetNode.nextSibling);
        }

        // 표시 제거
        targetNode.classList.remove('drag-over-above', 'drag-over-below');

        // 서버에 순서 저장 (부모 ID가 있는 경우만)
        if (treeDraggedParentId) {
            await saveOrgTreeOrder(treeDraggedParentId);
        }
    });

    treeContainer.dataset.dragInitialized = 'true';
}

/**
 * 조직 트리 순서 저장
 */
async function saveOrgTreeOrder(parentId) {
    if (!parentId) return;

    // 해당 부모의 자식 노드들 순서 수집
    const parent = document.querySelector(`.tree-node[data-id="${parentId}"]`);
    if (!parent) return;

    const childrenContainer = parent.querySelector('.tree-children');
    if (!childrenContainer) return;

    const children = childrenContainer.querySelectorAll(':scope > .tree-node');
    const orgIds = Array.from(children).map(node => parseInt(node.dataset.id));

    if (orgIds.length === 0) return;

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch('/admin/api/organizations/reorder', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify({
                parent_id: parseInt(parentId),
                org_ids: orgIds
            })
        });

        const result = await response.json();

        if (result.success) {
            showToast('순서가 저장되었습니다', 'success');
        } else {
            showToast(result.error || '순서 저장에 실패했습니다', 'error');
            // 실패 시 데이터 다시 로드
            await loadOrgManagementTab();
        }
    } catch (error) {
        console.error('순서 저장 오류:', error);
        showToast('순서 저장 중 오류가 발생했습니다', 'error');
        await loadOrgManagementTab();
    }
}

/**
 * 트리 노드 렌더링
 */
function renderTreeNode(org, parentId = null) {
    const typeIcons = {
        'company': 'fa-building',
        'division': 'fa-layer-group',
        'department': 'fa-users',
        'team': 'fa-user-friends',
        'headquarters': 'fa-building',
        'section': 'fa-user-friends',
        'office': 'fa-door-open',
        'part': 'fa-puzzle-piece'
    };
    const icon = typeIcons[org.org_type] || 'fa-folder';
    const hasChildren = org.children && org.children.length > 0;
    const isRoot = org.org_type === 'company';

    return `
        <div class="tree-node" data-id="${org.id}" data-type="${org.org_type}" data-parent-id="${parentId || ''}" draggable="${!isRoot}">
            <div class="tree-node-content" data-action="select-org" data-org-id="${org.id}">
                ${!isRoot ? `
                    <span class="tree-drag-handle" title="드래그하여 순서 변경">
                        <i class="fas fa-grip-vertical"></i>
                    </span>
                ` : ''}
                ${hasChildren ? `
                    <span class="tree-toggle" data-action="toggle-node">
                        <i class="fas fa-chevron-right"></i>
                    </span>
                ` : '<span class="tree-toggle-placeholder"></span>'}
                <span class="tree-icon">
                    <i class="fas ${icon}"></i>
                </span>
                <span class="tree-label">${escapeHtml(org.name)}</span>
                ${org.total_member_count > 0 ? `<span class="tree-member-count">(${org.total_member_count}명)</span>` : ''}
                ${org.code ? `<span class="tree-code">${escapeHtml(org.code)}</span>` : ''}
            </div>
            ${hasChildren ? `
                <div class="tree-children collapsed">
                    ${org.children.map(child => renderTreeNode(child, org.id)).join('')}
                </div>
            ` : ''}
        </div>
    `;
}

/**
 * 상위 조직 선택 옵션 업데이트
 */
async function updateParentOrgOptions() {
    try {
        const response = await fetch('/admin/api/organizations?format=flat');
        const result = await response.json();

        if (result.success) {
            const select = document.getElementById('orgParent');
            if (!select) return;

            select.innerHTML = '<option value="">없음 (최상위)</option>' +
                result.data.map(org => `<option value="${org.id}">${escapeHtml(org.path || org.name)}</option>`).join('');
        }
    } catch (error) {
        console.error('상위 조직 옵션 로드 실패:', error);
    }
}

/**
 * 트리 노드 토글
 */
function toggleTreeNode(el) {
    const node = el.closest('.tree-node');
    const children = node.querySelector('.tree-children');
    const icon = el.querySelector('i');

    if (children) {
        children.classList.toggle('collapsed');
        icon.classList.toggle('fa-chevron-right');
        icon.classList.toggle('fa-chevron-down');
    }
}

/**
 * 전체 펼치기
 */
function expandAllTree() {
    document.querySelectorAll('#orgTree .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('#orgTree .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });
}

/**
 * 전체 접기
 */
function collapseAllTree() {
    document.querySelectorAll('#orgTree .tree-children').forEach(el => {
        el.classList.add('collapsed');
    });
    document.querySelectorAll('#orgTree .tree-toggle i').forEach(el => {
        el.classList.add('fa-chevron-right');
        el.classList.remove('fa-chevron-down');
    });
}

/**
 * 트리 펼치기/접기 토글
 */
function toggleTreeExpand() {
    if (state.treeExpanded) {
        collapseAllTree();
        updateToggleButton(false);
    } else {
        expandAllTree();
        updateToggleButton(true);
    }
    state.treeExpanded = !state.treeExpanded;
}

/**
 * 토글 버튼 상태 업데이트
 */
function updateToggleButton(expanded) {
    const btn = document.getElementById('toggleTreeBtn');
    if (!btn) return;

    const icon = btn.querySelector('i');
    const srText = btn.querySelector('.sr-only');

    if (expanded) {
        icon.className = 'fas fa-compress-alt';
        btn.title = '전체 접기';
        if (srText) srText.textContent = '전체 접기';
    } else {
        icon.className = 'fas fa-expand-alt';
        btn.title = '전체 펼치기';
        if (srText) srText.textContent = '전체 펼치기';
    }
}

/**
 * 조직유형 설정 모달 열기
 */
function toggleOrgTypeSettings() {
    const modal = document.getElementById('orgTypeModal');
    if (!modal) return;

    modal.classList.add('show');

    // 드래그 앤 드롭 재초기화 (모달 내 테이블용)
    setTimeout(() => {
        initOrgTypeSortable();
    }, 100);
}

/**
 * 조직유형 설정 모달 닫기
 */
function closeOrgTypeModal() {
    const modal = document.getElementById('orgTypeModal');
    if (modal) {
        modal.classList.remove('show');
    }
}

/**
 * 조직 선택
 */
async function selectOrganization(orgId) {
    selectedOrgId = orgId;

    // 기존 선택 해제
    document.querySelectorAll('.tree-node-content.selected').forEach(el => {
        el.classList.remove('selected');
    });

    // 새로운 선택
    const node = document.querySelector(`.tree-node[data-id="${orgId}"] > .tree-node-content`);
    if (node) {
        node.classList.add('selected');
    }

    // 상세 정보 로드
    try {
        const response = await fetch(`/admin/api/organizations/${orgId}`);
        const result = await response.json();

        if (result.success) {
            renderOrgDetail(result.data);
        }
    } catch (error) {
        console.error('조직 정보 로드 오류:', error);
    }
}

/**
 * 조직 상세 정보 렌더링
 */
function renderOrgDetail(org) {
    const panel = document.getElementById('orgDetailPanel');
    if (!panel) return;

    const typeLabels = {
        'company': '회사',
        'division': '본부',
        'department': '부서',
        'team': '팀',
        'unit': '파트',
        'headquarters': '본부',
        'section': '소',
        'office': '실',
        'part': '파트'
    };

    // 소속인원 표시 (직접 + 하위 조직 합계)
    const memberCountHtml = org.total_member_count !== undefined
        ? `<div class="info-row">
               <span class="info-label">소속인원</span>
               <span class="info-value">${org.total_member_count}명${org.direct_member_count !== undefined && org.direct_member_count !== org.total_member_count ? ` (직접: ${org.direct_member_count}명)` : ''}</span>
           </div>`
        : '';

    // 대표 내선번호 표시
    const deptPhoneHtml = org.department_phone
        ? `<div class="info-row">
               <span class="info-label">대표 내선번호</span>
               <span class="info-value">${escapeHtml(org.department_phone)}</span>
           </div>`
        : '';

    // 조직 이메일 표시
    const deptEmailHtml = org.department_email
        ? `<div class="info-row">
               <span class="info-label">조직 이메일</span>
               <span class="info-value">${escapeHtml(org.department_email)}</span>
           </div>`
        : '';

    panel.querySelector('.panel-body').innerHTML = `
        <div class="org-detail">
            <div class="detail-header">
                <h4>${escapeHtml(org.name)}</h4>
                <span class="org-type-badge ${org.org_type}">${typeLabels[org.org_type] || org.org_type}</span>
            </div>

            <div class="detail-info">
                <div class="info-row">
                    <span class="info-label">조직 코드</span>
                    <span class="info-value">${org.code || '-'}</span>
                </div>
                ${memberCountHtml}
                <div class="info-row">
                    <span class="info-label">조직 경로</span>
                    <span class="info-value">${org.path || org.name}</span>
                </div>
                ${deptPhoneHtml}
                ${deptEmailHtml}
                <div class="info-row">
                    <span class="info-label">설명</span>
                    <span class="info-value">${org.description || '-'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">등록일</span>
                    <span class="info-value">${org.created_at ? new Date(org.created_at).toLocaleDateString('ko-KR') : '-'}</span>
                </div>
            </div>

            <div class="detail-actions">
                <button class="btn btn-secondary" data-action="edit-org" data-org-id="${org.id}">
                    <i class="fas fa-edit"></i> 수정
                </button>
                <button class="btn btn-secondary" data-action="add-child" data-parent-id="${org.id}">
                    <i class="fas fa-plus"></i> 하위 조직 추가
                </button>
                <button class="btn btn-danger" data-action="delete-org" data-org-id="${org.id}" data-org-name="${escapeHtml(org.name)}">
                    <i class="fas fa-trash"></i> 삭제
                </button>
            </div>
        </div>
    `;
}

/**
 * 조직 추가 모달 표시
 */
async function showAddOrgModal() {
    document.getElementById('orgModalTitle').textContent = '조직 추가';
    document.getElementById('orgForm').reset();
    document.getElementById('orgId').value = '';
    // 조직유형 옵션 및 직원 목록 동적 로드
    await Promise.all([
        loadOrgTypeOptions(),
        loadEmployeesForManager()
    ]);
    document.getElementById('orgModal').classList.add('show');
}

/**
 * 조직장 선택을 위한 직원 목록 로드
 */
async function loadEmployeesForManager() {
    const select = document.getElementById('orgManager');
    if (!select) return;

    try {
        const response = await fetch('/admin/api/organizations/employees');
        const result = await response.json();

        if (result.success && result.data) {
            select.innerHTML = '<option value="">선택하세요</option>' +
                result.data.map(emp =>
                    `<option value="${emp.id}">${emp.name}${emp.position ? ` (${emp.position})` : ''}</option>`
                ).join('');
        }
    } catch (error) {
        console.error('직원 목록 로드 실패:', error);
        select.innerHTML = '<option value="">선택하세요</option>';
    }
}

/**
 * 조직유형 옵션 동적 로드
 */
async function loadOrgTypeOptions() {
    const select = document.getElementById('orgType');
    if (!select) return;

    try {
        const response = await fetch('/api/corporate/organization-types/active');
        const result = await response.json();

        if (result.success && result.data) {
            select.innerHTML = result.data.map(type =>
                `<option value="${type.value}">${type.label}</option>`
            ).join('');

            // 기본값 선택 (팀 또는 첫 번째 옵션)
            const defaultOption = select.querySelector('option[value="team"]') ||
                                  select.querySelector('option[value="department"]') ||
                                  select.querySelector('option');
            if (defaultOption) {
                defaultOption.selected = true;
            }
        }
    } catch (error) {
        console.error('조직유형 옵션 로드 실패:', error);
        // 폴백: 기본 옵션
        select.innerHTML = `
            <option value="headquarters">본부</option>
            <option value="division">부</option>
            <option value="team" selected>팀</option>
            <option value="section">소</option>
            <option value="department">과</option>
            <option value="office">실</option>
            <option value="part">파트</option>
        `;
    }
}

/**
 * 하위 조직 추가 모달
 */
function showAddChildModal(parentId) {
    showAddOrgModal();
    document.getElementById('orgParent').value = parentId;
}

/**
 * 조직 수정 모달
 */
async function showEditOrgModal(orgId) {
    try {
        // 조직유형 옵션 및 직원 목록 먼저 로드
        await Promise.all([
            loadOrgTypeOptions(),
            loadEmployeesForManager()
        ]);

        const response = await fetch(`/admin/api/organizations/${orgId}`);
        const result = await response.json();

        if (result.success) {
            const org = result.data;
            document.getElementById('orgModalTitle').textContent = '조직 수정';
            document.getElementById('orgId').value = org.id;
            document.getElementById('orgName').value = org.name;
            document.getElementById('orgCode').value = org.code || '';
            document.getElementById('orgType').value = org.org_type;
            document.getElementById('orgParent').value = org.parent_id || '';
            document.getElementById('orgDescription').value = org.description || '';
            // 조직장/연락처 필드
            document.getElementById('orgManager').value = org.manager_id || '';
            document.getElementById('deptPhone').value = org.department_phone || '';
            document.getElementById('deptEmail').value = org.department_email || '';
            document.getElementById('orgModal').classList.add('show');
        }
    } catch (error) {
        console.error('조직 정보 로드 오류:', error);
    }
}

/**
 * 조직 저장
 */
async function saveOrganization(event) {
    event.preventDefault();

    const orgId = document.getElementById('orgId').value;
    const parentIdValue = document.getElementById('orgParent').value;
    const managerIdValue = document.getElementById('orgManager').value;
    const data = {
        name: document.getElementById('orgName').value,
        code: document.getElementById('orgCode').value || null,
        org_type: document.getElementById('orgType').value,
        parent_id: parentIdValue ? parseInt(parentIdValue, 10) : null,
        description: document.getElementById('orgDescription').value || null,
        manager_id: managerIdValue ? parseInt(managerIdValue, 10) : null,
        department_phone: document.getElementById('deptPhone').value || null,
        department_email: document.getElementById('deptEmail').value || null
    };

    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const url = orgId ? `/admin/api/organizations/${orgId}` : '/admin/api/organizations';
        const method = orgId ? 'PUT' : 'POST';

        const response = await fetch(url, {
            method: method,
            headers: {
                'Content-Type': 'application/json',
                'X-CSRFToken': csrfToken
            },
            body: JSON.stringify(data)
        });

        const result = await response.json();

        if (result.success) {
            closeOrgModal();
            showToast(orgId ? '조직이 수정되었습니다' : '조직이 추가되었습니다', 'success');
            // 데이터 새로고침
            state.loadedTabs.delete('org-management');
            await loadOrgManagementData();
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직 모달 닫기
 */
function closeOrgModal() {
    document.getElementById('orgModal')?.classList.remove('show');
}

/**
 * 삭제 모달 표시
 */
function showDeleteModal(orgId, orgName) {
    deleteOrgId = orgId;
    document.getElementById('deleteMessage').textContent = `'${orgName}' 조직을 삭제하시겠습니까?`;
    document.getElementById('cascadeDelete').checked = false;
    document.getElementById('deleteModal').classList.add('show');
}

/**
 * 삭제 모달 닫기
 */
function closeDeleteModal() {
    document.getElementById('deleteModal')?.classList.remove('show');
    deleteOrgId = null;
}

/**
 * 삭제 확인
 */
async function confirmDeleteOrg() {
    if (!deleteOrgId) return;

    const cascade = document.getElementById('cascadeDelete').checked;
    const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;

    try {
        const response = await fetch(`/admin/api/organizations/${deleteOrgId}?cascade=${cascade}`, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken
            }
        });

        const result = await response.json();

        if (result.success) {
            closeDeleteModal();
            showToast('조직이 삭제되었습니다', 'success');
            // 데이터 새로고침
            state.loadedTabs.delete('org-management');
            await loadOrgManagementData();
        } else {
            showToast(result.error || '삭제에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직 삭제 오류:', error);
        showToast('삭제 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직 관리 이벤트 핸들러 초기화
 */
function initOrgManagementHandlers() {
    const container = document.getElementById('tab-org-management');
    if (!container || container.dataset.handlersInitialized) return;

    // 공통 액션 핸들러
    function handleAction(action, target) {
        switch (action) {
            case 'toggle-node':
                toggleTreeNode(target);
                return true;
            case 'select-org':
                selectOrganization(parseInt(target.dataset.orgId));
                return true;
            case 'add-org':
                showAddOrgModal();
                return true;
            case 'toggle-tree':
                toggleTreeExpand();
                return true;
            case 'toggle-org-type-settings':
                toggleOrgTypeSettings();
                return true;
            case 'close-org-type-modal':
                closeOrgTypeModal();
                return true;
            case 'close-org-modal':
                closeOrgModal();
                return true;
            case 'close-delete-modal':
                closeDeleteModal();
                return true;
            case 'confirm-delete':
                confirmDeleteOrg();
                return true;
            case 'edit-org':
                showEditOrgModal(parseInt(target.dataset.orgId));
                return true;
            case 'add-child':
                showAddChildModal(parseInt(target.dataset.parentId));
                return true;
            case 'delete-org':
                showDeleteModal(parseInt(target.dataset.orgId), target.dataset.orgName);
                return true;
            case 'reset-org-types':
                resetOrgTypes();
                return true;
            case 'select-icon':
                showIconSelector(parseInt(target.dataset.id));
                return true;
            case 'delete-org-type':
                deleteOrgType(parseInt(target.dataset.id), target.dataset.typeCode);
                return true;
            case 'add-org-type':
                addOrgType();
                return true;
        }
        return false;
    }

    container.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;
        if (action === 'toggle-node') {
            e.stopPropagation();
        }
        handleAction(action, target);
    });

    // 조직유형 모달 이벤트 핸들러 (모달은 container 외부에 있음)
    const orgTypeModal = document.getElementById('orgTypeModal');
    if (orgTypeModal && !orgTypeModal.dataset.handlersInitialized) {
        orgTypeModal.addEventListener('click', function(e) {
            const target = e.target.closest('[data-action]');
            if (!target) {
                // 모달 배경 클릭 시 닫기
                if (e.target === orgTypeModal) {
                    closeOrgTypeModal();
                }
                return;
            }
            handleAction(target.dataset.action, target);
        });

        // 조직유형 라벨 입력 이벤트 (blur 시 저장)
        orgTypeModal.addEventListener('blur', function(e) {
            const input = e.target.closest('.org-type-label-input');
            if (input && input.value !== input.dataset.original) {
                const field = input.dataset.field || 'type_label_ko';
                saveOrgTypeLabel(parseInt(input.dataset.id), field, input.value.trim());
            }
        }, true);

        // 조직유형 라벨 입력 이벤트 (Enter 키)
        orgTypeModal.addEventListener('keydown', function(e) {
            if (e.key === 'Enter') {
                const input = e.target.closest('.org-type-label-input');
                if (input) {
                    e.preventDefault();
                    input.blur();
                }
            }
        });

        orgTypeModal.dataset.handlersInitialized = 'true';
    }

    // 조직유형 라벨 입력 이벤트 (blur 시 저장)
    container.addEventListener('blur', function(e) {
        const input = e.target.closest('.org-type-label-input');
        if (input && input.value !== input.dataset.original) {
            const field = input.dataset.field || 'type_label_ko';
            saveOrgTypeLabel(parseInt(input.dataset.id), field, input.value.trim());
        }
    }, true);

    // 조직유형 라벨 입력 이벤트 (Enter 키)
    container.addEventListener('keydown', function(e) {
        if (e.key === 'Enter') {
            const input = e.target.closest('.org-type-label-input');
            if (input) {
                e.preventDefault();
                input.blur();
            }
        }
    });

    // 폼 제출 이벤트
    container.addEventListener('submit', function(e) {
        const target = e.target.closest('[data-action="save-org"]');
        if (target) {
            e.preventDefault();
            saveOrganization(e);
        }
    });

    container.dataset.handlersInitialized = 'true';
}

// ========================================
// 조직 구조 탭 (분류 옵션 관리)
// ========================================
async function loadOrganizationData() {
    const content = document.getElementById('organization-content');

    try {
        const response = await ClassificationApi.getOrganization();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-organization [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('조직 구조 데이터 로드 실패:', error);
        showContentError(content);
    }
}

async function loadEmploymentData() {
    const content = document.getElementById('employment-content');

    try {
        const response = await ClassificationApi.getEmployment();
        Object.entries(response.data).forEach(([category, options]) => {
            renderCategoryList(`#tab-employment [data-category="${category}"]`, category, options);
        });
    } catch (error) {
        console.error('고용 정책 데이터 로드 실패:', error);
        showContentError(content);
    }
}

async function loadPatternsData() {
    const content = document.getElementById('patterns-content');

    try {
        const response = await SettingsApi.getAll();
        applySettingsToForm(response.data);
        updatePreviews();
    } catch (error) {
        console.error('패턴 규칙 데이터 로드 실패:', error);
        showContentError(content);
    }
}

async function loadVisibilityData() {
    const content = document.getElementById('visibility-content');

    try {
        const response = await VisibilityApi.get();
        applyVisibilityToForm(response.data);
    } catch (error) {
        console.error('노출 설정 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 법인 서류 데이터 로드
 */
async function loadDocumentsData() {
    const content = document.getElementById('documents-content');

    try {
        const [documentsResponse, statisticsResponse] = await Promise.all([
            DocumentsApi.getAll(),
            DocumentsApi.getStatistics()
        ]);

        // API 응답 구조: { success: true, data: { documents: [...], statistics: {...} } }
        const responseData = documentsResponse.data || documentsResponse;
        const documents = Array.isArray(responseData) ? responseData : (responseData.documents || []);
        const statistics = statisticsResponse.data || statisticsResponse;

        // 통계 업데이트
        updateDocumentStatistics(statistics);

        // 카테고리별 문서 렌더링 (템플릿과 일치)
        const categories = ['required', 'payroll', 'welfare', 'security', 'contract', 'other'];
        categories.forEach(category => {
            // benefits와 welfare 매핑 (DB에서 benefits로 저장된 경우 대응)
            const categoryDocs = documents.filter(d =>
                d.category === category ||
                (category === 'welfare' && d.category === 'benefits')
            );
            renderDocumentList(category, categoryDocs);
        });
    } catch (error) {
        console.error('법인 서류 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 문서 통계 업데이트
 * @param {Object} statistics - 통계 데이터
 */
function updateDocumentStatistics(statistics) {
    const statItems = document.querySelectorAll('.stat-item');
    statItems.forEach(item => {
        const label = item.querySelector('.stat-label')?.textContent;
        const valueEl = item.querySelector('.stat-value');
        if (!valueEl) return;

        if (label?.includes('전체')) {
            valueEl.textContent = statistics.total || 0;
        } else if (label?.includes('필수')) {
            valueEl.textContent = statistics.required || 0;
        } else if (label?.includes('만료')) {
            valueEl.textContent = statistics.expiringSoon || 0;
        }
    });
}

/**
 * 문서 리스트 렌더링
 * @param {string} category - 카테고리
 * @param {Array} documents - 문서 목록
 */
function renderDocumentList(category, documents) {
    const listContainer = document.querySelector(`.document-list[data-category="${category}"]`);
    if (!listContainer) return;

    if (documents.length === 0) {
        listContainer.innerHTML = `
            <div class="document-empty">
                <i class="fas fa-folder-open"></i>
                <p>등록된 서류가 없습니다</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = documents.map(doc => {
        const expiresText = doc.expiresAt ? formatDate(doc.expiresAt) : '';
        const isExpiring = doc.expiresAt && isExpiringSoon(doc.expiresAt);

        return `
            <div class="document-item ${isExpiring ? 'is-expiring' : ''}" data-id="${doc.id}">
                <div class="document-icon">
                    <i class="fas ${getFileIcon(doc.fileType)}"></i>
                </div>
                <div class="document-info">
                    <span class="document-title">${escapeHtml(doc.title)}</span>
                    <span class="document-meta">
                        ${doc.version ? `v${doc.version}` : ''}
                        ${expiresText ? `<span class="document-expires ${isExpiring ? 'text-danger' : ''}">${expiresText} 만료</span>` : ''}
                    </span>
                </div>
                <div class="document-actions">
                    <button class="btn-icon" data-action="download" title="다운로드">
                        <i class="fas fa-download"></i>
                    </button>
                    <button class="btn-icon" data-action="edit" title="수정">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" data-action="delete" title="삭제">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 파일 타입에 따른 아이콘 반환
 * @param {string} fileType - 파일 타입
 * @returns {string} 아이콘 클래스
 */
function getFileIcon(fileType) {
    const iconMap = {
        'application/pdf': 'fa-file-pdf',
        'image/jpeg': 'fa-file-image',
        'image/png': 'fa-file-image',
        'application/msword': 'fa-file-word',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document': 'fa-file-word',
        'application/vnd.ms-excel': 'fa-file-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': 'fa-file-excel'
    };
    return iconMap[fileType] || 'fa-file';
}

/**
 * 날짜 포맷팅
 * @param {string} dateStr - 날짜 문자열
 * @returns {string} 포맷된 날짜
 */
function formatDate(dateStr) {
    const date = new Date(dateStr);
    return `${date.getFullYear()}.${String(date.getMonth() + 1).padStart(2, '0')}.${String(date.getDate()).padStart(2, '0')}`;
}

/**
 * 만료 임박 여부 확인
 * @param {string} dateStr - 만료일
 * @returns {boolean} 30일 이내 만료 여부
 */
function isExpiringSoon(dateStr) {
    const expires = new Date(dateStr);
    const now = new Date();
    const diffDays = Math.ceil((expires - now) / (1000 * 60 * 60 * 24));
    return diffDays > 0 && diffDays <= 30;
}

/**
 * 카테고리 리스트 렌더링
 * @param {string} selector - 섹션 셀렉터
 * @param {string} category - 카테고리 코드
 * @param {Array} options - 옵션 목록
 */
function renderCategoryList(selector, category, options) {
    const section = document.querySelector(selector);
    if (!section) return;

    const listContainer = section.querySelector('.category-list');
    const countEl = section.querySelector('.category-count');

    // 옵션 개수 표시
    countEl.textContent = `(${options.length}개)`;

    if (options.length === 0) {
        listContainer.innerHTML = `
            <div class="category-empty">
                <i class="fas fa-inbox"></i>
                <p>등록된 항목이 없습니다</p>
            </div>
        `;
        return;
    }

    listContainer.innerHTML = options.map(option => {
        return `
            <div class="category-item" data-id="${option.id}" data-value="${option.value}">
                <div class="category-item-content">
                    <span class="category-item-value">${escapeHtml(option.label || option.value)}</span>
                </div>
                <div class="category-item-actions">
                    <button class="btn-icon" data-action="edit" title="수정">
                        <i class="fas fa-edit"></i>
                    </button>
                    <button class="btn-icon" data-action="delete" title="삭제">
                        <i class="fas fa-trash"></i>
                    </button>
                </div>
            </div>
        `;
    }).join('');
}

/**
 * 설정값을 폼에 적용
 * @param {Object} settings - 설정 데이터
 */
function applySettingsToForm(settings) {
    // 회사 코드
    const companyCode = document.getElementById('company_code');
    if (companyCode && settings.company_code) {
        companyCode.value = settings.company_code;
    }

    // 사번 접두어
    const prefix = document.getElementById('employee_number_prefix');
    if (prefix && settings['employee_number.prefix']) {
        prefix.value = settings['employee_number.prefix'];
    }

    // 사번 구분자
    const separator = document.getElementById('employee_number_separator');
    if (separator && settings['employee_number.separator']) {
        separator.value = settings['employee_number.separator'];
    }

    // 사번 자릿수
    const digits = document.getElementById('employee_number_digits');
    if (digits && settings['employee_number.digits']) {
        digits.value = settings['employee_number.digits'];
    }

    // 사번 연도 포함
    const includeYear = document.getElementById('employee_number_include_year');
    if (includeYear) {
        includeYear.checked = settings['employee_number.include_year'] === true;
    }

    // 이메일 도메인
    const emailDomain = document.getElementById('email_domain');
    if (emailDomain && settings['email.domain']) {
        emailDomain.value = settings['email.domain'];
    }

    // 이메일 자동 생성
    const autoEmail = document.getElementById('auto_generate_email');
    if (autoEmail) {
        autoEmail.checked = settings['email.auto_generate'] === true;
    }

    // 이메일 포맷
    const emailFormat = document.getElementById('email_format');
    if (emailFormat && settings['email.format']) {
        emailFormat.value = settings['email.format'];
    }

    // 내선번호 자릿수
    const phoneDigits = document.getElementById('internal_phone_digits');
    if (phoneDigits && settings['internal_phone.digits']) {
        phoneDigits.value = settings['internal_phone.digits'];
    }

    // 내선번호 범위
    const extStart = document.getElementById('extension_range_start');
    if (extStart && settings['internal_phone.range_start']) {
        extStart.value = settings['internal_phone.range_start'];
    }

    const extEnd = document.getElementById('extension_range_end');
    if (extEnd && settings['internal_phone.range_end']) {
        extEnd.value = settings['internal_phone.range_end'];
    }

    // 급여 지급일
    const paymentDay = document.getElementById('payment_day');
    if (paymentDay && settings['payroll.payment_day']) {
        paymentDay.value = settings['payroll.payment_day'];
    }

    // IP 설정
    const ipAutoAssign = document.getElementById('ip_auto_assign');
    if (ipAutoAssign) {
        ipAutoAssign.checked = settings['ip.auto_assign'] === true;
    }

    const ipRangeStart = document.getElementById('ip_range_start');
    if (ipRangeStart && settings['ip.range_start']) {
        ipRangeStart.value = settings['ip.range_start'];
    }

    const ipRangeEnd = document.getElementById('ip_range_end');
    if (ipRangeEnd && settings['ip.range_end']) {
        ipRangeEnd.value = settings['ip.range_end'];
    }

    // 자산번호 설정
    const assetPrefix = document.getElementById('asset_number_prefix');
    if (assetPrefix && settings['asset_number.prefix']) {
        assetPrefix.value = settings['asset_number.prefix'];
    }

    const assetSeparator = document.getElementById('asset_number_separator');
    if (assetSeparator && settings['asset_number.separator']) {
        assetSeparator.value = settings['asset_number.separator'];
    }

    const assetDigits = document.getElementById('asset_number_digits');
    if (assetDigits && settings['asset_number.digits']) {
        assetDigits.value = settings['asset_number.digits'];
    }
}

/**
 * 노출 설정값을 폼에 적용
 * @param {Object} data - 노출 설정 데이터
 */
function applyVisibilityToForm(data) {
    const fields = [
        'salary_visibility',
        'show_salary_to_managers',
        'evaluation_visibility',
        'show_evaluation_to_managers',
        'org_chart_visibility',
        'contact_visibility',
        'document_visibility'
    ];

    fields.forEach(field => {
        const el = document.getElementById(field);
        // camelCase로 변환
        const camelField = field.replace(/_([a-z])/g, (_, c) => c.toUpperCase());
        if (el && data[camelField] !== undefined) {
            el.checked = data[camelField];
        }
    });
}

/**
 * 미리보기 업데이트
 */
function updatePreviews() {
    // 사번 미리보기
    const companyCode = document.getElementById('company_code')?.value || 'ABC';
    const prefix = document.getElementById('employee_number_prefix')?.value || 'EMP';
    const separator = document.getElementById('employee_number_separator')?.value || '-';
    const digits = parseInt(document.getElementById('employee_number_digits')?.value) || 6;
    const includeYear = document.getElementById('employee_number_include_year')?.checked;

    const employeePreview = document.getElementById('employee_number_preview');
    if (employeePreview) {
        const seq = '1'.padStart(digits, '0');
        const year = new Date().getFullYear();
        let preview = companyCode;
        if (separator) preview += separator;
        if (includeYear) preview += year + (separator || '');
        preview += prefix;
        if (separator) preview += separator;
        preview += seq;
        employeePreview.textContent = preview;
    }

    // 이메일 미리보기
    const emailDomain = document.getElementById('email_domain')?.value || 'company.co.kr';
    const emailFormat = document.getElementById('email_format')?.value || 'first.last';
    const emailPreview = document.getElementById('email_preview');
    if (emailPreview) {
        const formatExamples = {
            'first.last': 'hong.gildong',
            'last.first': 'gildong.hong',
            'firstlast': 'honggildong',
            'first_last': 'hong_gildong',
            'flast': 'ghong',
            'first': 'gildong'
        };
        const username = formatExamples[emailFormat] || 'hong.gildong';
        emailPreview.textContent = `${username}@${emailDomain}`;
    }

    // 내선번호 범위 미리보기
    const extStart = document.getElementById('extension_range_start')?.value || '100';
    const extEnd = document.getElementById('extension_range_end')?.value || '999';
    const extRangePreview = document.getElementById('extension_range_preview');
    if (extRangePreview) {
        extRangePreview.textContent = `${extStart} ~ ${extEnd}`;
    }

    // IP 범위 미리보기
    const ipStart = document.getElementById('ip_range_start')?.value || '192.168.1.100';
    const ipEnd = document.getElementById('ip_range_end')?.value || '192.168.1.200';
    const ipRangePreview = document.getElementById('ip_range_preview');
    if (ipRangePreview) {
        ipRangePreview.textContent = `${ipStart} ~ ${ipEnd}`;
    }

    // 자산번호 미리보기
    const assetPrefix = document.getElementById('asset_number_prefix')?.value || 'ASSET';
    const assetSeparator = document.getElementById('asset_number_separator')?.value || '-';
    const assetDigits = parseInt(document.getElementById('asset_number_digits')?.value) || 4;
    const assetPreview = document.getElementById('asset_number_preview');
    if (assetPreview) {
        const seq = '1'.padStart(assetDigits, '0');
        assetPreview.textContent = `${assetPrefix}${assetSeparator}${seq}`;
    }
}

/**
 * 카테고리 이벤트 핸들러 초기화
 */
function initCategoryHandlers() {
    // 추가 버튼
    document.querySelectorAll('.category-section [data-action="add"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const section = e.target.closest('.category-section');
            const form = section.querySelector('.add-item-form');
            form.classList.remove('d-none');
            form.querySelector('input').focus();
        });
    });

    // 저장/취소 버튼
    document.querySelectorAll('.add-item-form [data-action="save"]').forEach(btn => {
        btn.addEventListener('click', (e) => handleAddItem(e));
    });

    document.querySelectorAll('.add-item-form [data-action="cancel"]').forEach(btn => {
        btn.addEventListener('click', (e) => {
            const form = e.target.closest('.add-item-form');
            form.classList.add('d-none');
            form.querySelector('input').value = '';
        });
    });

    // 리스트 아이템 이벤트 위임
    document.querySelectorAll('.category-list').forEach(list => {
        list.addEventListener('click', handleListItemAction);
        list.addEventListener('change', handleListItemToggle);
    });
}

/**
 * 항목 추가 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleAddItem(e) {
    const form = e.target.closest('.add-item-form');
    const section = form.closest('.category-section');
    const category = section.dataset.category;
    const input = form.querySelector('input[data-field="value"]');
    const value = input.value.trim();

    if (!value) {
        showToast('값을 입력해주세요', 'warning');
        return;
    }

    try {
        const result = await ClassificationApi.add(category, { value });
        showToast('항목이 추가되었습니다', 'success');

        // 폼 리셋
        input.value = '';
        form.classList.add('d-none');

        // 리스트 갱신
        await refreshCategory(section.closest('.tab-panel').id.replace('tab-', ''), category);
    } catch (error) {
        showToast(error.message || '추가에 실패했습니다', 'error');
    }
}

/**
 * 리스트 아이템 액션 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleListItemAction(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    const item = btn.closest('.category-item');
    const section = btn.closest('.category-section');
    const category = section.dataset.category;
    const optionId = item?.dataset.id;

    switch (action) {
        case 'edit':
            startInlineEdit(item, category, optionId);
            break;
        case 'delete':
            await handleDeleteItem(category, optionId, section);
            break;
    }
}

/**
 * 시스템 옵션 토글 핸들러
 * @param {Event} e - change 이벤트
 */
async function handleListItemToggle(e) {
    if (!e.target.matches('[data-action="toggle"]')) return;

    const input = e.target;
    const category = input.dataset.category;
    const value = input.dataset.value;
    const isActive = input.checked;

    try {
        await ClassificationApi.toggleSystemOption(category, { value, isActive });
        showToast(isActive ? '활성화되었습니다' : '비활성화되었습니다', 'success');

        // 아이템 스타일 업데이트
        const item = input.closest('.category-item');
        item.classList.toggle('is-disabled', !isActive);
    } catch (error) {
        // 롤백
        input.checked = !isActive;
        showToast(error.message || '변경에 실패했습니다', 'error');
    }
}

/**
 * 항목 삭제 핸들러
 * @param {string} category - 카테고리
 * @param {number} optionId - 옵션 ID
 * @param {Element} section - 섹션 엘리먼트
 */
async function handleDeleteItem(category, optionId, section) {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
        await ClassificationApi.delete(category, optionId);
        showToast('항목이 삭제되었습니다', 'success');

        // 리스트 갱신
        const tabId = section.closest('.tab-panel').id.replace('tab-', '');
        await refreshCategory(tabId, category);
    } catch (error) {
        showToast(error.message || '삭제에 실패했습니다', 'error');
    }
}

/**
 * 인라인 편집 시작
 * @param {Element} item - 아이템 엘리먼트
 * @param {string} category - 카테고리
 * @param {number} optionId - 옵션 ID
 */
function startInlineEdit(item, category, optionId) {
    const content = item.querySelector('.category-item-content');
    const value = item.querySelector('.category-item-value').textContent;

    // 현재 내용 저장
    const originalHtml = content.innerHTML;

    content.innerHTML = `
        <div class="inline-edit">
            <input type="text" class="inline-edit-input" value="${escapeHtml(value)}">
            <div class="inline-edit-actions">
                <button class="btn-icon btn-save" title="저장">
                    <i class="fas fa-check"></i>
                </button>
                <button class="btn-icon btn-cancel" title="취소">
                    <i class="fas fa-times"></i>
                </button>
            </div>
        </div>
    `;

    const input = content.querySelector('.inline-edit-input');
    input.focus();
    input.select();

    // 저장
    content.querySelector('.btn-save').addEventListener('click', async () => {
        const newValue = input.value.trim();
        if (!newValue) {
            showToast('값을 입력해주세요', 'warning');
            return;
        }

        try {
            await ClassificationApi.update(category, optionId, {
                value: newValue,
                label: newValue
            });
            showToast('수정되었습니다', 'success');

            // 리스트 갱신
            const section = item.closest('.category-section');
            const tabId = section.closest('.tab-panel').id.replace('tab-', '');
            await refreshCategory(tabId, category);
        } catch (error) {
            showToast(error.message || '수정에 실패했습니다', 'error');
            content.innerHTML = originalHtml;
        }
    });

    // 취소
    content.querySelector('.btn-cancel').addEventListener('click', () => {
        content.innerHTML = originalHtml;
    });

    // Enter/Escape 키 처리
    input.addEventListener('keydown', (e) => {
        if (e.key === 'Enter') {
            content.querySelector('.btn-save').click();
        } else if (e.key === 'Escape') {
            content.querySelector('.btn-cancel').click();
        }
    });
}

async function refreshCategory(tabId, category) {
    try {
        const response = await ClassificationApi.getByCategory(category);
        // API returns {data: {category: [options]}} format
        const options = response.data?.[category] || response.data?.options || response.options || [];
        renderCategoryList(`#tab-${tabId} [data-category="${category}"]`, category, options);
    } catch (error) {
        console.error(`카테고리 갱신 실패: ${category}`, error);
        showToast(`${category} 목록 갱신에 실패했습니다`, 'error');
    }
}

/**
 * 섹션별 설정 데이터 추출
 * @param {string} section - 섹션 이름
 * @returns {Object} 섹션별 설정 데이터
 */
function getSectionSettings(section) {
    const sectionSettingsMap = {
        'employee_number': {
            'company_code': document.getElementById('company_code')?.value || '',
            'employee_number.prefix': document.getElementById('employee_number_prefix')?.value || '',
            'employee_number.separator': document.getElementById('employee_number_separator')?.value || '-',
            'employee_number.digits': document.getElementById('employee_number_digits')?.value || '6',
            'employee_number.include_year': document.getElementById('employee_number_include_year')?.checked || false
        },
        'email': {
            'email.domain': document.getElementById('email_domain')?.value || '',
            'email.auto_generate': document.getElementById('auto_generate_email')?.checked || false,
            'email.format': document.getElementById('email_format')?.value || 'first.last'
        },
        'internal_phone': {
            'internal_phone.digits': document.getElementById('internal_phone_digits')?.value || '4',
            'internal_phone.range_start': document.getElementById('extension_range_start')?.value || '',
            'internal_phone.range_end': document.getElementById('extension_range_end')?.value || ''
        },
        'payroll': {
            'payroll.payment_day': document.getElementById('payment_day')?.value || '25'
        },
        'ip': {
            'ip.auto_assign': document.getElementById('ip_auto_assign')?.checked || false,
            'ip.range_start': document.getElementById('ip_range_start')?.value || '',
            'ip.range_end': document.getElementById('ip_range_end')?.value || ''
        },
        'asset_number': {
            'asset_number.prefix': document.getElementById('asset_number_prefix')?.value || '',
            'asset_number.separator': document.getElementById('asset_number_separator')?.value || '-',
            'asset_number.digits': document.getElementById('asset_number_digits')?.value || '4'
        }
    };

    return sectionSettingsMap[section] || {};
}

/**
 * 섹션 이름 한글 매핑
 */
const SECTION_LABELS = {
    'employee_number': '사번 규칙',
    'email': '이메일 설정',
    'internal_phone': '내선번호 설정',
    'payroll': '급여 설정',
    'ip': 'IP 주소 관리',
    'asset_number': '자산번호 설정'
};

/**
 * 섹션별 설정 저장
 * @param {string} section - 섹션 이름
 */
async function saveSectionSettings(section) {
    const btn = document.querySelector(`.section-save-btn[data-section="${section}"]`);
    const originalContent = btn?.innerHTML;

    try {
        // 버튼 로딩 상태
        if (btn) {
            btn.disabled = true;
            btn.innerHTML = '<i class="fas fa-spinner fa-spin"></i> <span>저장 중...</span>';
        }

        const settings = getSectionSettings(section);
        await SettingsApi.saveAll(settings);

        const label = SECTION_LABELS[section] || section;
        showToast(`${label}이(가) 저장되었습니다`, 'success');
    } catch (error) {
        showToast(error.message || '저장에 실패했습니다', 'error');
    } finally {
        // 버튼 복원
        if (btn) {
            btn.disabled = false;
            btn.innerHTML = originalContent;
        }
    }
}

/**
 * 패턴 규칙 저장 핸들러 초기화
 */
function initPatternsHandlers() {
    // 미리보기 업데이트를 트리거하는 모든 필드
    const previewFields = [
        'company_code', 'employee_number_prefix', 'employee_number_separator',
        'employee_number_digits', 'employee_number_include_year',
        'email_domain', 'email_format', 'auto_generate_email',
        'extension_range_start', 'extension_range_end',
        'ip_range_start', 'ip_range_end',
        'asset_number_prefix', 'asset_number_separator', 'asset_number_digits'
    ];

    previewFields.forEach(id => {
        const el = document.getElementById(id);
        if (el) {
            el.addEventListener('input', updatePreviews);
            el.addEventListener('change', updatePreviews);
        }
    });

    // 섹션별 저장 버튼 이벤트
    document.querySelectorAll('.section-save-btn[data-section]').forEach(btn => {
        btn.addEventListener('click', () => {
            const section = btn.dataset.section;
            saveSectionSettings(section);
        });
    });
}

/**
 * 문서 핸들러 초기화
 */
function initDocumentsHandlers() {
    // 드래그 앤 드롭 영역
    const dropzone = document.getElementById('document-dropzone');
    const fileInput = document.getElementById('document-file-input');
    const uploadForm = document.getElementById('document-upload-form');

    if (dropzone && fileInput) {
        // 클릭으로 파일 선택
        dropzone.addEventListener('click', () => fileInput.click());

        // 드래그 앤 드롭 이벤트
        dropzone.addEventListener('dragover', (e) => {
            e.preventDefault();
            dropzone.classList.add('dragover');
        });

        dropzone.addEventListener('dragleave', () => {
            dropzone.classList.remove('dragover');
        });

        dropzone.addEventListener('drop', (e) => {
            e.preventDefault();
            dropzone.classList.remove('dragover');
            const files = e.dataTransfer.files;
            if (files.length > 0) {
                handleFileSelect(files[0]);
            }
        });

        // 파일 선택 이벤트
        fileInput.addEventListener('change', (e) => {
            if (e.target.files.length > 0) {
                handleFileSelect(e.target.files[0]);
            }
        });
    }

    // 업로드 폼 제출
    if (uploadForm) {
        uploadForm.addEventListener('submit', handleDocumentUpload);

        // 카테고리 변경 시 서류 유형 업데이트
        const categorySelect = uploadForm.querySelector('[name="category"]');
        if (categorySelect) {
            categorySelect.addEventListener('change', updateDocumentTypeOptions);
        }

        // 취소 버튼
        const cancelBtn = uploadForm.querySelector('[data-action="cancel"]');
        if (cancelBtn) {
            cancelBtn.addEventListener('click', () => {
                uploadForm.classList.add('d-none');
                uploadForm.reset();
                document.getElementById('selected-file-name').textContent = '';
            });
        }
    }

    // 문서 리스트 액션 이벤트 위임
    document.querySelectorAll('.document-list').forEach(list => {
        list.addEventListener('click', handleDocumentAction);
    });
}

/**
 * 파일 선택 처리
 * @param {File} file - 선택된 파일
 */
function handleFileSelect(file) {
    const uploadForm = document.getElementById('document-upload-form');
    const fileNameEl = document.getElementById('selected-file-name');

    if (!uploadForm) return;

    // 파일 크기 체크
    if (file.size > MAX_FILE_SIZE) {
        showToast(FILE_UPLOAD_MESSAGES.SIZE_EXCEEDED, 'error');
        return;
    }

    // 허용된 파일 형식 체크
    const allowedTypes = [
        'application/pdf',
        'image/jpeg',
        'image/png',
        'application/msword',
        'application/vnd.openxmlformats-officedocument.wordprocessingml.document',
        'application/vnd.ms-excel',
        'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    ];

    if (!allowedTypes.includes(file.type)) {
        showToast('허용되지 않은 파일 형식입니다', 'error');
        return;
    }

    // 파일 정보 저장
    uploadForm.dataset.selectedFile = file.name;
    uploadForm._selectedFile = file;

    // 파일명 표시
    if (fileNameEl) {
        fileNameEl.textContent = file.name;
    }

    // 폼 표시
    uploadForm.classList.remove('d-none');
}

/**
 * 문서 업로드 처리
 * @param {Event} e - submit 이벤트
 */
async function handleDocumentUpload(e) {
    e.preventDefault();

    const form = e.target;
    const file = form._selectedFile;

    if (!file) {
        showToast('파일을 선택해주세요', 'warning');
        return;
    }

    const title = form.querySelector('[name="title"]')?.value.trim();
    if (!title) {
        showToast('서류명을 입력해주세요', 'warning');
        return;
    }

    const category = form.querySelector('[name="category"]')?.value;
    const documentType = form.querySelector('[name="documentType"]')?.value;
    const description = form.querySelector('[name="description"]')?.value?.trim() || '';
    const expiresAt = form.querySelector('[name="expiresAt"]')?.value || '';
    const isRequired = form.querySelector('[name="isRequired"]')?.checked || false;

    try {
        // FormData로 파일과 메타데이터 함께 전송
        const formData = new FormData();
        formData.append('file', file);
        formData.append('title', title);
        formData.append('category', category);
        formData.append('documentType', documentType);
        formData.append('description', description);
        formData.append('expiresAt', expiresAt);
        formData.append('isRequired', isRequired);

        await DocumentsApi.upload(formData);

        showToast('서류가 등록되었습니다', 'success');

        // 폼 리셋
        form.classList.add('d-none');
        form.reset();
        form._selectedFile = null;
        document.getElementById('selected-file-name').textContent = '';

        // 리스트 갱신
        await loadDocumentsData();

    } catch (error) {
        showToast(error.message || '서류 등록에 실패했습니다', 'error');
    }
}

/**
 * 카테고리별 서류 유형 옵션 업데이트
 * @param {Event} e - change 이벤트
 */
function updateDocumentTypeOptions(e) {
    const category = e.target.value;
    const typeSelect = document.querySelector('#document-upload-form [name="documentType"]');

    if (!typeSelect) return;

    const typeOptions = {
        required: ['business_registration', 'corporate_seal', 'certificate_of_incorporation'],
        payroll: ['salary_regulations', 'tax_withholding', 'insurance_certificate'],
        welfare: ['welfare_policy', 'insurance_policy', 'retirement_plan'],
        benefits: ['welfare_policy', 'insurance_policy', 'retirement_plan'],
        security: ['security_policy', 'privacy_policy', 'access_control'],
        contract: ['employment_contract', 'nda', 'service_agreement'],
        other: ['other']
    };

    const typeLabels = {
        business_registration: '사업자등록증',
        corporate_seal: '법인인감증명',
        certificate_of_incorporation: '법인등기부등본',
        salary_regulations: '급여규정',
        tax_withholding: '원천징수영수증',
        insurance_certificate: '4대보험 가입증명',
        welfare_policy: '복리후생규정',
        insurance_policy: '단체보험증권',
        retirement_plan: '퇴직연금규약',
        security_policy: '보안정책',
        privacy_policy: '개인정보처리방침',
        access_control: '출입관리규정',
        employment_contract: '근로계약서',
        nda: '비밀유지계약서',
        service_agreement: '용역계약서',
        other: '기타'
    };

    const options = typeOptions[category] || ['other'];
    typeSelect.innerHTML = options.map(opt =>
        `<option value="${opt}">${typeLabels[opt] || opt}</option>`
    ).join('');
}

/**
 * 문서 액션 핸들러
 * @param {Event} e - 클릭 이벤트
 */
async function handleDocumentAction(e) {
    const btn = e.target.closest('[data-action]');
    if (!btn) return;

    const action = btn.dataset.action;
    const item = btn.closest('.document-item');
    const documentId = item?.dataset.id;

    switch (action) {
        case 'download':
            handleDocumentDownload(documentId);
            break;
        case 'edit':
            handleDocumentEdit(documentId);
            break;
        case 'delete':
            await handleDocumentDelete(documentId);
            break;
    }
}

/**
 * 문서 다운로드
 * @param {number} documentId - 문서 ID
 */
function handleDocumentDownload(documentId) {
    if (!documentId) {
        showToast('문서 ID가 없습니다', 'warning');
        return;
    }
    DocumentsApi.download(documentId);
}

/**
 * 문서 수정
 * @param {number} documentId - 문서 ID
 */
function handleDocumentEdit(documentId) {
    // TODO: 수정 모달 또는 인라인 편집 구현
    showToast('수정 기능은 준비 중입니다', 'info');
}

/**
 * 문서 삭제
 * @param {number} documentId - 문서 ID
 */
async function handleDocumentDelete(documentId) {
    if (!confirm('정말 삭제하시겠습니까?')) return;

    try {
        await DocumentsApi.delete(documentId);
        showToast('서류가 삭제되었습니다', 'success');
        await loadDocumentsData();
    } catch (error) {
        showToast(error.message || '삭제에 실패했습니다', 'error');
    }
}

/**
 * 노출 설정 핸들러 초기화
 */
function initVisibilityHandlers() {
    // 저장 버튼
    const saveBtn = document.getElementById('save-visibility');
    if (saveBtn) {
        saveBtn.addEventListener('click', async () => {
            try {
                const settings = {
                    salaryVisibility: document.getElementById('salary_visibility')?.checked,
                    showSalaryToManagers: document.getElementById('show_salary_to_managers')?.checked,
                    evaluationVisibility: document.getElementById('evaluation_visibility')?.checked,
                    showEvaluationToManagers: document.getElementById('show_evaluation_to_managers')?.checked,
                    orgChartVisibility: document.getElementById('org_chart_visibility')?.checked,
                    contactVisibility: document.getElementById('contact_visibility')?.checked,
                    documentVisibility: document.getElementById('document_visibility')?.checked
                };

                await VisibilityApi.save(settings);
                showToast('노출 설정이 저장되었습니다', 'success');
            } catch (error) {
                showToast(error.message || '저장에 실패했습니다', 'error');
            }
        });
    }

    // 초기화 버튼
    const resetBtn = document.getElementById('reset-visibility');
    if (resetBtn) {
        resetBtn.addEventListener('click', async () => {
            if (!confirm('모든 노출 설정을 기본값으로 초기화하시겠습니까?')) return;

            try {
                const data = await VisibilityApi.reset();
                applyVisibilityToForm(data);
                showToast('기본값으로 초기화되었습니다', 'success');
            } catch (error) {
                showToast(error.message || '초기화에 실패했습니다', 'error');
            }
        });
    }
}

// ========================================
// 감사 로그 탭 관련 함수
// ========================================

/**
 * 감사 로그 데이터 로드
 */
async function loadAuditData() {
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
    const { filters, currentPage, perPage } = state.audit;
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
            state.audit.total = result.data.total || 0;
            renderAuditLogs(result.data.logs || []);
            renderAuditPagination();

            // 결과 건수 업데이트
            const countEl = document.querySelector('#tab-audit .audit-log-count');
            if (countEl) {
                countEl.textContent = `${state.audit.total}건`;
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

    const { total, currentPage, perPage } = state.audit;
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
    state.audit.filters = {
        action: '',
        resourceType: '',
        status: '',
        startDate: '',
        endDate: ''
    };
    state.audit.currentPage = 1;

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
    state.audit.filters = {
        action: document.getElementById('auditFilterAction')?.value || '',
        resourceType: document.getElementById('auditFilterResource')?.value || '',
        status: document.getElementById('auditFilterStatus')?.value || '',
        startDate: document.getElementById('auditFilterStartDate')?.value || '',
        endDate: document.getElementById('auditFilterEndDate')?.value || ''
    };
    state.audit.currentPage = 1;

    loadAuditLogs();
}

/**
 * 감사 탭 이벤트 핸들러 초기화
 */
function initAuditHandlers() {
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
                if (page && page !== state.audit.currentPage) {
                    state.audit.currentPage = page;
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

function showToast(message, type = 'info') {
    if (typeof window.showToast === 'function') {
        window.showToast(message, type);
        return;
    }

    const toast = document.createElement('div');
    toast.className = `toast toast-${type}`;
    toast.style.cssText = `
        position: fixed;
        bottom: 20px;
        right: 20px;
        padding: 12px 24px;
        border-radius: 8px;
        color: white;
        font-size: 14px;
        z-index: 10000;
        animation: slideIn 0.3s ease;
        background: ${TOAST_COLORS[type] || TOAST_COLORS.info};
    `;
    toast.textContent = message;
    document.body.appendChild(toast);

    setTimeout(() => {
        toast.style.animation = 'slideOut 0.3s ease';
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * HTML 이스케이프
 * @param {string} str - 문자열
 * @returns {string} 이스케이프된 문자열
 */
function escapeHtml(str) {
    const div = document.createElement('div');
    div.textContent = str;
    return div.innerHTML;
}

/**
 * 아코디언 초기화
 */
function initAccordions() {
    // data-accordion 속성이 있는 모든 컨테이너에 아코디언 적용
    document.querySelectorAll('[data-accordion]').forEach(container => {
        new Accordion(container);
    });
}

/**
 * 페이지 초기화
 */
function init() {
    initTabs();
    initAccordions();
    initCategoryHandlers();
    initPatternsHandlers();
    initDocumentsHandlers();
    initVisibilityHandlers();
    initAuditHandlers();
}

// DOM 로드 후 초기화
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
} else {
    init();
}

// 토스트 애니메이션 스타일 추가
const style = document.createElement('style');
style.textContent = `
    @keyframes slideIn {
        from { transform: translateX(100%); opacity: 0; }
        to { transform: translateX(0); opacity: 1; }
    }
    @keyframes slideOut {
        from { transform: translateX(0); opacity: 1; }
        to { transform: translateX(100%); opacity: 0; }
    }
`;
document.head.appendChild(style);
