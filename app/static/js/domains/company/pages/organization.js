/**
 * organization.js - 조직 관리 페이지 스크립트
 *
 * 포함 기능:
 * - 조직 트리 토글/펼치기/접기
 * - 조직 선택 및 상세 정보 표시
 * - 조직 추가/수정/삭제 모달
 * - 이벤트 위임 처리
 */

let selectedOrgId = null;
let deleteOrgId = null;
let treeExpanded = false;
let draggedNode = null;
let draggedOrgId = null;

/**
 * 트리 노드 토글
 */
function toggleNode(el) {
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
function expandAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('.tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });
}

/**
 * 전체 접기
 */
function collapseAll() {
    document.querySelectorAll('.tree-children').forEach(el => {
        el.classList.add('collapsed');
    });
    document.querySelectorAll('.tree-toggle i').forEach(el => {
        el.classList.add('fa-chevron-right');
        el.classList.remove('fa-chevron-down');
    });
}

/**
 * 트리 펼치기/접기 토글
 */
function toggleTreeExpand() {
    if (treeExpanded) {
        collapseAll();
        updateToggleButton(false);
    } else {
        expandAll();
        updateToggleButton(true);
    }
    treeExpanded = !treeExpanded;
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
        console.error('Error loading organization:', error);
    }
}

/**
 * 조직 상세 정보 렌더링
 */
function renderOrgDetail(org) {
    const panel = document.getElementById('orgDetailPanel');
    const typeLabels = {
        'company': '회사',
        'division': '본부',
        'department': '부서',
        'team': '팀',
        'unit': '파트'
    };

    panel.querySelector('.panel-body').innerHTML = `
        <div class="org-detail">
            <div class="detail-header">
                <h4>${org.name}</h4>
                <span class="org-type-badge ${org.org_type}">${typeLabels[org.org_type] || org.org_type}</span>
            </div>

            <div class="detail-info">
                <div class="info-row">
                    <span class="info-label">조직 코드</span>
                    <span class="info-value">${org.code || '-'}</span>
                </div>
                <div class="info-row">
                    <span class="info-label">조직 경로</span>
                    <span class="info-value">${org.path || org.name}</span>
                </div>
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
                <button class="btn btn-danger" data-action="delete-org" data-org-id="${org.id}" data-org-name="${org.name}">
                    <i class="fas fa-trash"></i> 삭제
                </button>
            </div>
        </div>
    `;
}

/**
 * 조직 추가 모달 표시
 */
function showAddOrgModal() {
    document.getElementById('orgModalTitle').textContent = '조직 추가';
    document.getElementById('orgForm').reset();
    document.getElementById('orgId').value = '';
    document.getElementById('orgModal').classList.add('show');
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
            // 조직장 및 내선번호 필드
            document.getElementById('orgManager').value = org.manager_id || '';
            document.getElementById('leaderPhone').value = org.leader_phone || '';
            document.getElementById('deptPhone').value = org.department_phone || '';
            document.getElementById('orgModal').classList.add('show');
        }
    } catch (error) {
        console.error('Error loading organization:', error);
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
        // 조직장 및 내선번호 필드
        manager_id: managerIdValue ? parseInt(managerIdValue, 10) : null,
        leader_phone: document.getElementById('leaderPhone').value || null,
        department_phone: document.getElementById('deptPhone').value || null
    };

    // CSRF 토큰 가져오기
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
            location.reload();
        } else {
            alert(result.error || '저장에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error saving organization:', error);
        alert('저장 중 오류가 발생했습니다.');
    }
}

/**
 * 모달 닫기
 */
function closeOrgModal() {
    document.getElementById('orgModal').classList.remove('show');
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
    document.getElementById('deleteModal').classList.remove('show');
    deleteOrgId = null;
}

/**
 * 삭제 확인
 */
async function confirmDelete() {
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
            location.reload();
        } else {
            alert(result.error || '삭제에 실패했습니다.');
        }
    } catch (error) {
        console.error('Error deleting organization:', error);
        alert('삭제 중 오류가 발생했습니다.');
    }
}

/**
 * 노드가 다른 노드의 자손인지 확인
 * @param {Element} parent - 부모 노드
 * @param {Element} child - 자식 노드
 * @returns {boolean} 자손 여부
 */
function isDescendant(parent, child) {
    let node = child.parentElement;
    while (node) {
        if (node === parent) return true;
        node = node.parentElement;
    }
    return false;
}

/**
 * 드래그앤드롭 초기화
 */
