/**
 * 조직 관리 모듈
 *
 * 법인 설정 페이지의 조직 관리 탭 기능
 * - 조직 CRUD (추가, 수정, 삭제)
 * - 조직 상세 정보 표시
 * - 조직 통계
 *
 * 트리 관련 기능은 components/org-tree.js에서 처리
 */

import { showToast } from '../../../../../shared/components/toast.js';
import {
    renderOrgTree,
    toggleTreeNode,
    toggleTreeExpand,
    updateParentOrgOptions,
    setTreeCallbacks
} from '../components/org-tree.js';
import {
    renderOrgTypeSettings,
    saveOrgTypeLabel,
    deleteOrgType,
    addOrgType,
    showIconSelector,
    resetOrgTypes,
    initOrgTypeSortable
} from './org-type-settings.js';

// 모듈 상태
let selectedOrgId = null;
let deleteOrgId = null;

// 콜백 함수 (settings.js에서 설정)
let onDataReloadCallback = null;

/**
 * 데이터 리로드 콜백 설정
 * @param {Function} callback - 리로드 콜백 함수
 */
export function setDataReloadCallback(callback) {
    onDataReloadCallback = callback;
    // 트리 컴포넌트에도 콜백 전달
    setTreeCallbacks({
        onDataReload: callback
    });
}

/**
 * 조직 관리 탭 데이터 로드
 */
export async function loadOrgManagementData() {
    const content = document.getElementById('org-management-content');

    try {
        const [treeResponse, statsResponse, typesResponse] = await Promise.all([
            fetch('/admin/api/organizations?format=tree'),
            fetch('/admin/api/organizations/stats'),
            fetch('/api/corporate/organization-types')
        ]);

        const treeResult = await treeResponse.json();
        const statsResult = await statsResponse.json();
        const typesResult = await typesResponse.json();

        if (typesResult.success) {
            renderOrgTypeSettings(typesResult.data);
        }

        if (statsResult.success) {
            updateOrgStats(statsResult.data);
        }

        if (treeResult.success) {
            renderOrgTree(treeResult.data);
            await updateParentOrgOptions();
        }

        initOrgManagementHandlers();
    } catch (error) {
        console.error('조직 관리 데이터 로드 실패:', error);
        showContentError(content);
    }
}

/**
 * 콘텐츠 영역에 에러 메시지 표시
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

/**
 * HTML 이스케이프 (SSOT: window.HRFormatters.escapeHtml)
 */
function escapeHtml(str) {
    return window.HRFormatters?.escapeHtml?.(str) || '';
}

/**
 * 조직 통계 업데이트
 */
function updateOrgStats(stats) {
    const container = document.getElementById('org-stats-row');
    if (!container) return;

    const totalEl = document.getElementById('stat-total');
    if (totalEl) {
        totalEl.textContent = stats.total || 0;
    }

    const dynamicCards = container.querySelectorAll('.stat-card.dynamic');
    dynamicCards.forEach(card => card.remove());

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

/**
 * 조직 선택
 */
async function selectOrganization(orgId) {
    selectedOrgId = orgId;

    document.querySelectorAll('.tree-node-content.selected').forEach(el => {
        el.classList.remove('selected');
    });

    const node = document.querySelector(`.tree-node[data-id="${orgId}"] > .tree-node-content`);
    if (node) {
        node.classList.add('selected');
    }

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

    const memberCountHtml = org.total_member_count !== undefined
        ? `<div class="info-row">
               <span class="info-label">소속인원</span>
               <span class="info-value">${org.total_member_count}명${org.direct_member_count !== undefined && org.direct_member_count !== org.total_member_count ? ` (직접: ${org.direct_member_count}명)` : ''}</span>
           </div>`
        : '';

    const deptPhoneHtml = org.department_phone
        ? `<div class="info-row">
               <span class="info-label">대표 내선번호</span>
               <span class="info-value">${escapeHtml(org.department_phone)}</span>
           </div>`
        : '';

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

            const defaultOption = select.querySelector('option[value="team"]') ||
                                  select.querySelector('option[value="department"]') ||
                                  select.querySelector('option');
            if (defaultOption) {
                defaultOption.selected = true;
            }
        }
    } catch (error) {
        console.error('조직유형 옵션 로드 실패:', error);
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
            if (onDataReloadCallback) {
                await onDataReloadCallback();
            }
        } else {
            showToast(result.error || '저장에 실패했습니다', 'error');
        }
    } catch (error) {
        console.error('조직 저장 오류:', error);
        showToast('저장 중 오류가 발생했습니다', 'error');
    }
}

/**
 * 조직유형 설정 모달 열기
 */
function toggleOrgTypeSettings() {
    const modal = document.getElementById('orgTypeModal');
    if (!modal) return;

    modal.classList.add('show');

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
            if (onDataReloadCallback) {
                await onDataReloadCallback();
            }
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
export function initOrgManagementHandlers() {
    const container = document.getElementById('tab-org-management');
    if (!container || container.dataset.handlersInitialized) return;

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
                resetOrgTypes(async () => {
                    if (onDataReloadCallback) {
                        await onDataReloadCallback();
                    }
                });
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

    // 조직유형 모달 이벤트 핸들러
    const orgTypeModal = document.getElementById('orgTypeModal');
    if (orgTypeModal && !orgTypeModal.dataset.handlersInitialized) {
        orgTypeModal.addEventListener('click', function(e) {
            const target = e.target.closest('[data-action]');
            if (!target) {
                if (e.target === orgTypeModal) {
                    closeOrgTypeModal();
                }
                return;
            }
            handleAction(target.dataset.action, target);
        });

        orgTypeModal.addEventListener('blur', function(e) {
            const input = e.target.closest('.org-type-label-input');
            if (input && input.value !== input.dataset.original) {
                const field = input.dataset.field || 'type_label_ko';
                saveOrgTypeLabel(parseInt(input.dataset.id), field, input.value.trim());
            }
        }, true);

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

    // 조직유형 라벨 입력 이벤트
    container.addEventListener('blur', function(e) {
        const input = e.target.closest('.org-type-label-input');
        if (input && input.value !== input.dataset.original) {
            const field = input.dataset.field || 'type_label_ko';
            saveOrgTypeLabel(parseInt(input.dataset.id), field, input.value.trim());
        }
    }, true);

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

/**
 * 조직 관리 탭 초기화 엔트리 포인트
 */
export async function initOrgManagementTab() {
    await loadOrgManagementData();
}