function initTreeDragDrop() {
    const treeContainer = document.querySelector('.org-tree');
    if (!treeContainer) return;

    // 드래그 시작
    treeContainer.addEventListener('dragstart', (e) => {
        const node = e.target.closest('.tree-node');
        if (!node || node.dataset.type === 'company') {
            e.preventDefault();
            return;
        }

        draggedNode = node;
        draggedOrgId = node.dataset.id;
        node.classList.add('dragging');
        e.dataTransfer.effectAllowed = 'move';
        e.dataTransfer.setData('text/plain', draggedOrgId);
    });

    // 드래그 오버
    treeContainer.addEventListener('dragover', (e) => {
        e.preventDefault();
        const nodeContent = e.target.closest('.tree-node-content');
        if (!nodeContent) return;

        const targetNode = nodeContent.closest('.tree-node');
        if (!targetNode || targetNode === draggedNode) return;

        // 자손으로 이동 방지 (순환 참조)
        if (isDescendant(draggedNode, targetNode)) {
            e.dataTransfer.dropEffect = 'none';
            return;
        }

        e.dataTransfer.dropEffect = 'move';

        // 기존 드롭 표시 제거
        treeContainer.querySelectorAll('.drag-over').forEach(el => {
            el.classList.remove('drag-over');
        });

        // 새 드롭 표시
        nodeContent.classList.add('drag-over');
    });

    // 드래그 리브
    treeContainer.addEventListener('dragleave', (e) => {
        const nodeContent = e.target.closest('.tree-node-content');
        if (nodeContent) {
            nodeContent.classList.remove('drag-over');
        }
    });

    // 드롭
    treeContainer.addEventListener('drop', async (e) => {
        e.preventDefault();
        const nodeContent = e.target.closest('.tree-node-content');
        if (!nodeContent || !draggedOrgId) return;

        const targetNode = nodeContent.closest('.tree-node');
        const targetOrgId = targetNode.dataset.id;

        // 자기 자신으로 이동 방지
        if (draggedOrgId === targetOrgId) {
            cleanupDragState();
            return;
        }

        // 순환 참조 검증
        if (isDescendant(draggedNode, targetNode)) {
            showToast('하위 조직으로 이동할 수 없습니다.', 'error');
            cleanupDragState();
            return;
        }

        // API 호출
        const csrfToken = document.querySelector('meta[name="csrf-token"]')?.content;
        try {
            const response = await fetch(`/admin/api/organizations/${draggedOrgId}/move`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': csrfToken
                },
                body: JSON.stringify({ new_parent_id: parseInt(targetOrgId, 10) })
            });

            const result = await response.json();
            if (result.success) {
                showToast('조직이 이동되었습니다.', 'success');
                location.reload();
            } else {
                showToast(result.error || '이동에 실패했습니다.', 'error');
            }
        } catch (error) {
            console.error('조직 이동 오류:', error);
            showToast('이동 중 오류가 발생했습니다.', 'error');
        }

        cleanupDragState();
    });

    // 드래그 종료
    treeContainer.addEventListener('dragend', () => {
        cleanupDragState();
    });
}

/**
 * 드래그 상태 정리
 */
function cleanupDragState() {
    if (draggedNode) {
        draggedNode.classList.remove('dragging');
    }
    document.querySelectorAll('.drag-over').forEach(el => {
        el.classList.remove('drag-over');
    });
    draggedNode = null;
    draggedOrgId = null;
}

/**
 * 토스트 메시지 표시
 */
function showToast(message, type = 'info') {
    // 기존 토스트 컨테이너 사용 또는 생성
    let container = document.querySelector('.toast-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'toast-container';
        document.body.appendChild(container);
    }

    const toast = document.createElement('div');
    toast.className = `toast toast--${type}`;
    toast.innerHTML = `
        <i class="fas ${type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-exclamation-circle' : 'fa-info-circle'}"></i>
        <span>${message}</span>
    `;
    container.appendChild(toast);

    // 애니메이션 후 제거
    setTimeout(() => {
        toast.classList.add('toast--fade-out');
        setTimeout(() => toast.remove(), 300);
    }, 3000);
}

/**
 * 페이지 초기화
 */
function initOrganizationPage() {
    // 첫 번째 레벨 펼치기
    document.querySelectorAll('.tree-node[data-type="company"] > .tree-children').forEach(el => {
        el.classList.remove('collapsed');
    });
    document.querySelectorAll('.tree-node[data-type="company"] > .tree-node-content .tree-toggle i').forEach(el => {
        el.classList.remove('fa-chevron-right');
        el.classList.add('fa-chevron-down');
    });

    // 드래그앤드롭 초기화
    initTreeDragDrop();

    // 이벤트 위임 - 클릭 이벤트
    document.addEventListener('click', function(e) {
        const target = e.target.closest('[data-action]');
        if (!target) return;

        const action = target.dataset.action;

        switch (action) {
            case 'toggle-node':
                e.stopPropagation();
                toggleNode(target);
                break;
            case 'select-org':
                selectOrganization(parseInt(target.dataset.orgId));
                break;
            case 'add-org':
                showAddOrgModal();
                break;
            case 'toggle-tree':
                toggleTreeExpand();
                break;
            case 'close-org-modal':
                closeOrgModal();
                break;
            case 'close-delete-modal':
                closeDeleteModal();
                break;
            case 'confirm-delete':
                confirmDelete();
                break;
            case 'edit-org':
                showEditOrgModal(parseInt(target.dataset.orgId));
                break;
            case 'add-child':
                showAddChildModal(parseInt(target.dataset.parentId));
                break;
            case 'delete-org':
                showDeleteModal(parseInt(target.dataset.orgId), target.dataset.orgName);
                break;
        }
    });

    // 이벤트 위임 - 폼 제출
    document.addEventListener('submit', function(e) {
        const target = e.target.closest('[data-action="save-org"]');
        if (target) {
            e.preventDefault();
            saveOrganization(e);
        }
    });
}

// 페이지 로드 시 초기화
document.addEventListener('DOMContentLoaded', initOrganizationPage);
